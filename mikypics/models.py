from django.db import models
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPSTAGS
import io
from django.core.files.base import ContentFile
from pathlib import Path
from datetime import datetime

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50)
    photo = models.ForeignKey('Photo', related_name='tags', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='tags', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

class Photo(models.Model):
    image = models.ImageField(upload_to='images/')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    date_taken = models.DateTimeField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.extract_exif_data()
        if not self.thumbnail:  # Only create a thumbnail if one doesn't exist
            self.create_thumbnail()
        super().save(*args, **kwargs)

    def extract_exif_data(self):
        img = Image.open(self.image)
        exif_data = img._getexif()

        if exif_data:
            for tag, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag, tag)

                # Extract Date Taken and convert to the proper format
                if tag_name == "DateTimeOriginal":
                    try:
                        # Convert from 'YYYY:MM:DD HH:MM:SS' to 'YYYY-MM-DD HH:MM:SS'
                        self.date_taken = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                    except ValueError:
                        self.date_taken = None  # Handle any errors during conversion

                # Extract GPS Info
                if tag_name == "GPSInfo":
                    gps_info = {}
                    for key in value.keys():
                        decode = ExifTags.GPSTAGS.get(key, key)
                        gps_info[decode] = value[key]

                    self.latitude, self.longitude = self._get_lat_lng(gps_info)

    def _get_lat_lng(self, gps_info):
        def convert_to_degrees(value):
            d, m, s = value
            return d + (m / 60.0) + (s / 3600.0)

        if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
            lat = convert_to_degrees(gps_info['GPSLatitude'])
            lon = convert_to_degrees(gps_info['GPSLongitude'])
            if gps_info.get('GPSLatitudeRef') == 'S':
                lat = -lat
            if gps_info.get('GPSLongitudeRef') == 'W':
                lon = -lon
            return lat, lon
        return None, None

    def create_thumbnail(self):
        img = Image.open(self.image)

        # Automatically rotate the image based on EXIF orientation
        img = self.correct_orientation(img)

        img.thumbnail((200, 200))  # Define the size of the thumbnail

        thumb_io = io.BytesIO()
        img.save(thumb_io, format='JPEG')

        thumb_name = f"thumb_{Path(self.image.name).stem}.jpg"
        self.thumbnail.save(thumb_name, ContentFile(thumb_io.getvalue()), save=False)

    def correct_orientation(self, img):
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break

            exif = img._getexif()

            if exif is not None:
                orientation = exif.get(orientation)

                if orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 6:
                    img = img.rotate(-90, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            # In case the image does not have EXIF data or other issues occur
            pass

        return img

    @property
    def thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        return self.image.url
