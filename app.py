import streamlit as st
import requests
from PIL import Image
import os
from utils import extract_text_from_image, predict_damage_type

st.set_page_config(page_title="🚗 Auto Claim Bot", layout="centered")

st.title("🚗 Auto Claim Assistant")
st.write("Hi! I'm your Auto Claim Bot. Let's get started.")

# Inputs
name = st.text_input("Enter your name:")
policy_number = st.text_input("Enter your policy number:")

# Upload image
uploaded_file = st.file_uploader("Upload a photo of the damage:", type=["jpg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    temp_path = os.path.join("temp_upload.jpg")
    img.save(temp_path)

    with st.spinner("🔍 Analyzing damage type..."):
        predictions = predict_damage_type(temp_path)

        if "error" in predictions:
            st.error(predictions["error"])
        else:
            st.write("🔍 Predicted Damage Type:", predictions["predicted_damage"])
            st.write("Confidence:", f"{predictions['confidence']:.2%}")
            
            # Additional predictions display if available
            if isinstance(predictions, list):
                for pred in predictions:
                    if isinstance(pred, dict):
                        try:
                            prob = float(pred.get('prob', 0))
                            st.write(f"{pred.get('description', 'N/A')} ({prob:.2%})")
                        except (ValueError, TypeError) as e:
                            st.error(f"Invalid probability value: {pred.get('prob')}")
                    else:
                        st.warning(f"Unexpected prediction format: {type(pred)}")
    
    # Clean up temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)

if st.button("Submit Claim"):
    if not name or not policy_number or not uploaded_file:
        st.error("⚠️ Please fill all fields and upload an image.")
    else:
        # Submit to backend
        url = "http://localhost:5000/submit_claim"
        files = {"image": uploaded_file}
        data = {
            "name": name,
            "policy": policy_number
        }
        try:
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()  # Raises exception for 4XX/5XX errors
            result = response.json()
            st.success("✅ Claim submitted successfully!")
            st.json(result)
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error submitting claim: {str(e)}")
        except ValueError:
            st.error("❌ Invalid response from server")