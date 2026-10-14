import streamlit as st
from playwright.sync_api import sync_playwright
import os
import time

if "browser_installed" not in st.session_state:
    try:
        os.system("playwright install chromium")
    except:
        pass
    st.session_state.browser_installed = True

st.set_page_config(page_title="NotRa Live Project Agent", page_icon="🤖", layout="wide")

st.title("🤖 NotRa Live Project Agent")
st.caption("🟢 Bulletproof Auto-Recovery Session + Manual Refresh")

# Bulletproof safe session manager (Auto-recreates browser if connection closes)
def get_safe_page():
    try:
        if "browser" in st.session_state and "page" in st.session_state:
            # Test if connection is still alive
            _ = st.session_state.page.url
            return st.session_state.page
    except Exception:
        pass
    
    # Re-initialize cleanly if closed or dead
    try:
        if "p" in st.session_state:
            try: st.session_state.p.stop()
            except: pass
        
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        
        st.session_state.p = p
        st.session_state.browser = browser
        st.session_state.page = page
        return page
    except Exception as e:
        st.error(f"Browser init error: {e}")
        return None

task_command = st.text_input("Enter command for NotRa (e.g., 'open youtube and play first video', 'scroll down'):")

if st.button("Execute Task"):
    if not task_command:
        st.warning("Please enter a command first!")
    else:
        status_box = st.empty()
        status_box.info(f"🚀 NotRa is executing: '{task_command}'...")
        
        try:
            page = get_safe_page()
            if not page:
                st.error("Failed to connect browser session. Please try again.")
                st.stop()

            cmd = task_command.lower()

            if "http" in cmd or ".gd" in cmd or ".com" in cmd or ".net" in cmd:
                words = task_command.split()
                url = next((w for w in words if w.startswith("http") or "." in w), "")
                if url:
                    if not url.startswith("http"): url = "https://" + url
                    page.goto(url)
                    page.wait_for_timeout(3000)

            elif "youtube" in cmd or "yt" in cmd or "play" in cmd or "video" in cmd:
                if "youtube.com" not in page.url:
                    page.goto("https://www.youtube.com")
                    page.wait_for_timeout(2000)
                
                q = cmd.replace("go to", "").replace("search", "").replace("on youtube", "").replace("youtube", "").replace("yt", "").replace("play", "").replace("video", "").strip()
                if q and len(q) > 2:
                    try:
                        page.fill('input[name="search_query"]', q)
                    except:
                        page.keyboard.type(q)
                    page.keyboard.press('Enter')
                    page.wait_for_timeout(3000)
                
                try:
                    page.locator('ytd-video-renderer #video-title').first.click()
                    page.wait_for_timeout(3000)
                except:
                    pass

            elif "scroll" in cmd:
                page.mouse.wheel(0, 800)
                page.wait_for_timeout(2000)
            else:
                page.keyboard.type(task_command)
                page.wait_for_timeout(2000)

            status_box.success("Task executed successfully!")

        except Exception as e:
            status_box.error(f"Execution Error: {e}")

# Live Stream Window Display with Manual Refresh Button
st.subheader("📺 Live Browser Window Stream")
if st.button("🔄 Refresh Live View"):
    st.rerun()

try:
    page = get_safe_page()
    if page:
        current_url = page.url
        screenshot_bytes = page.screenshot(type="png", full_page=False)
        st.image(screenshot_bytes, caption=f"Current Live View | URL: {current_url}", use_container_width=True)
    else:
        st.info("Run a task to initialize the live browser window.")
except Exception as e:
    st.info("Click 'Execute Task' or 'Refresh Live View' to load browser stream.")
    
