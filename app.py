import os
import re
import requests
import asyncio
import streamlit as st
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from playwright.async_api import async_playwright

# Bot Token provided by Ramim
BOT_TOKEN = "8718050320:AAEMSjaDMAZttACJwEXgMM-bXBtvkhdVEkc"

# Ensure playwright chromium is installed
if not os.path.exists("/tmp/playwright_installed"):
    try:
        os.system("playwright install chromium")
        with open("/tmp/playwright_installed", "w") as f:
            f.write("installed")
    except:
        pass

# Streamlit Page Config
st.set_page_config(page_title="NotRa Telegram Agent", page_icon="🤖")

st.title("🤖 NotRa Telegram Browser Agent Server")
st.success("🟢 Bot is actively running on Telegram! You can close this tab or keep it open.")
st.markdown("👉 **Click here to talk to your bot:** [@Notra_aibot](https://t.me/Notra_aibot)")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "history" not in context.user_data:
        context.user_data["history"] = []
    
    keyboard = [
        [InlineKeyboardButton("🤖 Open NotRa Bot", url="https://t.me/Notra_aibot")],
        [InlineKeyboardButton("🔍 Google Search", callback_data="cmd_search"),
         InlineKeyboardButton("🌐 Open Website", callback_data="cmd_open")],
        [InlineKeyboardButton("🎵 YouTube Search", callback_data="cmd_yt_search"),
         InlineKeyboardButton("▶️ Play YT Video", callback_data="cmd_yt_play")],
        [InlineKeyboardButton("🖱️ Scroll & Touch", callback_data="cmd_scroll"),
         InlineKeyboardButton("🧠 View Memory", callback_data="cmd_memory")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = (
        "🤖 **Welcome to NotRa Telegram Browser Agent!**\n"
        "🟢 Built and Owned exclusively by Ramim\n\n"
        "🧠 **TG Memory Active:** Apnar shob ager task ebong history Telegram memory-te save thakbe!\n"
        "📱 **Touch & Scroll:** Jekono page-e giye scroll ba touch/click korte parbe.\n\n"
        "Niche command select karo ba direct likhe pathao!\n"
        "Example: `open github.com`, `scroll down`, ba `click sign in`"
    )
    await update.message.reply_text(welcome_msg, parse_mode="Markdown", reply_markup=reply_markup)

async def view_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history = context.user_data.get("history", [])
    if not history:
        msg = "🧠 **NotRa Memory:** Kono purono task memory te save ney."
    else:
        msg = "🧠 **NotRa User Memory (Last Tasks):**\n\n"
        for idx, item in enumerate(history[-5:], 1):
            msg += f"{idx}. Command: `{item['command']}`\n   URL: {item['url']}\n"
    
    if update.callback_query:
        await update.callback_query.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text(msg, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data == "cmd_search":
        await query.message.reply_text("💡 Type search query like: `search python programming`")
    elif data == "cmd_open":
        await query.message.reply_text("💡 Type website to open like: `open github.com`")
    elif data == "cmd_yt_search":
        await query.message.reply_text("💡 Type YouTube search like: `search on youtube lofi music`")
    elif data == "cmd_yt_play":
        await query.message.reply_text("💡 Type YouTube play like: `play lofi on youtube`")
    elif data == "cmd_scroll":
        await query.message.reply_text("💡 Type scroll or touch command like: `scroll down` or `click login`")
    elif data == "cmd_memory":
        await view_memory(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_command = update.message.text.strip()
    chat_id = update.message.chat_id
    
    if "history" not in context.user_data:
        context.user_data["history"] = []
    
    status_msg = await update.message.reply_text("⏳ NotRa is executing your command using TG Memory...")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
            )

            browser_context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await browser_context.new_page()

            cmd = task_command.lower()

            # URL Extraction
            url_match = re.search(r'(https?://[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', task_command)
            target_url = None
            if url_match:
                matched_str = url_match.group(0).rstrip(".,!?;'")
                if not matched_str.startswith("http"):
                    target_url = "https://" + matched_str
                else:
                    target_url = matched_str

            # If user wants to continue on current page or start fresh
            if "youtube" in cmd or "yt" in cmd or "play" in cmd or "video" in cmd:
                await page.goto("https://www.youtube.com", wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)

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
                    await page.fill('input[name="search_query"]', q)
                    await page.keyboard.press('Enter')
                    await page.wait_for_timeout(3500)
                except:
                    pass

                if "play" in cmd or "video" in cmd:
                    try:
                        videos = page.locator('ytd-video-renderer a#video-title')
                        count = await videos.count()
                        clicked = False
                        for i in range(min(count, 4)):
                            try:
                                await videos.nth(i).click(force=True)
                                await page.wait_for_timeout(4000)
                                clicked = True
                                break
                            except:
                                continue
                        if not clicked and count > 0:
                            await videos.first.click(force=True)
                            await page.wait_for_timeout(4000)
                    except:
                        pass

            elif target_url and not ("search" in cmd and "google" in cmd):
                try:
                    await page.goto(target_url, wait_until="domcontentloaded", timeout=25000)
                    await page.wait_for_timeout(2500)
                except Exception as e:
                    await status_msg.edit_text(f"⚠️ Could not load `{target_url}`. Domain offline or connection error.")
                    await browser.close()
                    return

            else:
                # Check if it's a direct scroll or touch/click command without new URL
                if "scroll" in cmd or "click" in cmd:
                    # If history has a previous URL, open it first
                    history = context.user_data.get("history", [])
                    last_url = history[-1]["url"] if history else "https://www.google.com"
                    await page.goto(last_url, wait_until="domcontentloaded", timeout=25000)
                    await page.wait_for_timeout(2000)
                else:
                    clean_q = (cmd.replace("search on google", "")
                                  .replace("google", "")
                                  .replace("search", "")
                                  .replace("open", "")
                                  .replace("find", "")
                                  .strip())
                    if not clean_q: clean_q = task_command

                    google_url = f"https://www.google.com/search?q={requests.utils.quote(clean_q)}"
                    await page.goto(google_url, wait_until="domcontentloaded", timeout=25000)
                    await page.wait_for_timeout(2000)

                    if "open website" in cmd or "go to site" in cmd or "make an account" in cmd:
                        try:
                            await page.locator('h3').first.click(force=True)
                            await page.wait_for_timeout(3000)
                        except:
                            pass

            # --- Scroll & Touch Interaction Engine ---
            if "scroll down" in cmd:
                await page.mouse.wheel(0, 800)
                await page.wait_for_timeout(1500)
            elif "scroll up" in cmd:
                await page.mouse.wheel(0, -800)
                await page.wait_for_timeout(1500)

            if "click" in cmd:
                click_words = cmd.split("click")[-1].strip()
                if click_words:
                    try:
                        await page.get_by_text(click_words, exact=False).first.click(force=True, timeout=5000)
                        await page.wait_for_timeout(2500)
                    except:
                        pass

            current_url = page.url
            
            # Save to Telegram User Memory
            context.user_data["history"].append({
                "command": task_command,
                "url": current_url
            })
            
            # Screenshot Capture & Send to Telegram
            img_path = f"telegram_shot_{chat_id}.png"
            await page.screenshot(path=img_path, full_page=False)
            await browser.close()

            with open(img_path, "rb") as photo:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=f"✅ **Task Executed Successfully!**\n🌐 **URL:** {current_url}\n🧠 Memory updated in TG Chat!"
                )
            await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ Execution Error: {str(e)}")

# Background runner for Streamlit without Signal Handler crash
@st.cache_resource
def run_telegram_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("memory", view_memory))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    app.run_polling(stop_signals=None)

# Start Bot in Streamlit Instance
run_telegram_bot()
