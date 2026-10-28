from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from src.api.routes import router as api_router
from src.middleware.rate_limiter import RateLimitMiddleware

app = FastAPI(title="Distributed Rate Limiter")
app.add_middleware(RateLimitMiddleware)
app.include_router(api_router, prefix="/api")

DASHBOARD_HTML = """
<!DOCTYPE html>
<html id="html" class="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rate Limiter Control Center</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>tailwind.config = { darkMode: 'class' }</script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
</head>
<body class="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-200 min-h-screen p-4 md:p-8">
<div class="max-w-6xl mx-auto space-y-5">

  <div class="flex justify-between items-center">
    <div>
      <h1 class="text-2xl md:text-3xl font-bold">Rate Limiter Control Center</h1>
      <div class="text-xs text-slate-500 mt-1 flex items-center gap-2">
        <span id="ws-dot" class="inline-block w-2 h-2 rounded-full bg-slate-500"></span>
        <span id="ws-text">connecting...</span>
        <span>FastAPI + Redis (Lua atomic counters) + WebSockets</span>
      </div>
    </div>
    <button id="theme-btn" class="px-3 py-2 bg-blue-600 text-white rounded text-sm">Toggle Theme</button>
  </div>

  <div id="banner" class="hidden bg-red-600 text-white rounded-xl px-4 py-3 font-semibold"></div>

  <div class="grid grid-cols-2 md:grid-cols-6 gap-3">
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4"><div class="text-xs text-slate-500">Total</div><div id="k-total" class="text-2xl font-bold">0</div></div>
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4"><div class="text-xs text-slate-500">Allowed</div><div id="k-allowed" class="text-2xl font-bold text-emerald-500">0</div></div>
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4"><div class="text-xs text-slate-500">Blocked (429)</div><div id="k-blocked" class="text-2xl font-bold text-red-500">0</div></div>
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4"><div class="text-xs text-slate-500">Block rate</div><div id="k-rate" class="text-2xl font-bold">0%</div></div>
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4"><div class="text-xs text-slate-500">Req / sec (5s avg)</div><div id="k-rps" class="text-2xl font-bold">0</div></div>
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4"><div class="text-xs text-slate-500">Server CPU / MEM</div><div id="k-cpu" class="text-2xl font-bold text-blue-500">0%</div></div>
  </div>

  <div class="grid md:grid-cols-3 gap-5">
    <div class="md:col-span-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4">
      <h2 class="font-bold mb-2">Traffic (last 60 seconds)</h2>
      <div class="h-56"><canvas id="chart"></canvas></div>
    </div>

    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 space-y-3">
      <h2 class="font-bold">Try it live</h2>
      <p class="text-xs text-slate-500">Fires real requests from your browser at <code>/api/resource</code>.</p>
      <div class="flex gap-2">
        <button id="send1" class="flex-1 bg-blue-600 text-white rounded p-2 text-sm">Send 1</button>
        <button id="burst" class="flex-1 bg-red-600 text-white rounded p-2 text-sm">Burst 20</button>
      </div>
      <div>
        <div class="flex justify-between text-xs text-slate-500 mb-1"><span>Your quota</span><span id="quota-text">-</span></div>
        <div class="w-full h-2 bg-slate-200 dark:bg-slate-800 rounded"><div id="quota-bar" class="h-2 bg-emerald-500 rounded" style="width:100%"></div></div>
      </div>
      <div id="last" class="text-xs font-mono text-slate-500">No requests sent yet.</div>
      <button id="reset" class="w-full border border-slate-400 dark:border-slate-600 rounded p-2 text-sm">Reset my quota</button>
      <div class="pt-2 border-t border-slate-200 dark:border-slate-800">
        <div class="text-xs text-slate-500 mb-1">Limit per 60s window</div>
        <div class="flex gap-2">
          <input type="number" id="limit-val" value="10" min="1" max="1000" class="w-full p-2 bg-slate-100 dark:bg-slate-800 rounded text-sm">
          <button id="apply-btn" class="bg-slate-700 text-white rounded px-3 text-sm">Apply</button>
        </div>
        <div id="limit-msg" class="text-xs text-slate-500 mt-1"></div>
      </div>
    </div>
  </div>

  <div class="grid md:grid-cols-3 gap-5">
    <div class="md:col-span-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4">
      <h2 class="font-bold mb-2">Live request feed</h2>
      <div class="flex gap-3 px-2 text-xs text-slate-500 font-mono">
        <span class="w-20">time</span><span class="w-10">code</span><span class="w-32">client</span><span class="flex-1">path</span><span class="w-20">latency</span><span class="w-16">left</span>
      </div>
      <div id="feed" class="h-72 overflow-y-auto font-mono text-xs space-y-1 mt-1">
        <div id="empty" class="text-slate-500 px-2 py-4">Waiting for traffic...</div>
      </div>
    </div>
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4">
      <h2 class="font-bold mb-2">Top offenders (blocked)</h2>
      <div id="offenders" class="space-y-1 text-sm font-mono"></div>
    </div>
  </div>
</div>

<script>
const $ = (id) => document.getElementById(id);
let total = 0, allowed = 0, blocked = 0, secA = 0, secB = 0;
const history = [];
const offenders = {};
const blockTimes = {};
let bannerUntil = 0;

$('theme-btn').onclick = () => $('html').classList.toggle('dark');

// ---------- chart ----------
const chart = new Chart($('chart'), {
  type: 'bar',
  data: {
    labels: Array(60).fill(''),
    datasets: [
      { label: 'Allowed', data: Array(60).fill(0), backgroundColor: '#22c55e', stack: 's' },
      { label: 'Blocked', data: Array(60).fill(0), backgroundColor: '#ef4444', stack: 's' }
    ]
  },
  options: {
    animation: false, responsive: true, maintainAspectRatio: false,
    scales: {
      x: { stacked: true, display: false },
      y: { stacked: true, beginAtZero: true, ticks: { precision: 0 } }
    },
    plugins: { legend: { labels: { color: '#94a3b8' } } }
  }
});

setInterval(() => {
  chart.data.datasets[0].data.push(secA); chart.data.datasets[0].data.shift();
  chart.data.datasets[1].data.push(secB); chart.data.datasets[1].data.shift();
  chart.update('none');
  history.push(secA + secB);
  if (history.length > 5) history.shift();
  $('k-rps').innerText = (history.reduce((a, b) => a + b, 0) / history.length).toFixed(1);
  secA = 0; secB = 0;
  if (bannerUntil && Date.now() > bannerUntil) { $('banner').classList.add('hidden'); bannerUntil = 0; }
}, 1000);

// ---------- rendering ----------
function renderKpis() {
  $('k-total').innerText = total;
  $('k-allowed').innerText = allowed;
  $('k-blocked').innerText = blocked;
  $('k-rate').innerText = (total ? (blocked / total * 100).toFixed(1) : '0') + '%';
}

function renderOffenders() {
  const box = $('offenders');
  box.textContent = '';
  const rows = Object.entries(offenders).sort((a, b) => b[1] - a[1]).slice(0, 5);
  if (!rows.length) {
    const d = document.createElement('div');
    d.className = 'text-slate-500 text-xs';
    d.textContent = 'No blocked clients yet.';
    box.appendChild(d);
    return;
  }
  rows.forEach(([ip, count]) => {
    const row = document.createElement('div');
    row.className = 'flex justify-between';
    const a = document.createElement('span'); a.textContent = ip;
    const b = document.createElement('span'); b.className = 'text-red-500'; b.textContent = count + ' blocked';
    row.appendChild(a); row.appendChild(b);
    box.appendChild(row);
  });
}

function addRow(e) {
  const empty = $('empty'); if (empty) empty.remove();
  const row = document.createElement('div');
  row.className = 'flex gap-3 px-2 py-1 rounded ' + (e.blocked ? 'bg-red-500/10 text-red-500' : 'text-emerald-500');
  const cells = [
    [new Date(e.ts * 1000).toLocaleTimeString(), 'w-20'],
    [String(e.status), 'w-10'],
    [e.ip, 'w-32'],
    [e.path, 'flex-1 truncate'],
    [Number(e.latency_ms).toFixed(1) + ' ms', 'w-20'],
    [String(e.remaining), 'w-16']
  ];
  cells.forEach(([text, cls]) => {
    const s = document.createElement('span');
    s.className = cls; s.textContent = text;
    row.appendChild(s);
  });
  const feed = $('feed');
  feed.prepend(row);
  while (feed.children.length > 60) feed.removeChild(feed.lastChild);
}

function checkIncident(e) {
  if (!e.blocked) return;
  const now = Date.now();
  const arr = (blockTimes[e.ip] || []).filter(t => now - t < 10000);
  arr.push(now);
  blockTimes[e.ip] = arr;
  if (arr.length >= 5) {
    const b = $('banner');
    b.textContent = 'INCIDENT: possible abuse from ' + e.ip + ' (' + arr.length + ' blocked requests in 10s)';
    b.classList.remove('hidden');
    bannerUntil = now + 8000;
  }
}

function handleLive(e) {
  total++;
  if (e.blocked) { blocked++; secB++; offenders[e.ip] = (offenders[e.ip] || 0) + 1; }
  else { allowed++; secA++; }
  addRow(e);
  checkIncident(e);
  renderKpis();
  if (e.blocked) renderOffenders();
}

// ---------- initial state ----------
async function loadStats() {
  try {
    const r = await fetch('/api/stats', { cache: 'no-store' });
    const s = await r.json();
    total = s.total; allowed = s.allowed; blocked = s.blocked;
    $('limit-val').value = s.limit;
    s.offenders.forEach(o => offenders[o.ip] = o.count);
    s.recent.slice().reverse().forEach(addRow);
    renderKpis(); renderOffenders();
  } catch (err) { console.error(err); }
}

// ---------- websocket ----------
function connect() {
  const proto = location.protocol === 'https:' ? 'wss://' : 'ws://';
  const ws = new WebSocket(proto + location.host + '/api/ws/status');
  ws.onopen = () => {
    $('ws-dot').className = 'inline-block w-2 h-2 rounded-full bg-emerald-500';
    $('ws-text').innerText = 'LIVE';
  };
  ws.onclose = () => {
    $('ws-dot').className = 'inline-block w-2 h-2 rounded-full bg-red-500';
    $('ws-text').innerText = 'reconnecting...';
    setTimeout(connect, 2000);
  };
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.type === 'stats') {
      $('k-cpu').innerText = msg.data.cpu + '% / ' + msg.data.mem + '%';
    } else if (msg.type === 'request') {
      handleLive(msg.data);
    }
  };
}

// ---------- try it live ----------
async function hit() {
  try {
    const r = await fetch('/api/resource', { cache: 'no-store' });
    const rem = r.headers.get('X-RateLimit-Remaining');
    const lim = r.headers.get('X-RateLimit-Limit');
    if (rem !== null && lim !== null) {
      $('quota-text').innerText = rem + ' / ' + lim + ' left';
      $('quota-bar').style.width = (Number(rem) / Number(lim) * 100) + '%';
      $('quota-bar').className = 'h-2 rounded ' + (Number(rem) === 0 ? 'bg-red-500' : 'bg-emerald-500');
    }
    return r.status;
  } catch (err) { return 0; }
}

$('send1').onclick = async () => {
  const s = await hit();
  $('last').innerText = 'Last response: HTTP ' + s;
};
$('burst').onclick = async () => {
  const results = await Promise.all(Array.from({ length: 20 }, () => hit()));
  const ok = results.filter(s => s === 200).length;
  const bad = results.filter(s => s === 429).length;
  $('last').innerText = 'Burst of 20: ' + ok + ' allowed, ' + bad + ' blocked (429)';
};
$('reset').onclick = async () => {
  await fetch('/api/demo/reset', { method: 'POST' });
  $('quota-text').innerText = '-';
  $('quota-bar').style.width = '100%';
  $('quota-bar').className = 'h-2 bg-emerald-500 rounded';
  $('last').innerText = 'Your quota was reset.';
};
$('apply-btn').onclick = async () => {
  const v = $('limit-val').value;
  const r = await fetch('/api/config/limit?limit=' + encodeURIComponent(v), { method: 'POST' });
  $('limit-msg').innerText = r.ok ? 'Limit set to ' + v + '. Click "Reset my quota" to apply it immediately.' : 'Invalid limit (1-1000).';
};

loadStats().then(connect);
</script>
</body>
</html>
"""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def root():
    return DASHBOARD_HTML