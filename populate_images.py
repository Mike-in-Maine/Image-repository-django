import os
import django
from geopy.geocoders import Nominatim

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photos.settings')  # Adjust 'photos' to your correct project name

# Initialize Django
django.setup()

from django.conf import settings
from mikypics.models import Photo

# Initialize the Nominatim geocoder
geolocator = Nominatim(user_agent="miky-pics-app")

def reverse_geocode(photo):
    """Fetch location name based on latitude and longitude."""
    if photo.latitude and photo.longitude:
        try:
            location = geolocator.reverse((photo.latitude, photo.longitude), exactly_one=True)
            if location:
                return location.address
        except Exception as e:
            print(f"Error in reverse geocoding for photo {photo.id}: {e}")
    return None

# Path to the media/images and thumbnails directories
image_dir = os.path.join(settings.MEDIA_ROOT, 'images')
thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')

# Loop through files in the image directory
for filename in os.listdir(image_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        image_path = os.path.join('images', filename)  # Relative path for the model

        # Check if the image already exists in the database
        photo = Photo.objects.filter(image=image_path).first()

        if photo:
            # Check if the thumbnail exists on the filesystem
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, photo.thumbnail.name) if photo.thumbnail else None
            if not photo.thumbnail or not os.path.exists(thumbnail_path):
                print(f"Thumbnail for {filename} is missing. Regenerating thumbnail...")
                photo.create_thumbnail()  # Regenerate the thumbnail
                photo.save()

            # Check if location name needs to be populated
            if not photo.location_name:
                location_name = reverse_geocode(photo)
                if location_name:
                    photo.location_name = location_name
                    photo.save()
                    print(f"Updated photo {photo.id} with location: {photo.location_name}")
                else:
                    print(f"Could not find location for photo {photo.id}")
            else:
                print(f"Skipped {filename} as both the image, thumbnail, and location exist.")
        else:
            # Create a new Photo object and save it to the database
            new_photo = Photo(image=image_path)
            new_photo.save()

            # Reverse geocode and update location
            location_name = reverse_geocode(new_photo)
            if location_name:
                new_photo.location_name = location_name

            # Create a thumbnail and save it to the database
            new_photo.create_thumbnail()
            new_photo.save()

            print(f"Inserted {filename} into the database with location: {new_photo.location_name}")

