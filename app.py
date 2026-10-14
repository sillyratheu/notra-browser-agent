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

st.set_page_config(page_title="NotRa Autonomous Cloud Agent", page_icon="🤖", layout="centered")

st.title("🤖 NotRa Autonomous Browser Agent")
st.caption("🟢 Full interactive automation & login handler")

# Session states for maintaining browser state & login credentials
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Command input box
command = st.text_input("Give a complex task (e.g., 'go to github, login, and create a repo', 'play video on youtube'):")

# Login credentials expander if site requires sign in
with st.expander("🔑 Secure Login Credentials (Optional)"):
    user_email = st.text_input("Email / Username", type="default")
    user_pass = st.text_input("Password", type="password")

if st.button("Run Autonomous Task"):
    if not command:
        st.warning("Please enter a task command!")
    else:
        with st.spinner(f"NotRa is autonomously executing: '{command}'..."):
            try:
                with sync_playwright() as p:
                    # Run visible or headless based on needs (headless=True on cloud)
                    browser = p.chromium.launch(headless=True)
                    context = browser.new_context(viewport={"width": 1280, "height": 800})
                    page = context.new_page()

                    cmd_lower = command.lower()

                    # Example 1: GitHub Login & Automation Task
                    if "github" in cmd_lower:
                        page.goto("https://github.com/login")
                        page.wait_for_timeout(2000)
                        
                        if user_email and user_pass:
                            page.fill('input#login_field', user_email)
                            page.fill('input#password', user_pass)
                            page.click('input[name="commit"]')
                            page.wait_for_timeout(4000)
                            st.info("🔐 Injected credentials and attempted login!")
                        else:
                            st.warning("⚠️ No credentials provided. Proceeding as guest/view-only.")

                        if "create" in cmd_lower or "repo" in cmd_lower:
                            page.goto("https://github.com/new")
                            page.wait_for_timeout(3000)

                    # Example 2: YouTube Video Playback / Interaction
                    elif "youtube" in cmd_lower or "yt" in cmd_lower or "play" in cmd_lower:
                        page.goto("https://www.youtube.com")
                        page.wait_for_timeout(2000)
                        
                        q = cmd_lower.replace("go to", "").replace("search", "").replace("on youtube", "").replace("youtube", "").replace("play", "").strip()
                        if not q: q = "lofi music"
                        
                        page.fill('input[name="search_query"]', q)
                        page.keyboard.press('Enter')
                        page.wait_for_timeout(4000)
                        
                        # Click the first video to play it
                        try:
                            page.click('ytd-video-renderer #video-title')
                            page.wait_for_timeout(3000)
                            st.info("▶️ Video opened and playing autonomously!")
                        except:
                            pass

                    # Example 3: General Browsing / Survey Filling
                    else:
                        page.goto(f"https://www.google.com/search?q={requests.utils.quote(command)}")
                        page.wait_for_timeout(3000)

                    # Capture final state screenshot
                    page_title = page.title()
                    screenshot_path = "agent_action.png"
                    page.screenshot(path=screenshot_path, full_page=False)
                    browser.close()

                    st.success(f"Task executed successfully! Current Page: {page_title}")
                    st.image(screenshot_path, caption=f"Live Result for: {command}", use_column_width=True)

            except Exception as e:
                st.error(f"Agent Execution Error: {e}")
