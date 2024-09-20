from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import preprocess_input, decode_predictions
import numpy as np

# Load pre-trained model
model = InceptionV3(weights='imagenet')

def generate_tags(photo):
    img = image.load_img(photo.image.path, target_size=(299, 299))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    predictions = model.predict(img_array)
    decoded_predictions = decode_predictions(predictions, top=10)[0]  # Get top 10 predictions

    for i, (_, label, _) in enumerate(decoded_predictions):
        category, _ = Category.objects.get_or_create(name=label)
        Tag.objects.create(name=label, photo=photo, category=category)
