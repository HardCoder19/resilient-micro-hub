class FactorySimulator:
    def __init__(self, max_load_mw: float = 2.0):
        self.max_load_mw = max_load_mw
        # Operation level from 0.0 (off) to 1.0 (full 3D printing/robotic load)
        self.operation_level = 1.0 
        
        # Phase 3: "Raise the Roof" Modular Load Profiling
        # Each active line consists of robotic arms and 3D printers
        self.total_lines = 4
        
        # Phase 3: "Firm" Capacity Guardrail
        # Represents Ward 250 Micro-nuclear baseline generation ensuring
        # the factory never drops to 0.0 MW available power.
        self.firm_capacity_mw = 0.5 
        
    def set_operation_level(self, level: float):
        """Throttles the factory's power usage (0.0 to 1.0)"""
        self.operation_level = max(0.0, min(1.0, level))
        
    def get_current_load_mw(self) -> float:
        """
        Returns the current real-time load of the factory.
        If firm capacity exists, it covers the baseline payload even if throttled.
        """
        requested_load = self.max_load_mw * self.operation_level
        # The factory consumes at minimum its firm capacity (idle maintenance, life support)
        # and at maximum its full operational load.
        return max(self.firm_capacity_mw, requested_load)
        
    def get_active_robotic_lines(self) -> int:
        """Calculates how many modular housing lines are active based on power level."""
        # E.g., at 50% power, 2 out of 4 lines are active.
        return int(self.total_lines * self.operation_level)
        
    def get_power_consumed_mwh(self, duration_hours: float) -> float:
        """Calculates power used over a timeframe."""
        return self.get_current_load_mw() * duration_hours
