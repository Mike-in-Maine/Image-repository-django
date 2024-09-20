# To insert more pictures in the database:
# python manage.py shell
# exec(open('populate_images.py').read())



import os
from django.conf import settings
from mikypics.models import Photo  # Assuming you have a Photo model in mikypics app

# Path to the media/images directory
image_dir = os.path.join(settings.MEDIA_ROOT, 'images')

# Loop through files in the image directory
for filename in os.listdir(image_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        image_path = os.path.join('images', filename)  # Relative path for the model

        # Check if the image is already in the database
        if not Photo.objects.filter(image=image_path).exists():
            # Create a new Photo object and save it to the database
            new_photo = Photo(image=image_path)
            new_photo.save()

        print(f'Inserted {filename} into the database.')
