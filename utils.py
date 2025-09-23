import pytesseract
from PIL import Image
import numpy as np
from keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from keras.preprocessing import image
from keras.models import load_model
import tensorflow as tf
from keras.preprocessing import image
import numpy as np
import json
import os
from datetime import datetime
import shutil
import sqlite3


#Load your trained model
#model = load_model("car_damage_classifier.h5")

#custom_objects = {"custom_activation": custom_activation}
custom_objects = {}  # update if you had custom layers/activations

try:
    model = load_model(
        "car_damage_classifier.h5",
        custom_objects=custom_objects,
        compile=False  # 👈 prevents optimizer/state issues
    )
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None
    
class_labels = sorted(os.listdir("car_damage_dataset"))  # e.g., ['broken_headlight', ...]

def prepare_image(img_path, target_size=(224, 224)):
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0  # normalize
    return img_array
    predicted_class = class_labels[np.argmax(preds)]
    confidence = float(np.max(preds))

    return {"predicted_damage": predicted_class, "confidence": confidence}
# Optional: Set Tesseract path if needed (Windows only)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(img):
    return pytesseract.image_to_string(img)

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

def generate_claim_reference(branch_name):
    """
    Generate: CLN/Branch/Seq/Year → e.g. CLN/MUMBAI/0005/2025
    """
    year = datetime.now().year
    config_dir = "claim_config"
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, f"{branch_name}.json")

    # Load existing sequence
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        last_seq = config.get("last_sequence", 0)
        last_year = config.get("year", year)

        if last_year != year:
            seq = 1  # Reset on new year
        else:
            seq = last_seq + 1
    else:
        seq = 1
        config = {
            "branch": branch_name,
            "year": year,
            "last_sequence": 0
        }

    # Format claim number
    claim_ref = f"CLN/{branch_name}/{seq:04d}/{year}"

    # Update config
    config["last_sequence"] = seq
    config["year"] = year
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

    return claim_ref

def save_claim_with_image(name, policy_number, plate_number, location, branch, uploaded_image, date_of_accident):
    """
    Saves claim data and image in structured folder + updates SQLite
    Returns claim_ref
    """
    # Generate claim reference
    claim_ref = generate_claim_reference(branch)

    # Create claim-specific folder
    safe_ref = claim_ref.replace("/", "_")  # For file system
    claim_folder = os.path.join("submissions", safe_ref)
    os.makedirs(claim_folder, exist_ok=True)

    # Save image
    image_filename = f"damage_{safe_ref}.jpg"
    image_path = os.path.join(claim_folder, image_filename)  # ← Fixed!
    
    with open(image_path, "wb") as f:
        shutil.copyfileobj(uploaded_image, f)  # Handle Streamlit UploadedFile

    # Save metadata JSON (optional)
    metadata = {
        "claim_ref": claim_ref,
        "name": name,
        "policy_number": policy_number,
        "plate_number": plate_number,
        "location": location,
        "branch": branch,
        "image_path": image_path,
        "date_of_accident": date_of_accident
    }

    with open(os.path.join(claim_folder, "data.json"), "w") as f:
        import json
        json.dump(metadata, f, indent=4)

    # Save to SQLite
    conn = sqlite3.connect("claims.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO claims (
        name, claim_ref, branch, policy_number,
        plate_number, location, image_path, date_of_accident
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", [
    name, claim_ref, branch, policy_number,
    plate_number,
    location, image_path, date_of_accident
])
    conn.commit()
    conn.close()

    return claim_ref