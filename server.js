const express = require('express');
const axios = require('axios');
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

// Optimized Fast Ping for Streamlit & Web Apps
async function simulateUserVisit(monitor) {
  const startTime = Date.now();

  // If it's a Streamlit app, target its internal health check endpoint for guaranteed UP status
  let targetUrl = monitor.url;
  if (targetUrl.includes('streamlit.app') && !targetUrl.includes('_stcore/health')) {
    targetUrl = targetUrl.endsWith('/') ? `${targetUrl}_stcore/health` : `${targetUrl}/_stcore/health`;
  }

  try {
    const response = await axios.get(targetUrl, {
      headers: {
        'User-Agent': 'NotRa-Uptime-Bot/1.0 (+https://notra-uptime.onrender.com)'
      },
      timeout: 15000
    });
    
    const responseTime = Date.now() - startTime;
    
    monitor.status = 'UP';
    monitor.statusCode = response.status;
    monitor.lastChecked = new Date().toLocaleTimeString();
    monitor.responseTime = `${responseTime}ms`;

  } catch (error) {
    console.error(`Ping failed for ${monitor.url}:`, error.message);
    monitor.status = 'DOWN';
    monitor.statusCode = error.response ? error.response.status : 'ERR';
    monitor.lastChecked = new Date().toLocaleTimeString();
    monitor.responseTime = 'N/A';
  } finally {
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
