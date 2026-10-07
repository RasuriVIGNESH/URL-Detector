import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
API_KEY = os.getenv("API_KEY", "change-this-demo-key")

st.set_page_config(page_title="Secure Phishing URL Detector", page_icon="🔐", layout="centered")
st.title("Secure Phishing URL Detector")
st.caption("Static URL analysis using machine learning. The submitted URL is never opened.")

url = st.text_input("Enter a URL", placeholder="https://www.example.com")
if st.button("Check URL", type="primary", use_container_width=True):
    if not url.strip():
        st.warning("Please enter a URL.")
    else:
        try:
            response = requests.post(
                f"{API_URL}/predict",
                json={"url": url},
                headers={"X-API-Key": API_KEY},
                timeout=10,
            )
            if response.ok:
                result = response.json()
                if result["prediction"] == "phishing":
                    st.error(f"Prediction: PHISHING | Risk: HIGH")
                    st.warning("Do not open this URL or enter passwords/payment details.")
                else:
                    st.success(f"Prediction: LEGITIMATE | Risk: LOW")
                    st.info("No strong phishing indicators were found in the URL text.")
                st.metric("Confidence", f"{result['confidence'] * 100:.2f}%")
                st.write("**Model version:**", result["model_version"])
                with st.expander("Extracted features"):
                    st.json(result["features"])
                st.caption(result["disclaimer"])
            else:
                detail = response.json().get("detail", response.text)
                st.error(f"Request rejected: {detail}")
        except requests.RequestException as exc:
            st.error(f"Could not reach the API at {API_URL}: {exc}")

st.divider()
st.caption("Educational demonstration only. This classifier is not a replacement for a production URL reputation service.")
