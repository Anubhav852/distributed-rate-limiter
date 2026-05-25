from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.api.routes import router as api_router
from src.middleware.rate_limiter import rate_limit_middleware

app = FastAPI(title="Elite Enterprise API")
app.add_middleware(BaseHTTPMiddleware, dispatch=rate_limit_middleware)
app.include_router(api_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body class="bg-slate-950 text-slate-200 p-10">
        <div id="toast" class="fixed top-5 right-5 hidden p-4 bg-red-600 rounded shadow-lg text-white font-bold">ALERT: Rate Limit Exceeded!</div>
        <div class="max-w-6xl mx-auto">
            <h1 class="text-4xl font-bold mb-10 text-white">Enterprise Control Center</h1>
            <div class="grid grid-cols-2 gap-8">
                <div class="bg-slate-900 p-8 rounded-2xl border border-slate-700">
                    <h2 class="text-xl mb-4">Live Throughput</h2>
                    <div id="counter" class="text-8xl font-mono">10</div>
                </div>
                <div class="bg-slate-900 p-8 rounded-2xl border border-slate-700">
                    <canvas id="trafficChart"></canvas>
                </div>
            </div>
        </div>
        <script>
            function triggerAlert() {
                const t = document.getElementById('toast');
                t.classList.remove('hidden');
                setTimeout(() => t.classList.add('hidden'), 3000);
            }
            const chart = new Chart(document.getElementById('trafficChart'), {
                type: 'line',
                data: { labels: Array(20).fill(''), datasets: [{ data: Array(20).fill(10), borderColor: '#3b82f6', fill: true }] },
                options: { responsive: true }
            });
            const ws = new WebSocket('ws://' + window.location.host + '/api/ws/status');
            ws.onmessage = (e) => {
                const data = JSON.parse(e.data);
                document.getElementById('counter').innerText = data.remaining;
                if(data.remaining < 2) triggerAlert();
                chart.data.datasets[0].data.push(data.remaining);
                chart.data.datasets[0].data.shift();
                chart.update();
            };
        </script>
    </body>
    </html>
    """