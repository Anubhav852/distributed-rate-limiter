from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from src.api.routes import router as api_router
from src.middleware.rate_limiter import RateLimitMiddleware

app = FastAPI(title="Elite Enterprise Suite")
app.add_middleware(RateLimitMiddleware)
app.include_router(api_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html id="html" class="dark">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    </head>
    <body class="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-200 p-8">
        <div class="max-w-6xl mx-auto space-y-6">
            <div class="flex justify-between items-center">
                <h1 class="text-3xl font-bold">Enterprise Control Center</h1>
                <button id="theme-btn" class="px-4 py-2 bg-blue-600 text-white rounded">Toggle Theme</button>
            </div>
            <div class="grid grid-cols-3 gap-6">
                <div class="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-700">
                    <h2 class="font-bold">CPU Load</h2>
                    <div id="cpu" class="text-3xl text-blue-500">0%</div>
                </div>
                <div class="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-700">
                    <h2 class="font-bold mb-2">Limit Capacity</h2>
                    <input type="number" id="limit-val" value="10" class="w-full p-2 bg-slate-100 dark:bg-slate-800 rounded text-black dark:text-white">
                    <button id="apply-btn" class="w-full mt-2 bg-blue-600 text-white p-2 rounded">Apply</button>
                </div>
                <div class="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-700">
                    <canvas id="chart"></canvas>
                </div>
            </div>
            <div class="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-700">
                <h2 class="font-bold mb-4">Audit Trail (Real-Time Logs)</h2>
                <div id="logs" class="h-40 overflow-y-auto font-mono text-xs text-red-500 space-y-1"></div>
            </div>
        </div>
        <script>
            document.getElementById('theme-btn').onclick = () => document.getElementById('html').classList.toggle('dark');
            document.getElementById('apply-btn').onclick = async () => {
                await axios.post('/api/config/limit?limit=' + document.getElementById('limit-val').value);
                alert('Limit Updated');
            };
            const chart = new Chart(document.getElementById('chart'), {
                type: 'line',
                data: { labels: Array(20).fill(''), datasets: [{ label: 'CPU', data: Array(20).fill(0), borderColor: '#3b82f6' }] },
                options: { scales: { y: { min: 0, max: 100 } } }
            });
            const ws = new WebSocket('ws://' + window.location.host + '/api/ws/status');
            ws.onmessage = (e) => {
                const msg = JSON.parse(e.data);
                if(msg.type === 'stats') {
                    document.getElementById('cpu').innerText = msg.data.cpu + '%';
                    chart.data.datasets[0].data.push(msg.data.cpu);
                    chart.data.datasets[0].data.shift();
                    chart.update();
                } else if(msg.type === 'log') {
                    document.getElementById('logs').innerHTML = `<div>` + msg.data + `</div>` + document.getElementById('logs').innerHTML;
                }
            };
        </script>
    </body>
    </html>
    """