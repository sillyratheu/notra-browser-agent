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

st.set_page_config(page_title="NotRa Live Project Agent", page_icon="🤖", layout="wide")

st.title("🤖 NotRa Live Project Agent")
st.caption("🟢 Smart understanding + Persistent session + Live refreshing window stream")

# Initialize persistent browser session in Streamlit session_state
if "playwright_active" not in st.session_state:
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()
    
    st.session_state.p = p
    st.session_state.browser = browser
    st.session_state.context = context
    st.session_state.page = page
    st.session_state.playwright_active = True

page = st.session_state.page

# Sidebar controls for project session
with st.sidebar:
    st.header("📂 Project Session Hub")
    st.markdown("Session active thakbe. Poroborti command age-er state thekei kaj korbe.")
    if st.button("🔄 Reset Project Session"):
        try:
            st.session_state.browser.close()
            st.session_state.p.stop()
        except:
            pass
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Session reset done! Please refresh page.")
        st.rerun()

# Main Command Box
task_command = st.text_input("Enter command for NotRa (e.g., 'open youtube and play first video', 'scroll down'):")

if st.button("Execute Task"):
    if not task_command:
        st.warning("Please enter a command first!")
    else:
        status_box = st.empty()
        
        # Phase 1: Understanding command first
        status_box.info("🧠 NotRa is understanding your command...")
        time.sleep(1) # Simulation of thinking/understanding phase
        
        try:
            cmd = task_command.lower()
            status_box.info(f"🚀 NotRa is executing: '{task_command}'...")

            # Navigation / Action logic based on persistent state
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
                
                # Automatically click the first video if requested
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

            # Phase 2: Live Refreshing Window Stream (Single slot updating every 3 seconds)
            st.subheader("📺 Live Browser Window Stream")
            image_placeholder = st.empty() # Dynamic slot that updates every 3 seconds

            for i in range(5):
                page.wait_for_timeout(3000) # Wait 3 seconds
                current_url = page.url
                ss_path = f"live_frame_{time.time()}.png"
                page.screenshot(path=ss_path, full_page=False)
                
                # Replace the image in real-time like a live stream frame
                image_placeholder.image(ss_path, caption=f"Live View - Step {i+1}/5 | URL: {current_url}", use_column_width=True)
                status_box.info(f"NotRa is working... Live frame updated ({i+1}/5)")

            status_box.success("Task done Boss! 🎉 NotRa has successfully executed your command.")

        except Exception as e:
            status_box.error(f"Execution Error: {e}")
    
