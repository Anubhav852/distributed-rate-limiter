# 🚀 Enterprise Rate Limiter & Monitoring Suite

[![Status](https://img.shields.io/badge/status-production--ready-green.svg)]()

## Live Demo

Try the live Distributed Rate Limiter dashboard on Render: [https://distributed-rate-limiter-1qtt.onrender.com](https://distributed-rate-limiter-1qtt.onrender.com).

### Test it

- Select **Send 1** to send a real request through the FastAPI rate-limiting middleware.
- Select **Burst 20** to send 20 requests quickly. Requests within the current per-client limit are allowed; excess requests receive HTTP 429 and appear as blocked events in the live feed.
- The dashboard shows request totals, allowed and blocked traffic, recent events, and server CPU and memory.
- Use **Reset my quota** to clear the current browser client's rate-limit counter. The global limit can be changed from the dashboard.

The hosted app uses Render Key Value for shared rate-limit counters and dashboard statistics. The demo may take a little time to respond after the service has been idle.

The **Enterprise Rate Limiter & Monitoring Suite** is a high-concurrency, distributed API management solution. It provides granular rate control via Redis and real-time system observability, designed for engineers who need to monitor API health and throughput in mission-critical environments.

---

## 🏗️ System Architecture
The suite utilizes an event-driven architecture, separating the request-handling pipeline from the real-time observability bus.

```mermaid
graph LR
    User -->|API Request| FastAPI
    FastAPI -->|Check Limit| Redis
    Redis -->|Atomic Count| FastAPI
    FastAPI -->|Stream Stats| WebSockets
    WebSockets -->|Live Data| Dashboard
    FastAPI -->|Log 429| AuditTrail
```

## Components:
API Gateway Layer (FastAPI): Handles incoming requests and enforces policy via middleware.

State Engine (Redis): Manages atomic counters via Lua scripts for thread-safe rate enforcement.

Telemetry Bus (WebSockets): Streams server-side health metrics (psutil) to the dashboard.

Audit Layer: Captures and logs 429 Too Many Requests status codes for forensic analysis.

## Key Capabilities
Atomic Rate Enforcement: Eliminates "race conditions" common in standard rate limiters by utilizing Redis-Lua atomicity.

Real-time Observability: A live-updating dashboard visualizing CPU and memory pressure.

Forensic Audit Trail: Real-time logging of blocked requests, allowing for instant identification of API abuse.

Dynamic Configuration: Adjust global API rate limits in real-time without server restarts.

Modern UI: Responsive, Tailwind-powered interface with persistent Dark/Light mode.

## Getting Started
1. Prerequisites
Redis Server: Ensure redis-server is installed and active on localhost:6379.

Python: Version 3.11+.

2. Installation
PowerShell
# Initialize and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install core dependencies
pip install fastapi uvicorn redis pydantic-settings psutil
3. Execution
Launch the production-ready server:

PowerShell
python -m uvicorn src.main:app --reload
Access the Enterprise Control Center at http://127.0.0.1:8000.

## Monitoring & Audit Logs
The dashboard is split into three functional panes:

System Health: Real-time CPU monitoring to detect resource exhaustion.

Configuration: Global limit management.

Audit Trail: An append-only log of all triggered rate limits, providing immediate visual feedback on API traffic anomalies.

 Roadmap
* Multi-node Cluster Support: Extend Redis logic for cross-region synchronization.

* Authentication: Add JWT/OAuth2 for administrative access.

* Persistent Storage: Dump audit logs into PostgreSQL for historical analysis.