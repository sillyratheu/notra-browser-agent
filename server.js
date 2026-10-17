const express = require('express');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 3000;

const TARGET_URL = process.env.TARGET_URL || 'https://notyourpcoooo.streamlit.app';

let lastStatus = {
  status: 'PENDING',
  lastChecked: 'Not checked yet',
  responseTime: 'N/A'
};

async function pingStreamlitApp() {
  const startTime = Date.now();
  console.log(`[${new Date().toLocaleTimeString()}] Pinging Streamlit VNC PC...`);

  try {
    // Send lightweight HTTP GET request with maxRedirects allowed to avoid loop error
    await axios.get(TARGET_URL, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) StreamlitKeeper/1.0'
      },
      maxRedirects: 5,
      timeout: 15000
    });

    const duration = Date.now() - startTime;
    lastStatus = {
      status: 'ACTIVE 24/7',
      lastChecked: new Date().toLocaleTimeString(),
      responseTime: `${duration}ms`
    };

    console.log(`[SUCCESS] Pinged Streamlit successfully in ${duration}ms!`);

  } catch (error) {
    console.error(`[ERROR] Failed to ping Streamlit app:`, error.message);
    lastStatus = {
      status: 'ERROR',
      lastChecked: new Date().toLocaleTimeString(),
      responseTime: 'N/A'
    };
  }
}

// Run ping every 2 minutes
setInterval(pingStreamlitApp, 2 * 60 * 1000);

// Run initial ping 3 seconds after boot up
setTimeout(pingStreamlitApp, 3000);

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
