import os
import streamlit as st

def authorize():
    user_domain = os.environ.get("USERDOMAIN", "").upper()
    ALLOWED_DOMAINS = ["NESTLE"]

    if user_domain not in ALLOWED_DOMAINS:
        st.error(f"🚫 Access denied. Unauthorized User!")
        st.stop()