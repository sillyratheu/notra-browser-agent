import streamlit as st
from playwright.sync_api import sync_playwright
import os
import requests
import re

if "browser_installed" not in st.session_state:
    try:
        os.system("playwright install chromium")
    except:
        pass
    st.session_state.browser_installed = True

st.set_page_config(page_title="NotRa Browser Agent", page_icon="🤖", layout="wide")

st.title("🤖 NotRa Autonomous Browser Agent")
st.caption("🟢 Built and Owned exclusively by Ramim • Advanced Smart Intent Engine")

if "action_history" not in st.session_state:
    st.session_state.action_history = []

# Sidebar for Login Credentials Helper
with st.sidebar:
    st.header("🔑 Login & Auth Helper")
    st.markdown("Kono site-e login ba sign-up lagbe, ekhane info diye dile agent automatic fill-up korbe.")
    input_user = st.text_input("Username / Email")
    input_pass = st.text_input("Password", type="password")

# --- Generic Command Helper Menu (No fixed values) ---
st.markdown("### ⚡ Command Helper Menu")

preset_options = [
    "-- Select Command Type --",
    "Google Search - [enter query]",
    "Open Website - [enter domain.com]",
    "YouTube Search - [enter video/song]",
    "Play YouTube Video - [enter title]",
    "Do Task - [open site & sign up]"
]

selected_preset = st.selectbox("Choose Command Template:", preset_options)

# Generic template mapping
preset_mapping = {
    "Google Search - [enter query]": "search ",
    "Open Website - [enter domain.com]": "open ",
    "YouTube Search - [enter video/song]": "search on youtube ",
    "Play YouTube Video - [enter title]": "play on youtube ",
    "Do Task - [open site & sign up]": "open site and create account "
}

default_cmd_value = preset_mapping.get(selected_preset, "") if selected_preset != "-- Select Command Type --" else ""

# Main Command Box
task_command = st.text_input("Enter clean command (e.g., 'play lofi on youtube', 'open github.com'):", value=default_cmd_value)

col1, col2 = st.columns(2)
with col1:
    user_action = st.selectbox("Extra Action:", ["None", "Scroll Down", "Scroll Up", "Click First Result", "Go Back"])
with col2:
    custom_click_text = st.text_input("Or Click Element by Text (optional):", "")

if st.button("Run Browser Agent"):
    if not task_command:
        st.warning("Please enter a command first!")
    else:
        st.session_state.action_history = []
        with st.spinner("NotRa is executing your command intelligently..."):
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(
                        headless=True,
                        args=[
                            "--disable-blink-features=AutomationControlled",
                            "--no-sandbox",
                            "--disable-setuid-sandbox"
                        ]
                    )

                    context = browser.new_context(
                        viewport={"width": 1280, "height": 800},
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                    )
                    page = context.new_page()

                    cmd = task_command.lower().strip()

                    # Smart URL / Domain Detection via Regex for External Websites
                    url_match = re.search(r'(https?://[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', task_command)
                    target_url = None
                    if url_match:
                        matched_str = url_match.group(0).rstrip(".,!?;'")
                        if not matched_
