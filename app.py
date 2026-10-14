import streamlit as st
from playwright.sync_api import sync_playwright
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os
import requests

# Install playwright chromium automatically if missing
if "browser_installed" not in st.session_state:
    try:
        os.system("playwright install chromium")
    except:
        pass
    st.session_state.browser_installed = True

st.set_page_config(page_title="NotRa Browser Agent", page_icon="🌐", layout="centered")

st.title("🌐 NotRa Autonomous Browser Agent")
st.caption("🟢 Powered by local Qwen-0.5B model")

@st.cache_resource
def load_parser_model():
    model_name = "Qwen/Qwen2.5-0.5B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True
    )
    return tokenizer, model

tokenizer, model = load_parser_model()

def parse_command_locally(command):
    try:
        messages = [
            {"role": "system", "content": "You are a browser command parser. Extract the clean search query or URL from the user command. Output only the core keyword."},
            {"role": "user", "content": command}
        ]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer([text], return_tensors="pt")
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=30, temperature=0.3, do_sample=True)
        res = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)
        return res.strip()
    except Exception as e:
        print(f"Parser error: {e}")
        return command

command = st.text_input("Enter command (e.g., 'go to youtube and search Patar bashori'):")

if st.button("Execute Command"):
    if not command:
        st.warning("Please enter a command first!")
    else:
        with st.spinner(f"NotRa local Qwen is analyzing & executing: '{command}'..."):
            try:
                parsed_query = parse_command_locally(command)
                
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()

                    if "youtube" in command.lower() or "yt" in command.lower():
                        page.goto("https://www.youtube.com")
                        q = command.lower().replace("go to youtube", "").replace("search", "").replace("on youtube", "").replace("youtube", "").strip()
                        if not q: q = parsed_query
                        page.fill('input[name="search_query"]', q)
                        page.press('input[name="search_query"]', 'Enter')
                        page.wait_for_timeout(4000)
                    elif "http" in command.lower() or ".gd" in command.lower() or ".com" in command.lower():
                        words = command.split()
                        target_url = next((w for w in words if w.startswith("http") or "." in w), "https://google.com")
                        if not target_url.startswith("http"):
                            target_url = "https://" + target_url
                        page.goto(target_url)
                        page.wait_for_timeout(3000)
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
                
