import os
from django.core.management.base import BaseCommand
from mikypics.models import Photo
from django.conf import settings
from PIL import Image
from django.core.files import File

class Command(BaseCommand):
    help = 'Load new images from the media/images/ folder into the database and create thumbnails.'

    def handle(self, *args, **kwargs):
        image_folder = os.path.join(settings.MEDIA_ROOT, 'images')

        # Loop through all files in the images folder
        for image_name in os.listdir(image_folder):
            image_path = os.path.join(image_folder, image_name)

            # Skip directories and only process image files
            if os.path.isdir(image_path):
                continue

            # Check if the image already exists in the database
            if not Photo.objects.filter(image='images/' + image_name).exists():
                # Open the image file
                with open(image_path, 'rb') as f:
                    # Create a new Photo object
                    photo = Photo()
                    photo.image.save(image_name, File(f))
                    photo.save()

                    # Create a thumbnail after saving the image
                    self.create_thumbnail(photo, image_path)

                self.stdout.write(self.style.SUCCESS(f"Successfully loaded {image_name} into the database"))
            else:
                self.stdout.write(f"{image_name} is already in the database.")

    def create_thumbnail(self, photo, image_path):
        """
        Create a thumbnail for the given image and update the photo object.
        """
        # Define the thumbnail size (example: 150x150)
        thumbnail_size = (150, 150)

        # Open the original image
        with Image.open(image_path) as img:
            # Convert image to RGB mode (to avoid errors with some file types like PNG)
            img = img.convert('RGB')

            # Create a thumbnail
            img.thumbnail(thumbnail_size)

            # Generate a thumbnail name
            thumbnail_name = f"thumb_{os.path.basename(image_path)}"

            # Save the thumbnail to the media/thumbnails/ directory
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'thumbnails', thumbnail_name)
            img.save(thumbnail_path)

            # Save the thumbnail file to the photo object (assuming you have a thumbnail field in your model)
            with open(thumbnail_path, 'rb') as thumb_file:
                photo.thumbnail.save(thumbnail_name, File(thumb_file))

            # Save the updated photo object
            photo.save()
