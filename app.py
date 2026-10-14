import streamlit as st
from playwright.sync_api import sync_playwright
import os
import requests

if "browser_installed" not in st.session_state:
    try:
        os.system("playwright install chromium")
    except:
        pass
    st.session_state.browser_installed = True

st.set_page_config(page_title="NotRa Autonomous Agent", page_icon="🤖", layout="wide")

st.title("🤖 NotRa Smart AI Browser Agent")
st.caption("🟢 Live View Refresh + Real Human Actions (Scroll/Click/Play) + Smart Qwen Parser")

if "action_history" not in st.session_state:
    st.session_state.action_history = []

# Sidebar for Login Credentials
with st.sidebar:
    st.header("🔑 Login & Auth Helper")
    st.markdown("Kono site-e login ba sign-up lagbe, ekhane info diye dile agent automatic fill-up korbe.")
    input_user = st.text_input("Username / Email")
    input_pass = st.text_input("Password", type="password")

# Main Command Box
task_command = st.text_input("Enter any command (e.g., 'play a lofi song on youtube', 'scroll down', 'click on sign in'):")

col1, col2 = st.columns(2)
with col1:
    user_action = st.selectbox("Extra Action:", ["None", "Scroll Down", "Scroll Up", "Click First Video / Result", "Go Back"])
with col2:
    custom_click_text = st.text_input("Or Click Element by Text (optional):", "")

# Smart Qwen LLM Parser
def parse_command_with_qwen(command):
    API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-0.5B-Instruct"
    payload = {
        "inputs": f"Analyze this browser command: '{command}'. Determine if it's a search, play video, scroll, or navigation task. Reply in short.",
        "parameters": {"max_new_tokens": 40}
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=6)
        if response.status_code == 200:
            res = response.json()
            if isinstance(res, list) and len(res) > 0:
                return res[0].get("generated_text", command)
    except Exception as e:
        print(f"LLM Parse Error: {e}")
    return command

if st.button("Run Browser Agent"):
    if not task_command:
        st.warning("Please enter a command first!")
    else:
        st.session_state.action_history = []
        with st.spinner(f"NotRa is analyzing and executing: '{task_command}'..."):
            try:
                # 1. Understand command first using Qwen LLM parser
                llm_parsed = parse_command_with_qwen(task_command)
                
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    context = browser.new_context(viewport={"width": 1280, "height": 800})
                    page = context.new_page()

                    cmd = task_command.lower()

                    # 2. Smart Navigation & Action Execution
                    if "http" in cmd or ".gd" in cmd or ".com" in cmd or ".net" in cmd or ".org" in cmd:
                        words = task_command.split()
                        url = next((w for w in words if w.startswith("http") or "." in w), "https://google.com")
                        if not url.startswith("http"): url = "https://" + url
                        page.goto(url)
                        page.wait_for_timeout(3000)
                    elif "youtube" in cmd or "yt" in cmd or "play" in cmd or "video" in cmd:
                        page.goto("https://www.youtube.com")
                        page.wait_for_timeout(2000)
                        q = cmd.replace("go to", "").replace("search", "").replace("on youtube", "").replace("youtube", "").replace("yt", "").replace("play", "").replace("video", "").strip()
                        if not q: q = "trending music"
                        
                        try:
                            page.fill('input[name="search_query"]', q)
                        except:
                            page.keyboard.type(q)
                        page.keyboard.press('Enter')
                        page.wait_for_timeout(4000)
                        
                        # Real human-like action: Automatically click & play the first video if requested!
                        if "play" in cmd or "video" in cmd:
                            try:
                                page.locator('ytd-video-renderer #video-title').first.click()
                                page.wait_for_timeout(4000)
                            except:
                                pass
                    else:
                        page.goto(f"
    
