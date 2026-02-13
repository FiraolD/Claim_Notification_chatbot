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
from fpdf import FPDF


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

def save_claim_with_image(
    claim_ref,
    name,
    branch,
    phone_number,
    policy_number,
    plate_number,
    car_model,
    year_of_manufacture,
    date_of_accident,
    time_of_accident,
    type_of_accident,
    fatality,
    fatality_details,
    injuries,
    location,
    legal_authority_contacted,
    police_report_number,
    witnesses,
    description_of_accident,
    uploaded_images,
    ai_response
):
    """
    Saves claim data + all uploaded images separately
    into structured folders and records metadata in SQLite.
    """
    try:
        # --- Create base claim folder
        safe_ref = claim_ref.replace("/", "_")
        claim_folder = os.path.join("submissions", safe_ref)
        os.makedirs(claim_folder, exist_ok=True)

        # --- Create subfolder for images
        image_dir = os.path.join(claim_folder, "images")
        os.makedirs(image_dir, exist_ok=True)

        # --- Save uploaded images
        image_paths = []
        for idx, uploaded_file in enumerate(uploaded_images):
            img_filename = f"image_{idx+1}_{uploaded_file.name}"
            img_path = os.path.join(image_dir, img_filename)
            with open(img_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            image_paths.append(img_path)

        # --- Save claim metadata to JSON
        metadata = {
            "claim_ref": claim_ref,
            "name": name,
            "branch": branch,
            "phone_number": str(phone_number),
            "policy_number": policy_number,
            "plate_number": plate_number,
            "car_model": car_model,
            "year_of_manufacture": str(year_of_manufacture),
            "date_of_accident": str(date_of_accident),
            "time_of_accident": str(time_of_accident),
            "type_of_accident": type_of_accident,
            "fatality": fatality,
            "fatality_details": fatality_details,
            "injuries": injuries,
            "location": location,
            "legal_authority_contacted": legal_authority_contacted,
            "police_report_number": police_report_number,
            "witnesses": witnesses,
            "description_of_accident": description_of_accident,
            "uploaded_images": image_paths,
            "ai_response": ai_response,
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        metadata_path = os.path.join(claim_folder, "claim_data.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=4)

        # --- Save record to SQLite
        conn = sqlite3.connect("claims.db")
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_ref TEXT,
            name TEXT,
            branch TEXT,
            phone_number TEXT,
            policy_number TEXT,
            plate_number TEXT,
            car_model TEXT,
            year_of_manufacture TEXT,
            date_of_accident TEXT,
            time_of_accident TEXT,
            type_of_accident TEXT,
            fatality TEXT,
            fatality_details TEXT,
            injuries TEXT,
            location TEXT,
            legal_authority_contacted TEXT,
            police_report_number TEXT,
            witnesses TEXT,
            description_of_accident TEXT,
            json_path TEXT,
            submitted_on TEXT
        )
        """)
        conn.commit()

        cursor.execute("""
        INSERT INTO claims (
            claim_ref, name, branch, phone_number, policy_number,
            plate_number, car_model, year_of_manufacture, date_of_accident,
            time_of_accident, type_of_accident, fatality, fatality_details,
            injuries, location, legal_authority_contacted, police_report_number,
            witnesses, description_of_accident, json_path, submitted_on
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            claim_ref, name, branch, str(phone_number), policy_number,
            plate_number, car_model, str(year_of_manufacture),
            str(date_of_accident), str(time_of_accident),
            type_of_accident, fatality, fatality_details, injuries,
            location, legal_authority_contacted, police_report_number,
            witnesses, description_of_accident, metadata_path,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        conn.close()

        print(f"✅ Claim {claim_ref} saved successfully with {len(image_paths)} images.")
        return {"status": "ok", "claim_ref": claim_ref, "image_paths": image_paths}

    except Exception as e:
        print(f"❌ Error saving claim: {str(e)}")
        return {"status": "error", "message": str(e)}



def generate_claim_pdf(claim_data, logo_path=None):
    """
    Generate a well-formatted PDF receipt for a submitted claim,
    ensuring all content fits properly (no cut-off).
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title Section
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(0, 51, 153)
    pdf.cell(0, 12, "Awash Insurance - Claim Receipt", ln=True, align="C")
    pdf.ln(5)

    # Logo (top-right)
    if logo_path and os.path.exists(logo_path):
        pdf.image(logo_path, x=160, y=10, w=33)

    # Motto
    pdf.set_font("Arial", "I", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, '"Your Safety, Our Commitment"', ln=True, align="C")
    pdf.ln(8)

    # Claim Info Section
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Claim Information", ln=True)
    pdf.ln(3)

    # Table layout for claim fields
    pdf.set_font("Arial", "", 12)
    pdf.set_fill_color(245, 245, 245)

    fields = [
        ("Claim Reference", claim_data.get("claim_ref")),
        ("Full Name", claim_data.get("name")),
        ("Policy Number", claim_data.get("policy_number")),
        ("Plate Number", claim_data.get("plate_number")),
        ("Car Model", claim_data.get("car_model")),
        ("Branch", claim_data.get("branch")),
        ("Date of Accident", claim_data.get("date_of_accident")),
        ("Time of Accident", claim_data.get("time_of_accident")),
        ("Location", claim_data.get("location")),
        ("Type of Accident", claim_data.get("type_of_accident")),
        ("Fatality", claim_data.get("fatality")),
        ("Injuries", claim_data.get("injuries")),
        ("Witnesses", claim_data.get("witnesses")),
        ("Description of Accident", claim_data.get("description_of_accident")),
        ("Submitted On", datetime.now().strftime("%Y-%m-%d %H:%M"))
    ]

    # Proper wrapping for long text
    for label, value in fields:
        value = str(value) if value else "N/A"
        pdf.set_font("Arial", "B", 12)
        pdf.cell(60, 8, f"{label}:", border=0)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 8, value, border=0)
        pdf.ln(1)

    # Divider line
    pdf.ln(5)
    pdf.set_draw_color(0, 51, 153)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)

    # Footer message
    pdf.set_font("Arial", "I", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 8, "Thank you for choosing Awash Insurance. Our dedicated claims team will contact you within 24 hours.")
    pdf.ln(6)

    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(0, 51, 153)
    pdf.cell(0, 8, "Awash Insurance S.C. | We Flow With You.", align="C")

    # Safe file name
    safe_claim_ref = claim_data["claim_ref"].replace("/", "_")
    pdf_dir = "claims_pdfs"
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_output = os.path.join(pdf_dir, f"{safe_claim_ref}.pdf")
    pdf.output(pdf_output)

    return pdf_output
