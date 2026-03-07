class BatterySimulator:
    def __init__(self, max_capacity_mwh: float = 10.0, initial_soc: float = 0.5):
        self.max_capacity_mwh = max_capacity_mwh
        # State of Charge (0.0 to 1.0)
        self.soc = initial_soc
        self.charge_rate_mw = 5.0 # How fast it can charge/discharge per hour
        
    def get_soc(self) -> float:
        return self.soc
        
    def charge(self, duration_hours: float) -> float:
        """Charges battery for a given duration. Returns amount charged in MWh."""
        if self.soc >= 1.0:
            return 0.0
            
        amount_to_charge_mwh = self.charge_rate_mw * duration_hours
        available_headroom = (1.0 - self.soc) * self.max_capacity_mwh
        
        actual_charged = min(amount_to_charge_mwh, available_headroom)
        self.soc += (actual_charged / self.max_capacity_mwh)
        return actual_charged

    def discharge(self, duration_hours: float) -> float:
        """Discharges battery for a given duration. Returns amount discharged in MWh."""
        if self.soc <= 0.0:
            return 0.0
            
        amount_to_discharge_mwh = self.charge_rate_mw * duration_hours
        available_energy = self.soc * self.max_capacity_mwh
        
        actual_discharged = min(amount_to_discharge_mwh, available_energy)
        self.soc -= (actual_discharged / self.max_capacity_mwh)
        return actual_discharged
