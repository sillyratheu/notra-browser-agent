import streamlit as st
from playwright.sync_api import sync_playwright
import os
import requests

# Ensure playwright chromium is installed
if "browser_installed" not in st.session_state:
    try:
        os.system("playwright install chromium")
    except:
        pass
    st.session_state.browser_installed = True

st.set_page_config(page_title="NotRa Browser Agent", page_icon="🌐", layout="centered")

st.title("🌐 NotRa Autonomous Browser Agent")
st.caption("🟢 Universal AI Browser Automation")

command = st.text_input("Enter any command (e.g., 'search Patar bashori on YouTube', 'open ramims.work.gd', etc.):")

if st.button("Execute Command"):
    if not command:
        st.warning("Please enter a command first!")
    else:
        with st.spinner(f"NotRa is executing: '{command}'..."):
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page(viewport={"width": 1280, "height": 800})

                    cmd_lower = command.lower()

                    # 1. Handle URL / Website opening directly
                    if "http" in cmd_lower or ".gd" in cmd_lower or ".com" in cmd_lower or ".net" in cmd_lower or ".org" in cmd_lower:
                        words = command.split()
                        target_url = next((w for w in words if w.startswith("http") or "." in w), "https://google.com")
                        if not target_url.startswith("http"):
                            target_url = "https://" + target_url
                        page.goto(target_url)
                        page.wait_for_timeout(3000)

                    # 2. Handle YouTube Search automatically
                    elif "youtube" in cmd_lower or "yt" in cmd_lower or "play" in cmd_lower:
                        page.goto("https://www.youtube.com")
                        page.wait_for_timeout(2000)
                        
                        # Extract search query intelligently
                        q = cmd_lower.replace("go to", "").replace("search", "").replace("on youtube", "").replace("youtube", "").replace("yt", "").replace("play", "").strip()
                        if not q:
                            q = "trending"
                        
                        try:
                            # Try multiple possible YouTube search input selectors
                            page.fill('input[name="search_query"]', q)
                        except:
                            try:
                                page.fill('input#search', q)
                            except:
                                page.keyboard.type(q)
                                
                        page.keyboard.press('Enter')
                        page.wait_for_timeout(4000)

                    # 3. Handle any general search or task via Google
                    else:
                        page.goto(f"https://www.google.com/search?q={requests.utils.quote(command)}")
                        page.wait_for_timeout(3000)

                    page_title = page.title()
                    screenshot_path = "screenshot.png"
                    page.screenshot(path=screenshot_path, full_page=False)
                    browser.close()

                    st.success(f"Successfully executed! Page Title: {page_title}")
                    st.image(screenshot_path, caption=f"Live view for: {command}", use_column_width=True)

            except Exception as e:
                st.error(f"Execution Error: {e}")
                    
