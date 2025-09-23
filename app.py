# app.py
import streamlit as st
from streamlit_toggle import st_toggle_switch
from PIL import Image
import os
import shutil
from datetime import datetime

# Import from utils (make sure these are defined)
from utils import (
    predict_damage_type,
    generate_claim_reference,
    save_claim_with_image,
    generate_claim_pdf
)

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="🛡️ Awash Insurance ClaimBot",
    page_icon="🚗",
    layout="centered"
)

# -------------------- SIDEBAR - THEME TOGGLE --------------------
#st.sidebar.title("🎨 Appearance")
theme = st_toggle_switch(
    label="Dark Mode",
    key="theme_toggle",
    default_value=False,
    label_after=True,
    inactive_color='Light',
    active_color='Dark',
    track_color="#E4E6E9"
)

# Dynamic CSS based on theme
if theme:

    primary_color = "#1D0CB8"
    bg_color = "#121212"
    text_color = "#2008F7"
    card_bg = "#1e1e1e"
    color_input="#0d65e9"
else:
    primary_color = "#1B9AF0"
    bg_color = "#3f80c0"
    text_color = "#030213"
    card_bg = "#030241"
    color_input="#0d11e9"

st.markdown(f"""
<style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
        font-family: 'Segoe UI', sans-serif;
        transition: background-color 0.3s ease;
    }}
    h1, h2, h3, h4 {{
        color: {primary_color} !important;
        font-weight: 600;
    }}
    .motto {{
        color: {"#050585" if not theme else "#EDEDF0"};
        font-style: italic;
        font-size: 1.1em;
        font-weight: 600;
        margin-bottom: 1rem;
    }}
    .claim-ref {{
        font-size: 24px;
        font-weight: bold;
        color: {primary_color};
        background-color: {"#1414d8" if theme else "#1b6cd6"};
        border-left: 5px solid {primary_color};
        padding: 16px;
        border-radius: 8px;
        text-align: center;
        font-family: 'Courier New', monospace;
        margin: 20px 0;
    }}
    .stButton>button {{
        background-color: {primary_color};
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: bold;
        padding: 12px 24px;
        font-size: 18px;
        box-shadow: 0 4px 8px rgba(0, 51, 153, 0.2);
    }}
    .stButton>button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 6px 12px rgba(0, 51, 153, 0.3);
        background-color: {"#0C0A8D" if theme else '#002266'};
        color: {'#121212' if theme else 'white'};
    }}
    .footer {{
        text-align: center;
        color: {"#0C0A8D" if theme else "#1FACE4"};
        font-size: 1em;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 1px solid {"#10A3CF" if theme else "#E5E5EC"};
    }}
    .stTextInput, .stSelectBox, .stDateInput, .stTimeInput, .stTextArea, .stNumberInput {{
        background-color: {card_bg};
        border: 1px solid {'#444' if theme else '#ccc'};
        border-radius: 8px;
        padding: 10px;
        font-size: 16px;
        color: {color_input if theme else '#030213'};
    }}
    .sttitle {{
        font-size: 2.5em;
        font-weight: 700;
        color: {"#0C0A8D" if theme else "#091BB8"};
        margin-bottom: 0.5rem;
        
    }}
</style>
""", unsafe_allow_html=True)

# -------------------- HEADER WITH LOGO & MOTTO --------------------
col1, col2 = st.columns([1, 3])

logo_path = r"D:\PYTHON PROJECTS\KIAM PROJECTS\Claim_Notification_chatbot\Awash_logo.jpg"

with col1:
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)
    else:
        st.write("🏦")

with col2:
    st.title("🛡️ Awash Insurance")
    st.markdown('<p class="motto"><strong>We flow with you</strong></p>', unsafe_allow_html=True)

st.markdown("---")



st.markdown("### 📝 Submit a New Claim")

# -------------------- FORM INPUTS --------------------
name = st.text_input("👤 Full Name")
branch = st.selectbox("🏢 Select Branch", [
    "FFN", "BOL", "LDT", "ADD", "DIR", "JIM", "HRR", "MKL", "WLT", "KZN", "GMB", "BRD", "NKM", "WLS", "PIS", "NFS", "ARB", "GFM", "DSE", "HWS", "DBR"
])
phone_number = st.number_input("📞 Phone Number")
policy_number = st.text_input("📄 Policy Number")
plate_number = st.text_input("🚘 Plate Number")
car_model = st.text_input("🚗 Car Model")
year_of_manufacture = st.date_input("📅 Year of Manufacture")
date_of_accident = st.date_input("🗓️ Date of Accident")
time_of_accident = st.time_input("⏰ Time of Accident (24hr)")
type_of_accident = st.text_input("🔧 Type of Accident (e.g., collision, theft)")
fatality = st.selectbox("💀 Was there any fatality?", ["Yes", "No"])
fatality_details = st.text_input("📝 Fatality Details (if applicable)")
injuries = st.selectbox("🩹 Were there any injuries?", ["Yes", "No"])
location = st.text_input("📍 Location of Accident")
legal_authority_contacted = st.selectbox("👮 Legal Authority Contacted?", ["Yes", "No"])
police_report_number = st.text_input("📋 Police Report Number (if applicable)")
witnesses = st.text_input("👥 Witnesses (names & contact info)")
description = st.text_area("📝 Description of the Accident")

# -------------------- IMAGE UPLOAD & ANALYSIS --------------------
uploaded_files = st.file_uploader(
    "📸 Upload photos of the damage:",
    type=["jpg", "png", "jpeg"],
    accept_multiple_files=True
)

image_paths = []

if uploaded_files:
    st.write(f"📷 Uploaded {len(uploaded_files)} image(s):")
    cols = st.columns(min(len(uploaded_files), 3))

    for idx, uploaded_file in enumerate(uploaded_files):
        with cols[idx % len(cols)]:
            img = Image.open(uploaded_file)
            st.image(img, caption=f"Photo {idx+1}", use_container_width=True)

            temp_path = f"temp_analysis_{idx}.jpg"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.spinner(f"🔍 Analyzing damage..."):
                predictions = predict_damage_type(temp_path)
                if "error" not in predictions:
                    st.markdown(f"**{predictions['predicted_damage']}**")
                    st.progress(int(predictions['confidence'] * 100))
                else:
                    st.error(predictions["error"])

            if os.path.exists(temp_path):
                os.remove(temp_path)

            image_paths.append((uploaded_file, f"img_{idx+1}.jpg"))

# -------------------- SUBMIT CLAIM BUTTON --------------------
if st.button("Submit Claim"):
    required = [name, policy_number, plate_number, location, type_of_accident, branch]
    if not all(required) or not uploaded_files:
        st.error("⚠️ Please fill all required fields and upload at least one image.")
    else:
        try:
            claim_ref = generate_claim_reference(branch)

            # Gather full claim data
            claim_data = {
                "claim_ref": claim_ref,
                "name": name,
                "branch": branch,
                "phone_number": phone_number,
                "policy_number": policy_number,
                "plate_number": plate_number,
                "car_model": car_model,
                "year_of_manufacture": year_of_manufacture,
                "date_of_accident": date_of_accident.isoformat(),
                "time_of_accident": time_of_accident.isoformat(),
                "type_of_accident": type_of_accident,
                "fatality": fatality,
                "fatality_details": fatality_details,
                "injuries": injuries,
                "location": location,
                "legal_authority_contacted": legal_authority_contacted,
                "police_report_number": police_report_number,
                "witnesses": witnesses,
                "description_of_accident": description
            }

            # Save to DB and file system
            save_claim_with_image(
                **claim_data,
                uploaded_images=image_paths,
                ai_response=f"Claim submitted successfully. Ref: {claim_ref}"
            )

            # Generate PDF
            pdf_path = generate_claim_pdf(claim_data, logo_path=logo_path)

            # Success feedback
            st.success("✅ Your claim has been submitted successfully!")
            st.balloons()
            st.markdown(f'<div class="claim-ref">{claim_ref}</div>', unsafe_allow_html=True)
            st.info("Our team will contact you within 24 hours.")

            # Download PDF button
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download Claim Receipt (PDF)",
                    data=f.read(),
                    file_name=f"{claim_ref}.pdf",
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            
            # -------------------- QUICK LINK TO CHATBOT --------------------
st.markdown(
    """
    💬 Need help? [Ask our AI Assistant](https://3a7f42f57eb56c3528.gradio.live)  
    _Get instant answers about policies, claims, and coverage._
    """,
    unsafe_allow_html=True
)

st.markdown('<p class="motto"><strong>Where there is Awash there is peace of mind!</strong></p>', unsafe_allow_html=True)
# -------------------- FOOTER --------------------
st.markdown("---")
st.markdown(
    '<div class="footer">'
    '© 2025 Awash Insurance S.C. All rights reserved. | '
    '<a href="https://awashinsurance.com" target="_blank">awashinsurance.com</a> | '
    'Version 1.4'
    '</div>',
    unsafe_allow_html=True
)