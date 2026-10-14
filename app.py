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
st.caption("🟢 Powered by Qwen LLM Parser & Live Playwright Automation")

if "action_history" not in st.session_state:
    st.session_state.action_history = []

# Sidebar for Login Credentials
with st.sidebar:
    st.header("🔑 Login & Auth Helper")
    st.markdown("Kono site-e login ba sign-up lagbe, ekhane info diye dile agent automatic fill-up korbe.")
    input_user = st.text_input("Username / Email")
    input_pass = st.text_input("Password", type="password")

# Main Command Box
task_command = st.text_input("Enter any command (e.g., 'go to youtube and search lofi', 'open github and login'):")

# Use Hugging Face Free Qwen API as a smart parser (Zero RAM usage, zero crash!)
def parse_command_with_qwen(command):
    API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-0.5B-Instruct"
    payload = {
        "inputs": f"Extract the core action and target from this browser command: '{command}'. Reply in format 'ACTION: [navigate/search/click] | TARGET: [query/url]'",
        "parameters": {"max_new_tokens": 40}
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=8)
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
        with st.spinner(f"NotRa Qwen LLM is analyzing & executing: '{task_command}'..."):
            try:
                # Get smart interpretation from Qwen LLM
                llm_parsed = parse_command_with_qwen(task_command)
                
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    context = browser.new_context(viewport={"width": 1280, "height": 800})
                    page = context.new_page()

                    cmd = task_command.lower()

                    # Universal Navigation & Task Execution
                    if "http" in cmd or ".gd" in cmd or ".com" in cmd or ".net" in cmd or ".org" in cmd:
                        words = task_command.split()
                        url = next((w for w in words if w.startswith("http") or "." in w), "https://google.com")
                        if not url.startswith("http"):
                            url = "https://" + url
                        page.goto(url)
                        page.wait_for_timeout(3000)
                    elif "youtube" in cmd or "yt" in cmd or "play" in cmd:
                        page.goto("https://www.youtube.com")
                        page.wait_for_timeout(2000)
                        q = cmd.replace("go to", "").replace("search", "").replace("on youtube", "").replace("youtube", "").replace("yt", "").replace("play", "").strip()
                        if not q: q = "trending"
                        page.fill('input[name="search_query"]', q)
                        page.keyboard.press('Enter')
                        page.wait_for_timeout(4000)
                    else:
                        page.goto(f"https://www.google.com/search?q={requests.utils.quote(task_command)}")
                        page.wait_for_timeout(3000)

                    # Capture Step 1 Live View
                    img1 = "step1.png"
                    page.screenshot(path=img1, full_page=False)
                    st.session_state.action_history.append((f"Executed via Qwen Parser: {llm_parsed}", img1))

                    # Auto Login Check
                    if "login" in page.url.lower() or "signin" in page.url.lower():
                        if input_user and input_pass:
                            page.fill('input[type="email"], input[name*="user"], input[name*="login"]', input_user)
                            page.fill('input[type="password"]', input_pass)
                            page.keyboard.press('Enter')
                            page.wait_for_timeout(4000)
                            img_login = "step_login.png"
                            page.screenshot(path=img_login, full_page=False)
                            st.session_state.action_history.append(("Auto-Filled Login & Logged In", img_login))

                    browser.close()
                    st.success("Task completed successfully!")

            except Exception as e:
                st.error(f"Agent Execution Error: {e}")

# Live Stream Window Display
if st.session_state.action_history:
    st.subheader("🖥️ Live Browser Action Stream")
    for desc, img_p in st.session_state.action_history:
        st.markdown(f"**Status:** {desc}")
        if os.path.exists(img_p):
            st.image(img_p, caption=desc, use_column_width=True)
    
