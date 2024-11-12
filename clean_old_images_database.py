import os
import django

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photos.settings')  # Adjust 'mikypics' to your project name

# Initialize Django
django.setup()

from django.conf import settings
from mikypics.models import Photo

# Path to the media/images directory
image_dir = os.path.join(settings.MEDIA_ROOT, 'images')

# Loop through the database entries and check if the file exists
for photo in Photo.objects.all():
    image_path = os.path.join(settings.MEDIA_ROOT, photo.image.name)

    # If the file does not exist, delete the database entry
    if not os.path.exists(image_path):
        print(f'Deleting {photo.image.name} from the database as it no longer exists on the file system.')
        photo.delete()

print('Database cleaned up successfully.')

