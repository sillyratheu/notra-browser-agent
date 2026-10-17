const express = require('express');
const puppeteer = require('puppeteer');

const app = express();
const PORT = process.env.PORT || 3000;

// Set your Streamlit VNC App URL here
const TARGET_URL = process.env.TARGET_URL || 'https://notyourpcoooo.streamlit.app';

let lastStatus = {
  status: 'PENDING',
  lastChecked: 'Not checked yet',
  responseTime: 'N/A'
};

async function visitStreamlitApp() {
  let browser = null;
  const startTime = Date.now();
  console.log(`[${new Date().toLocaleTimeString()}] Visiting Streamlit VNC PC...`);

  try {
    // Ultra-lightweight Chrome flags optimized for Render's 512MB RAM
    browser = await puppeteer.launch({
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--disable-gpu',
        '--no-first-run',
        '--no-zygote',
        '--single-process'
      ]
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 720 });
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36');

    // 1. Open Streamlit VNC App
    await page.goto(TARGET_URL, { waitUntil: 'networkidle2', timeout: 45000 });

    // 2. Simulate User Interaction (Scroll down)
    await page.evaluate(() => {
      window.scrollBy(0, 200);
    });
    await new Promise(resolve => setTimeout(resolve, 1500));

    // 3. Simulate User Interaction (Click on page)
    await page.mouse.click(150, 150);
    await new Promise(resolve => setTimeout(resolve, 1500));

    const duration = Date.now() - startTime;
    lastStatus = {
      status: 'ACTIVE 24/7',
      lastChecked: new Date().toLocaleTimeString(),
      responseTime: `${duration}ms`
    };

    console.log(`[SUCCESS] Visited and interacted with Streamlit VNC PC successfully in ${duration}ms!`);

  } catch (error) {
    console.error(`[ERROR] Failed to visit Streamlit app:`, error.message);
    lastStatus = {
      status: 'ERROR',
      lastChecked: new Date().toLocaleTimeString(),
      responseTime: 'N/A'
    };
  } finally {
    if (browser) {
      await browser.close(); // Crucial: Free memory immediately
    }
  }
}

// Run user simulation every 2 minutes (120,000 ms)
setInterval(visitStreamlitApp, 2 * 60 * 1000);

// Run initial visit 5 seconds after boot up
setTimeout(visitStreamlitApp, 5000);

// Dashboard / Health Check Endpoint
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Streamlit Keeper Service</title>
      <style>
        body { font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 40px; text-align: center; }
        .card { background: #1e293b; padding: 30px; border-radius: 12px; display: inline-block; max-width: 500px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        h1 { color: #38bdf8; font-size: 1.8rem; }
        .status { padding: 8px 16px; border-radius: 6px; font-weight: bold; background: #166534; color: #4ade80; display: inline-block; margin: 10px 0; }
        p { margin: 8px 0; color: #94a3b8; }
        a { color: #38bdf8; text-decoration: none; word-break: break-all; }
      </style>
    </head>
    <body>
      <div class="card">
        <h1>🚀 Streamlit PC Keeper</h1>
        <p>Target App: <a href="${TARGET_URL}" target="_blank">${TARGET_URL}</a></p>
        <div class="status">${lastStatus.status}</div>
        <p><strong>Last Check:</strong> ${lastStatus.lastChecked}</p>
        <p><strong>Response Time:</strong> ${lastStatus.responseTime}</p>
      </div>
    </body>
    </html>
  `);
});

app.listen(PORT, () => {
  console.log(`Keeper Service is running on port ${PORT}`);
});
