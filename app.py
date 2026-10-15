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

# Main Command Box
task_command = st.text_input("Enter your command (e.g., 'play lofi on youtube', 'open github.com', 'search top survey site'):")

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

                    # Smart URL / Domain Detection via Regex
                    url_match = re.search(r'(https?://[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', task_command)
                    target_url = None
                    if url_match:
                        matched_str = url_match.group(0).rstrip(".,!?;'")
                        if not matched_str.startswith("http"):
                            target_url = "https://" + matched_str
                        else:
                            target_url = matched_str

                    # Intent Execution Engine
                    if "youtube" in cmd or "yt" in cmd or "play" in cmd or "video" in cmd:
                        page.goto("https://www.youtube.com", wait_until="domcontentloaded", timeout=30000)
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
                            page.wait_for_timeout(3500)
                        except:
                            pass

                        # Robust Video Playback (Avoids unavailable/dead links)
                        if "play" in cmd or "video" in cmd:
                            try:
                                videos = page.locator('ytd-video-renderer a#video-title')
                                count = videos.count()
                                clicked = False
                                for i in range(min(count, 4)):
                                    try:
                                        videos.nth(i).click()
                                        page.wait_for_timeout(4000)
                                        clicked = True
                                        break
                                    except:
                                        continue
                                if not clicked and count > 0:
                                    videos.first.click()
                                    page.wait_for_timeout(4000)
                            except:
                                pass

                    elif target_url and not ("search" in cmd and "google" in cmd):
                        # Direct Website Navigation
                        try:
                            page.goto(target_url, wait_until="domcontentloaded", timeout=25000)
                            page.wait_for_timeout(2500)
                        except Exception as e:
                            st.error(f"⚠️ Could not load `{target_url}`. The domain might be down, invalid, or blocking automation.")
                            browser.close()
                            st.stop()

                    else:
                        # General Smart Google Search for other queries
                        clean_q = (cmd.replace("search on google", "")
                                      .replace("google", "")
                                      .replace("search", "")
                                      .replace("open", "")
                                      .replace("find", "")
                                      .strip())
                        if not clean_q: clean_q = task_command

                        google_url = f"https://www.google.com/search?q={requests.utils.quote(clean_q)}"
                        page.goto(google_url, wait_until="domcontentloaded", timeout=25000)
                        page.wait_for_timeout(2000)

                        # If user asked to open website from search result
                        if "open website" in cmd or "go to site" in cmd or "make an account" in cmd:
                            try:
                                page.locator('h3').first.click()
                                page.wait_for_timeout(3000)
                            except:
                                pass

                    # Handle Extra Actions
                    if user_action == "Scroll Down" or "scroll down" in cmd:
                        page.mouse.wheel(0, 800)
                        page.wait_for_timeout(1000)
                    elif user_action == "Scroll Up":
                        page.mouse.wheel(0, -800)
                        page.wait_for_timeout(1000)
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

                    # Intelligent Auth, Signup & Captcha Auto-Fill Helper
                    current_url = page.url
                    try:
                        page_body_text = page.inner_text("body").lower()
                    except:
                        page_body_text = ""

                    is_auth_required = any(k in current_url.lower() or k in page_body_text for k in ["login", "signin", "signup", "register", "create account"])
                    is_captcha_required = any(k in page_body_text for k in ["captcha", "robot", "verify you are human", "challenge"])

                    if input_user and input_pass and is_auth_required:
                        try:
                            page.fill('input[type="email"], input[name*="user"], input[name*="login"], input[placeholder*="email" i]', input_user)
                            page.fill('input[name*="password"], input[type="password"], input[placeholder*="password" i]', input_pass)
                            page.wait_for_timeout(1000)
                        except:
                            pass

                    if is_captcha_required:
                        st.error(f"⚠️ **Attention Ramim!** NotRa encountered a Captcha/Robot block at: [{current_url}]({current_url}). Please solve it manually.")
                    elif is_auth_required and not input_user:
                        st.warning(f"⚠️ **Auth/Sign-up page detected:** Please input your Username/Email & Password in the sidebar so NotRa can fill it automatically.")

                    # Capture Live View Screenshot
                    img1 = "step1.png"
                    page.screenshot(path=img1, full_page=False)
                    st.session_state.action_history.append((f"Task executed successfully (URL: {current_url})", img1))

                    browser.close()
                    st.success("Task processed successfully by NotRa!")

            except Exception as e:
                st.error(f"Agent Execution Error: {e}")

# Live Stream Window Display
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
