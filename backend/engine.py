import asyncio
import time
from data_clients.ercot_client import ERCotClient
from data_clients.nyiso_client import NYISOClient
from battery_sim import BatterySimulator
from factory_sim import FactorySimulator
from asset_health import AssetHealthPredictor
from agent import run_trading_agent
from esg_ledger import ESGLedger

class OrchestratorEngine:
    def __init__(self):
        self.ercot = ERCotClient()
        self.nyiso = NYISOClient()
        self.battery = BatterySimulator(max_capacity_mwh=10.0, initial_soc=0.5)
        self.factory = FactorySimulator(max_load_mw=2.0)
        self.health_predictor = AssetHealthPredictor()
        self.esg_ledger = ESGLedger()
        
        # We will use 5 minute steps (0.0833 hours) for Phase 1 live data
        self.simulated_hours_per_tick = 5 / 60.0 
        
        self.current_price = 0.0
        self.grid_status = "NORMAL"
        self.action_log = "Engine Initialized."
        self.health_state = {}

    async def _fetch_telemetry(self):
        # Fetching concurrently
        self.current_price, self.grid_status = await asyncio.gather(
            self.ercot.get_real_time_lmp(),
            self.nyiso.get_grid_condition()
        )

    def _execute_agentic_trading(self):
        """
        Phase 2: Agentic Engine (LangGraph) running live trading logic based on grid signals.
        """
        # Execute LangGraph node flow to get AI trading decision
        agent_decision = run_trading_agent(self.current_price, self.grid_status, self.battery.get_soc())
        
        # Parse output EBOC signals
        action = agent_decision.get('target_battery_action', 'HOLD')
        multiplier = agent_decision.get('target_factory_multiplier', 1.0)
        self.action_log = f"Agent Reason: {agent_decision.get('decision_reasoning', 'Unknown')}"

        # Act on Factory
        self.factory.set_operation_level(multiplier)
        
        # Act on Battery
        battery_discharged_mwh = 0.0
        if action == "CHARGE":
            self.battery.charge(self.simulated_hours_per_tick)
        elif action == "DISCHARGE":
            battery_discharged_mwh = self.battery.discharge(self.simulated_hours_per_tick)
            
        # Is the system disconnected from the grid?
        is_islanded = self.grid_status != "NORMAL"

        # Phase 4: ESG Compliance Logging
        self.esg_ledger.log_tick(
            is_islanded=is_islanded,
            duration_hours=self.simulated_hours_per_tick,
            battery_discharged_mwh=battery_discharged_mwh,
            factory_consumed_mwh=self.factory.get_current_load_mw() * self.simulated_hours_per_tick
        )

    async def tick(self) -> dict:
        """
        Executes one evaluation tick of the Orchestrator.
        Returns the current state dictionary for the API/Frontend.
        """
        await self._fetch_telemetry()
        self._execute_agentic_trading()
        
        # Run asset health prediction
        self.health_state = await self.health_predictor.analyze_telemetry(
            self.factory.get_current_load_mw(),
            self.battery.get_soc()
        )
        
        return {
            "time": time.strftime("%H:%M:%S"),
            "gridPrice": self.current_price,
            "gridStatus": self.grid_status,
            "batterySoC": self.battery.get_soc() * 100, # converted to percentage
            "factoryLoad": self.factory.get_current_load_mw(),
            "firmCapacity": self.factory.firm_capacity_mw,
            "activeRoboticLines": self.factory.get_active_robotic_lines(),
            "actionLog": self.action_log,
            "transformerHealth": self.health_state["transformer_health"],
            "batteryHealth": self.health_state["battery_cell_health"],
            "predictiveAlerts": self.health_state["predictive_alerts"],
            "esgReport": self.esg_ledger.get_compliance_report()
        }
