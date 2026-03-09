# Resilient Micro-Hub Orchestrator

The **Resilient Micro-Hub Orchestrator** is an advanced Agentic BTM (Behind-the-Meter) energy management platform designed to solve the "Deployment Deadlock" for modular housing infrastructure. 

By intelligently orchestrating dynamic robotic factory loads, massive utility-scale Battery Energy Storage Systems (BESS), and firm localized generation (like micro-nuclear or long-duration storage) using an AI Agent, this platform maximizes arbitrage yield while guaranteeing factory life-support operations during grid emergencies.

## 🌟 Key Features

*   **Live Grid Telemetry:** Real-time ingestion of ERCOT Locational Marginal Pricing (LMP) and NYISO grid constraint signals.
*   **LangGraph Agentic Trading Engine:** Replaces hardcoded `if/else` logic with a stateful AI agent that generates unified Energy Bid-Offer Curves (EBOC), deciding when to perform energy arbitrage vs. when to prioritize cheap factory production.
*   **Flexible Load Orchestration:** Dynamically profiles and throttles robotic manufacturing lines ("Raise the Roof") based on pricing signals without dropping below a strict "Firm Capacity" baseline guardrail.
*   **Predictive Asset Health:** Simulates deep-learning diagnostics to predict cell health fade and transformer degradation caused by extreme thermal or state-of-charge constraints.
*   **BTM Resilience Controller (Islanding):** Automatically detects severe grid disturbances and physically islands the micro-hub, redirecting all battery and firm generation exclusively to life-support systems.
*   **Automated ESG Ledger:** An automated Measurement, Reporting, and Verification (MRV) logging system tracking Scope 3 emissions avoided and clean energy utilized for ISSB and CBAM compliance reporting.
*   **Real-Time Data Dashboard:** A responsive React frontend powered by WebSockets, providing live charting, agent thought-process justifications, and interactive grid-override controls.

---

## 🛠️ Technology Stack

**Backend:**
*   Python 3.10+
*   FastAPI & Uvicorn (Real-time async server)
*   WebSockets (Bi-directional telemetry streaming)
*   LangGraph & Langchain (Agentic AI reasoning)

**Frontend:**
*   React 18 & Vite
*   Tailwind CSS v4
*   Recharts (High-performance dynamic charting)
*   Lucide React (Icons)

---

## 🚀 How to Run the Project Local Environment

The architecture is split into two independent services: the Python FastAPI Backend and the React Frontend. You will need to run both concurrently in separate terminal windows.

### Prerequisites
*   **Python:** Version 3.10 or higher.
*   **Node.js:** Version 20.19+ or 22.12+ (Required by Vite and Tailwind CSS v4).

### 1. Start the Backend Server

The backend runs the simulation environment, the LangGraph AI agent, and streams the telemetry via WebSockets.

1. Open your terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```
2. *(Optional but recommended)* Create and activate a Virtual Environment:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI server using Uvicorn:
   ```bash
   uvicorn api:app --reload
   ```
   *The backend should now be running at `http://127.0.0.1:8000`. You will see it broadcasting telemetry ticks in the console.*

### 2. Start the Frontend Dashboard

The frontend is a Vite-powered React application that visualizes the WebSocket data.

1. Open a **new** terminal window and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the Node modules:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your web browser and navigate to the URL provided in the terminal (usually `http://localhost:5173`).

---

## 🧪 Testing the Simulation

Once both servers are running and the dashboard is open:

1. **Observe the Autonomous Agent:** Watch the Line Chart map the fluctuating `Grid Price ($/MWh)` against the `Factory Load (MW)`. Observe how the AI agent autonomously throttles the robotic lines down when grid prices spike above $60 in order to maximize battery arbitrage profits.
2. **Read the AI Justification:** Check the "AI Trading Agent" metric card. The agent outputs its internal thought process (EBOC logic) justifying why it is acting.
3. **Trigger Emergency Islanding:** Click the red **"Force Islanding"** toggle button in the top right corner. 
    * Watch the system immediately abandon profit-seeking to protect the Micro-Hub.
    * Notice the Factory Load drops instantly to the 0.5 MW "Firm Capacity" baseline.
    * Scroll down to the ESG Ledger and watch the **Hours Islanded** and **Scope 3 Emissions Avoided** metrics begin to climb in real-time as you survive off-grid.
