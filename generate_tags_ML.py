import os
import django
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import preprocess_input, decode_predictions
import numpy as np

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photos.settings')  # Adjust 'photos' to your actual project settings
django.setup()

from mikypics.models import Tag, Category

# Load pre-trained model
model = InceptionV3(weights='imagenet')

# Directory containing the images you want to process
image_dir = 'media/images/'  # Adjust this path to your actual image folder


def generate_tags_from_folder(image_path):
    print(f"Processing {image_path}")

    try:
        # Load and preprocess the image
        img = image.load_img(image_path, target_size=(299, 299))  # Load image from file
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        # Predict using the pre-trained model
        predictions = model.predict(img_array)
        decoded_predictions = decode_predictions(predictions, top=10)[0]  # Get top 10 predictions

        confidence_threshold = 0.1  # Adjust this threshold for stricter filtering
        # Print the tags
        print("Generated Tags:")
        for _, label, confidence in decoded_predictions:
            if confidence >= confidence_threshold:
                print(f"- {label}")

            # Save the tag to the database (optional)
                category, _ = Category.objects.get_or_create(name=label)
            # Here, you can link this tag to a photo model in the database if needed

    except Exception as e:
        print(f"Error processing {image_path}: {e}")


# Loop through all files in the directory and process each image
for filename in os.listdir(image_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        full_image_path = os.path.join(image_dir, filename)
        generate_tags_from_folder(full_image_path)


