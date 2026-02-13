# app.py
import streamlit as st
from PIL import Image
import os
import re
from datetime import datetime

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

# -------------------- CUSTOM THEME (Awash Blue Gradient) --------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #EAF3FA 0%, #BFD7ED 50%, #8DB9E5 100%);
    color: #002060;
    font-family: 'Segoe UI', sans-serif;
}
h1, h2, h3, h4 {
    color: #002060 !important;
    font-weight: 700;
}
.motto {
    color: #0056A6;
    font-style: italic;
    font-size: 1.1em;
    font-weight: 600;
    margin-bottom: 1rem;
}
.claim-ref {
    font-size: 22px;
    font-weight: bold;
    color: #0056A6;
    background-color: #EAF3FA;
    border-left: 5px solid #0056A6;
    padding: 14px;
    border-radius: 8px;
    text-align: center;
    font-family: 'Courier New', monospace;
    margin: 20px 0;
}

/* Input & Select Fields */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stTimeInput input {
    background-color: #FFFFFF !important;
    border: 1.5px solid #0056A6 !important;
    border-radius: 10px !important;
    color: #002060 !important;
    padding: 10px !important;
    font-size: 16px !important;
}

/* Placeholder Text Color */
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #002060 !important;
    opacity: 1 !important;
}

/* Dropdown text */
div[data-baseweb="select"] > div {
    color: #FFFFF !important;
}

/* Buttons */
.stButton>button {
    background-color: #0056A6 !important;
    color: #FFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    font-size: 17px !important;
    font-weight: bold !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.stButton>button:hover {
    background-color: #003B73 !important;
    transform: translateY(-1px);
}

/* Footer */
.footer {
    text-align: center;
    color: #003B73;
    font-size: 1em;
    margin-top: 3rem;
    padding: 1rem;
    border-top: 1px solid #AACBE4;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
/* Input and Field Label Colors */
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stDateInput label, .stTimeInput label, .stTextArea label {
    color: #003B73 !important;          /* Awash Blue */
    font-weight: 600 !important;
    font-size: 15px !important;
}

/* Add an icon + label alignment fix */
.stTextInput label p, .stSelectbox label p,
.stDateInput label p, .stTimeInput label p {
    display: flex;
    align-items: center;
    gap: 6px;
}

/* Optional - make icons slightly smaller for visual balance */
.stTextInput label p span, .stSelectbox label p span {
    font-size: 18px;
}

/* Add a subtle underline when focused */
.stTextInput input:focus, .stTextArea textarea:focus,
.stSelectbox div[data-baseweb="select"]:focus-within {
    border-color: #0078D7 !important;
    box-shadow: 0 0 6px rgba(0, 120, 215, 0.3) !important;
}
</style>
""", unsafe_allow_html=True)


# -------------------- HEADER --------------------
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

# -------------------- CLAIM FORM --------------------
st.markdown("### 📝 Submit a New Claim")

# Input Fields
name = st.text_input("👤 Full Name", placeholder="Enter your full name")

branch = st.selectbox("🏢 Select Branch", [
    "FFN", "BOL", "LDT", "ADD", "DIR", "JIM", "HRR", "MKL", "WLT", "KZN",
    "GMB", "BRD", "NKM", "WLS", "PIS", "NFS", "ARB", "GFM", "DSE", "HWS", "DBR"
])

phone_number = st.text_input("📞 Phone Number", placeholder="+251912345678")
if phone_number and not re.match(r"^\+?\d{9,15}$", phone_number):
    st.warning("⚠️ Please enter a valid phone number (e.g., +251912345678).")

policy_number = st.text_input("📄 Policy Number", placeholder="Enter your policy number")
plate_number = st.text_input("🚘 Plate Number", placeholder="Enter vehicle plate number")
car_model = st.text_input("🚗 Car Model", placeholder="Enter car model")
year_of_manufacture = st.date_input("📅 Year of Manufacture")
date_of_accident = st.date_input("🗓️ Date of Accident")
time_of_accident = st.time_input("⏰ Time of Accident (24hr)")
type_of_accident = st.text_input("🔧 Type of Accident", placeholder="e.g., Collision, Theft, Fire")

fatality = st.selectbox("💀 Was there any fatality?", ["No", "Yes"])
fatality_details = ""
if fatality == "Yes":
    fatality_details = st.text_area("📝 Fatality Details")

injuries = st.selectbox("🩹 Were there any injuries?", ["No", "Yes"])
location = st.text_input("📍 Location of Accident")
legal_authority_contacted = st.selectbox("👮 Legal Authority Contacted?", ["No", "Yes"])
police_report_number = st.text_input("📋 Police Report Number (if applicable)")
witnesses = st.text_area("👥 Witnesses (names & contact info)")
description = st.text_area("📝 Description of the Accident")

# -------------------- IMAGE UPLOAD --------------------
uploaded_files = st.file_uploader(
    "📸 Upload photos of the damage",
    type=["jpg", "png", "jpeg"],
    accept_multiple_files=True
)

# Preview images
if uploaded_files:
    st.write(f"📷 Uploaded {len(uploaded_files)} image(s):")
    cols = st.columns(min(len(uploaded_files), 3))
    for idx, uploaded_file in enumerate(uploaded_files):
        with cols[idx % len(cols)]:
            st.image(uploaded_file, caption=f"Photo {idx+1}", use_container_width=True)

# -------------------- SUBMIT CLAIM --------------------
if st.button("Submit Claim"):
    required = [name, policy_number, plate_number, location, type_of_accident, branch]
    if not all(required) or not uploaded_files:
        st.error("⚠️ Please fill all required fields and upload at least one image.")
    else:
        try:
            claim_ref = generate_claim_reference(branch)
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

            # Save and generate PDF
            save_claim_with_image(**claim_data, uploaded_images=uploaded_files, ai_response=f"Claim submitted successfully. Ref: {claim_ref}")
            pdf_path = generate_claim_pdf(claim_data, logo_path=logo_path)

            # Success Message
            st.success("✅ Your claim has been submitted successfully!")
            st.markdown(f'<div class="claim-ref">{claim_ref}</div>', unsafe_allow_html=True)
            st.info("Our team will contact you within 24 hours.")

            # Download PDF
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download Claim Receipt (PDF)",
                    data=f.read(),
                    file_name=f"{claim_ref}.pdf",
                    mime="application/pdf"
                )
            st.balloons()
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

# -------------------- FOOTER --------------------
st.markdown("---")
st.markdown(
    '<div class="footer">'
    '© 2025 Awash Insurance S.C. All rights reserved. | '
    '<a href="https://awashinsurance.com" target="_blank">awashinsurance.com</a> | '
    'Version 1.5'
    '</div>',
    unsafe_allow_html=True
)
