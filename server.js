const express = require('express');
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;
const DATA_FILE = path.join(__dirname, 'monitors.json');

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Load stored monitors
function loadMonitors() {
  if (fs.existsSync(DATA_FILE)) {
    try {
      const data = fs.readFileSync(DATA_FILE, 'utf8');
      return JSON.parse(data);
    } catch (err) {
      console.error("Error reading data file:", err);
      return [];
    }
  }
  return [];
}

// Save monitors to JSON file
function saveMonitors(monitors) {
  try {
    fs.writeFileSync(DATA_FILE, JSON.stringify(monitors, null, 2), 'utf8');
  } catch (err) {
    console.error("Error saving data file:", err);
  }
}

let monitors = loadMonitors();

// Real user simulation using Puppeteer
async function simulateUserVisit(monitor) {
  let browser = null;
  try {
    const startTime = Date.now();

    // Launch lightweight Puppeteer browser instance
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
    
    // Set standard viewport and realistic User-Agent
    await page.setViewport({ width: 1280, height: 800 });
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36');

    // 1. Visit the web app URL
    await page.goto(monitor.url, { waitUntil: 'networkidle2', timeout: 45000 });

    // 2. Simulate human scroll action
    await page.evaluate(() => {
      window.scrollBy(0, 300);
    });
    await new Promise(r => setTimeout(r, 1500));

    // 3. Simulate click interaction on page body
    await page.mouse.click(200, 200);
    await new Promise(r => setTimeout(r, 1500));

    const responseTime = Date.now() - startTime;
    
    monitor.status = 'UP';
    monitor.statusCode = 200;
    monitor.lastChecked = new Date().toLocaleTimeString();
    monitor.responseTime = `${responseTime}ms`;

  } catch (error) {
    console.error(`Simulation failed for ${monitor.url}:`, error.message);
    monitor.status = 'DOWN';
    monitor.statusCode = 'ERR';
    monitor.lastChecked = new Date().toLocaleTimeString();
    monitor.responseTime = 'N/A';
  } finally {
    if (browser) {
      await browser.close(); // Always close browser to free RAM
    }
    saveMonitors(monitors);
  }
}

// Timer check for intervals
setInterval(() => {
  const now = Date.now();
  monitors.forEach(monitor => {
    const intervalMs = monitor.interval * 60 * 1000;
    if (!monitor.lastCheckedTime || (now - monitor.lastCheckedTime >= intervalMs)) {
      monitor.lastCheckedTime = now;
      simulateUserVisit(monitor);
    }
  });
}, 10000);

// API Routes
app.get('/api/monitors', (req, res) => {
  res.json(monitors);
});

app.post('/api/monitors', (req, res) => {
  const { name, url, interval } = req.body;
  if (!name || !url || !interval) {
    return res.status(400).json({ error: 'All fields are required!' });
  }

  const parsedInterval = Math.max(1, Math.min(60, parseInt(interval)));
  
  const newMonitor = {
    id: Date.now().toString(),
    name,
    url,
    interval: parsedInterval,
    status: 'PENDING',
    statusCode: '-',
    lastChecked: 'Not checked yet',
    responseTime: '-'
  };

  monitors.push(newMonitor);
  saveMonitors(monitors);
  simulateUserVisit(newMonitor);
  res.status(201).json(newMonitor);
});

app.delete('/api/monitors/:id', (req, res) => {
  monitors = monitors.filter(m => m.id !== req.params.id);
  saveMonitors(monitors);
  res.json({ success: true });
});

app.listen(PORT, () => {
  console.log(`NotRa Uptime is running on port ${PORT}`);
});
