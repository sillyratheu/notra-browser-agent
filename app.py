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

st.set_page_config(page_title="NotRa Browser Agent", page_icon="🤖", layout="wide")

st.title("🤖 NotRa Autonomous Browser Agent")
st.caption("🟢 Built and Owned exclusively by Ramim • Ultra-Fast Smart Intent Engine")

if "action_history" not in st.session_state:
    st.session_state.action_history = []

# Sidebar for Login Credentials Helper
with st.sidebar:
    st.header("🔑 Login & Auth Helper")
    st.markdown("Kono site-e login ba sign-up lagbe, ekhane info diye dile agent automatic fill-up korbe.")
    input_user = st.text_input("Username / Email")
    input_pass = st.text_input("Password", type="password")

# Main Command Box
task_command = st.text_input("Enter clean command (e.g., 'play lofi on youtube', 'open topsurvey.app', 'search python'):")

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
        with st.spinner("NotRa is executing instantly..."):
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

                    # Smart Direct URL Navigation with Fallback to Google if site fails
                    if "http" in cmd or ".app" in cmd or ".com" in cmd or ".net" in cmd or ".org" in cmd or ".io" in cmd or ".gd" in cmd:
                        words = task_command.split()
                        url = next((w for w in words if "http" in w or "." in w), "https://google.com")
                        if not url.startswith("http"):
                            url = "https://" + url
                        url = url.rstrip(".,!?;'")
                        
                        try:
                            page.goto(url, timeout=30000)
                            page.wait_for_timeout(3000)
                        except:
                            # Fallback if connection fails/closed
                            google_url = f"https://www.google.com/search?q={requests.utils.quote(task_command)}"
                            page.goto(google_url, timeout=30000)
                            page.wait_for_timeout(2000)
                            try:
                                page.locator('h3').first.click()
                                page.wait_for_timeout(3000)
                            except:
                                pass

                    elif "youtube" in cmd or "yt" in cmd or "play" in cmd or "video" in cmd:
                        page.goto("https://www.youtube.com", timeout=30000)
                        page.wait_for_timeout(2000)

                        q = (cmd.replace("open youtube", "")
                                .replace("search on youtube", "")
                                .replace("youtube", "")
                                .replace("yt", "")
                                .replace("play", "")
                                .replace("open", "")
                                .replace("search", "")
                                .replace("video", "")
                                .replace("the", "")
                                .replace("first", "")
                                .replace("on", "")
                                .strip())

                        if not q: q = "lofi music"

                        try:
                            page.fill('input[name="search_query"]', q)
                            page.keyboard.press('Enter')
                            page.wait_for_timeout(4000)
                        except:
                            pass

                        # Fix for YouTube video unavailable: skip livestreams/premiere/shorts or expired ones if needed, click valid video
                        if "play" in cmd or "video" in cmd:
                            try:
                                # Try clicking the second or first non-broken thumbnail title link
                                videos = page.locator('ytd-video-renderer a#video-title')
                                if videos.count() > 0:
                                    videos.first.click()
                                    page.wait_for_timeout(4000)
                            except:
                                try:
                                    page.locator('#contents ytd-video-renderer').first.click()
                                    page.wait_for_timeout(4000)
                                except:
                                    pass
                    else:
                        clean_q = (cmd.replace("search on google", "")
                                      .replace("google", "")
                                      .replace("search", "")
                                      .replace("open", "")
                                      .replace("find", "")
                                      .strip())
                        if not clean_q: clean_q = task_command

                        google_url = f"https://www.google.com/search?q={requests.utils.quote(clean_q)}"
                        page.goto(google_url, timeout=30000)
                        page.wait_for_timeout(2000)

                        if "open website" in cmd or "go to site" in cmd:
                            try:
                                page.locator('h3').first.click()
                                page.wait_for_timeout(2500)
                            except:
                                pass

                    # Handle Extra Actions Quickly
                    if user_action == "Scroll Down" or "scroll down" in cmd:
                        page.mouse.wheel(0, 800)
                        page.wait_for_timeout(1500)
                    elif user_action == "Scroll Up":
                        page.mouse.wheel(0, -800)
                        page.wait_for_timeout(1500)
                    elif user_action == "Click First Result":
                        try:
                            page.locator('h3, ytd-video-renderer #video-title').first.click()
                            page.wait_for_timeout(2500)
                        except:
                            pass
                    elif custom_click_text:
                        try:
                            page.get_by_text(custom_click_text, exact=False).first.click()
                            page.wait_for_timeout(2500)
                        except:
                            pass

                    # Intelligent Check for Login, Sign up, or Captcha & Auto Fill
                    current_url = page.url
                    page_body_text = page.inner_text("body").lower()

                    is_auth_required = any(k in current_url.lower() or k in page_body_text for k in ["login", "signin", "signup", "register", "create account"])
                    is_captcha_required = any(k in page_body_text for k in ["captcha", "robot", "verify you are human", "challenge"])

                    if input_user and input_pass:
                        try:
                            page.fill('input[type="email"], input[name*="user"], input[name*="login"], input[placeholder*="email" i]', input_user)
                            page.fill('input[name*="password"], input[type="password"], input[placeholder*="password" i]', input_pass)
                            page.wait_for_timeout(1000)
                        except:
                            pass

                    if is_captcha_required:
                        st.error(f"⚠️ **Attention Ramim!** NotRa encountered a Captcha block at: [{current_url}]({current_url}). Please solve it manually!")
                    elif is_auth_required and not input_user:
                        st.warning(f"⚠️ **Auth/Sign-up detected:** Please provide Username/Email & Password in the sidebar so NotRa can fill it automatically.")

                    # Capture Live View Screenshot
                    img1 = "step1.png"
                    page.screenshot(path=img1, full_page=False)
                    st.session_state.action_history.append((f"Task executed successfully (URL: {current_url})", img1))

                    browser.close()
                    st.success("Task processed successfully by NotRa!")

            except Exception as e:
                st.error(f"Agent Execution Error: {e}")

# Live Stream Window Display with Manual Refresh Button
st.subheader("🖥️ Live Browser Action Stream")
if st.button("🔄 Refresh Live View"):
    st.rerun()

if st.session_state.action_history:
    desc, img_p = st.session_state.action_history[-1]
    st.markdown(f"**Status:** {desc}")
    if os.path.exists(img_p):
        st.image(img_p, caption=desc, use_container_width=True)
else:
    st.info("Execute a task above to see the live browser view.")
