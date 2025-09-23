import streamlit as st
import requests
from PIL import Image
import sqlite3
import os
from utils import predict_damage_type, generate_claim_reference, save_claim_with_image

st.set_page_config(page_title="🚗Awash Insurance Claim Bot", layout="centered")

# Logo
#st.image("D:\PYTHON PROJECTS\KIAM PROJECTS\Claim_Notification_chatbot\Awash_logo.jpg", width=1600, shape(name=None) caption="Awash Insurance Claim Notification Bot")

#if st.button("Ask questions"):
    #st.write("You can ask me questions about your insurance policy, claim status, coverage details")
    #url = "https://1c14e08768111fff0d.gradio.live"
    
st.markdown("[If you have Question, Ask here](https://1c14e08768111fff0d.gradio.live)")
# Custom CSS for branding
st.markdown(
    """
    <style>
    .stApp {
        background-color: Blue-black;
    }
    h1, h2, h3, h4 {
        color: #003399;
    }
    div.stButton > button {
        background-color: Blue;
        color: white;
        border-radius: 10px;
        font-size: 16px;
        font-weight: bold;
        padding: 8px 16px;
    }
    div.stButton > button:hover {
        background-color: #cc5200;
        color: #fff;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.title("🚗Claim Notification Assistant")
st.write("Hi! I'm your Auto Claim Notification Bot. Let's get started.")

# Inputs
name = st.text_input("Enter your name:")
branch = st.selectbox("Select Branch", ["FFN", "BOL", "LDT", "ADD", "DIRE", "JIMMA", "HARAR", "MEKELE", "SEMERA", "DIRE DAWA"])
Phone_number = st.text_input("Enter your phone number:")
policy_number = st.text_input("Enter your policy number:")
#Policy_Type = st.text_input("Enter your policy/cover type:")
Plate_number = st.text_input("Enter your plate number:")
Car_Model = st.text_input("Enter your car model:")
Year_of_Manufacture = st.text_input("Enter year of manufacture of the car:")
Date_of_Accident = st.date_input("Enter date when the accident happened:")
Time_of_Accident = st.time_input("Enter time when the accident happened(24 hours format):") 
Type_of_Accident = st.text_input("Enter type of accident (e.g., collision, theft):")
Fatality = st.selectbox("Was there any fatality?", ["Yes", "No"])
Fatality_Details = st.text_input("If yes, provide details of the fatality (if applicable):")
Injuries = st.selectbox("Were there any injuries?", ["Yes", "No"])
Location_of_Accident = st.text_input("Enter specific location where the accident happened:")
Legal_Authority_Contacted = st.selectbox("Was legal authority contacted?", ["Yes", "No"])
Police_Report_Number = st.text_input("Enter police report number (if applicable):") 
Witnesses = st.text_input("Enter names and contact info of any witnesses (if applicable):")
Description_of_Accident = st.text_area("Provide a brief description of the accident:")


# Upload images
uploaded_files = st.file_uploader(
    "Upload photos of the damage (multiple allowed):",
    type=["jpg", "png", "jpeg"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        img = Image.open(uploaded_file)
        st.image(img, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)

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
    if not all([name, policy_number, Plate_number, Location_of_Accident, uploaded_file, Type_of_Accident, branch]):
        st.error("⚠️ Please fill all fields and upload an image.")
    else:
        try:
            ai_response = f"Your claim has been submitted successfully. Reference: {generate_claim_reference(branch)}"

            # ✅ Save everything including image
            claim_ref = save_claim_with_image(
                name=name,
                policy_number=policy_number,
                plate_number=Plate_number,
                location=Location_of_Accident,
                branch=branch,
                uploaded_image=uploaded_file,
                date_of_accident=Date_of_Accident.isoformat()
            )

            st.success("✅ Claim submitted successfully!")
            st.info(f"🔖 **Claim Reference Number:** `{claim_ref}`")
            st.write("Our team will contact you soon. Please keep this number.")

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")