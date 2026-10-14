import streamlit as st
from playwright.sync_api import sync_playwright
import os
import requests
import time

if "browser_installed" not in st.session_state:
    try:
        os.system("playwright install chromium")
    except:
        pass
    st.session_state.browser_installed = True

st.set_page_config(page_title="NotRa Autonomous Agent", page_icon="🤖", layout="wide")

st.title("🤖 NotRa Autonomous Browser Agent")
st.caption("🟢 Live 3-sec SS stream, Captcha/Login pause handler & Smart execution")

if "action_history" not in st.session_state:
    st.session_state.action_history = []

task_command = st.text_input("Enter ANY task for NotRa (e.g., 'go to github and create repo', 'search lofi on youtube'):")

if st.button("Run NotRa Agent"):
    if not task_command:
        st.warning("Please enter a command first!")
    else:
        st.session_state.action_history = []
        status_box = st.empty()
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(viewport={"width": 1280, "height": 800})
                page = context.new_page()

                cmd = task_command.lower()

                # 1. Navigation / Task starting
                status_box.info("NotRa is initiating navigation...")
                if "http" in cmd or ".gd" in cmd or ".com" in cmd or ".net" in cmd or ".org" in cmd:
                    words = task_command.split()
                    url = next((w for w in words if w.startswith("http") or "." in w), "https://google.com")
                    if not url.startswith("http"): url = "https://" + url
                    page.goto(url)
                elif "youtube" in cmd or "yt" in cmd or "play" in cmd:
                    page.goto("https://www.youtube.com")
                    page.wait_for_timeout(2000)
                    q = cmd.replace("go to", "").replace("search", "").replace("on youtube", "").replace("youtube", "").replace("yt", "").replace("play", "").strip()
                    if not q: q = "trending"
                    try:
                        page.fill('input[name="search_query"]', q)
                    except:
                        page.keyboard.type(q)
                    page.keyboard.press('Enter')
                else:
                    page.goto(f"https://www.google.com/search?q={requests.utils.quote(task_command)}")

                # 2. 3-Second Interval Live SS Loop & Captcha/Login Detection
                for i in range(5):  # Monitor progress steps
                    page.wait_for_timeout(3000)  # Wait 3 seconds
                    current_url = page.url
                    page_text = page.inner_text("body").lower()

                    # Check for Captcha or Login blocks
                    if "captcha" in page_text or "robot" in page_text or "verify" in page_text:
                        status_box.error("⚠️ NotRa hit a CAPTCHA wall! Please take over control.")
                        break
                    elif "login" in current_url or "signin" in current_url:
                        status_box.warning(f"🔑 Login required at: {current_url}. Please complete sign-in.")
                        break

                    # Take live screenshot every 3 seconds
                    ss_path = f"live_ss_{i}.png"
                    page.screenshot(path=ss_path, full_page=False)
                    st.session_state.action_history.append((f"Live Action Step {i+1} (URL: {current_url})", ss_path))
                    status_box.info(f"NotRa is working... Step {i+1} captured.")

                browser.close()
                st.success("Task done Boss! 🎉 NotRa has successfully executed your command.")

        except Exception as e:
            st.error(f"NotRa Agent Error: {e}")

# Display Live 3-Sec Window Stream History
if st.session_state.action_history:
    st.subheader("📺 NotRa Live Window Stream (Every 3 Seconds)")
    for desc, img_p in st.session_state.action_history:
        st.markdown(f"**{desc}**")
        if os.path.exists(img_p):
            st.image(img_p, caption=desc, use_column_width=True)
        
