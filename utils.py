import pytesseract
from PIL import Image
import numpy as np
from keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from keras.preprocessing import image
from keras.models import load_model

import os

# Load your trained model
model = load_model("car_damage_classifier.h5")
class_labels = sorted(os.listdir("car_damage_dataset"))  # e.g., ['broken_headlight', ...]

def predict_damage_type(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = x / 255.0  # Rescale like training

    preds = model.predict(x)
    predicted_class = class_labels[np.argmax(preds)]
    confidence = float(np.max(preds))

    return {"predicted_damage": predicted_class, "confidence": confidence}
# Optional: Set Tesseract path if needed (Windows only)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(img):
    return pytesseract.image_to_string(img)

def predict_damage_type(img_path):
    try:
        model = MobileNetV2(weights='imagenet')
        img = image.load_img(img_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        preds = model.predict(x)
        decoded = decode_predictions(preds, top=3)[0]

    except Exception as e:
        return [{"error": str(e)}]
def predict_damage_type(img_path):
    if model is None:
        print("❌ Model not loaded")
        return {"error": "Model not trained or missing"}

    try:
        img = image.load_img(img_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = x / 255.0  # Rescale like training

        preds = model.predict(x)
        predicted_class = class_labels[np.argmax(preds)]
        confidence = float(np.max(preds))

        print("✅ Prediction successful:")
        print(f"Predicted Class: {predicted_class}, Confidence: {confidence:.2%}")

        return {"predicted_damage": predicted_class, "confidence": confidence}

    except Exception as e:
        print("❌ Prediction error:", str(e))
        return {"error": str(e)}