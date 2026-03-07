import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from engine import OrchestratorEngine
import time

app = FastAPI(title="Resilient Micro-Hub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                print(f"Error broadcasting: {e}")

manager = ConnectionManager()
engine = OrchestratorEngine()

@app.get("/")
def read_root():
    return {"status": "Resilient Micro-Hub API is running"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Listen for client commands (Phase 5 - Interactive Guardrails)
            data = await websocket.receive_text()
            try:
                command = json.loads(data)
                if command.get("action") == "TOGGLE_ISLANDING":
                    # Force the engine into an emergency state
                    if engine.grid_status == "NORMAL":
                        engine.grid_status = "EMERGENCY_ISLAND"
                        print("Simulating Emergency Islanding...")
                    else:
                        engine.grid_status = "NORMAL"
                        print("Restoring Grid Connection...")
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected from WebSocket")

async def system_telemetry_loop():
    print("Starting background telemetry loop broadcast with OrchestratorEngine...")
    while True:
        try:
            # In purely simulated mode, if user manually toggled islanding, we intercept the normal fetch
            # But normally the engine fetches new data every tick. We'll let it fetch, but if we are 
            # in an forced emergency state we override what it fetched.
            manual_override = engine.grid_status == "EMERGENCY_ISLAND"
            
            # Advance simulation by one tick based on live data
            state = await engine.tick()
            
            # Re-apply override if active so the agent is forced to react
            if manual_override:
                engine.grid_status = "EMERGENCY_ISLAND"
                state["gridStatus"] = "EMERGENCY_ISLAND"
            
            # Broadcast the state down to all React clients
            await manager.broadcast(state)
            print(f"Broadcasted tick: {state['time']} | Grid: ${state['gridPrice']}/MWh")
            
            # 5-second tick for simulation timeframe
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Error in telemetry loop: {e}")
            await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(system_telemetry_loop())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
