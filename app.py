import streamlit as st
import requests
from PIL import Image
import os
from utils import extract_text_from_image, predict_damage_type

st.set_page_config(page_title="🚗 Auto Claim Bot", layout="centered")

st.title("🚗Claim Notification Assistant")
st.write("Hi! I'm your Auto Claim Notification Bot. Let's get started.")

# Inputs
name = st.text_input("Enter your name:")
policy_number = st.text_input("Enter your policy number:")
Policy_Type = st.text_input("Enter your policy type:")
Plate_number = st.text_input("Enter your plate number:")
Location_of_Accident = st.text_input("Enter specific location where the accident happened:")

# Upload images
uploaded_files = st.file_uploader(
    "Upload photos of the damage (multiple allowed):",
    type=["jpg", "png", "jpeg"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        img = Image.open(uploaded_file)
        st.image(img, caption=f"Uploaded: {uploaded_file.name}", use_column_width=True)

        temp_path = os.path.join("temp_upload.jpg")
        img.save(temp_path)

        with st.spinner("🔍 Analyzing damage type..."):
            predictions = predict_damage_type(temp_path)

            if "error" in predictions:
                st.error(predictions["error"])
            else:
                st.write("🔍 Predicted Damage Type:", predictions["predicted_damage"])
                st.write("Confidence:", f"{predictions['confidence']:.2%}")
                
                if isinstance(predictions, list):
                    for pred in predictions:
                        if isinstance(pred, dict):
                            try:
                                prob = float(pred.get('prob', 0))
                                st.write(f"{pred.get('description', 'N/A')} ({prob:.2%})")
                            except (ValueError, TypeError):
                                st.error(f"Invalid probability value: {pred.get('prob')}")
                        else:
                            st.warning(f"Unexpected prediction format: {type(pred)}")

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if st.button("Submit Claim"):
    if not name or not policy_number or not uploaded_files:
        st.error("⚠️ Please fill all fields and upload at least one image.")
    else:
        url = "http://localhost:5000/submit_claim"
        
        # Send images under the key "image" (Flask expects this)
        #files = [("image", (f.name, f, f, f.type)) for f in uploaded_files]
        files = [("image", (f.name, f, f.type)) for f in uploaded_files]

        
        data = {
            "name": name,
            "policy": policy_number
        }
        try:
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()
            result = response.json()
            st.success("✅ Claim submitted successfully!")
            st.json(result)
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error submitting claim: {str(e)}")
        except ValueError:
            st.error("❌ Invalid response from server")


