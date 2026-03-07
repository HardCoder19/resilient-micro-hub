import os
import json
import time
from datetime import datetime

class ESGLedger:
    """
    Automated MRV (Measurement, Reporting, and Verification) system.
    Tracks emissions avoided, power utilized behind-the-meter, and total islanded hours
    for ISSB and CBAM compliance reporting.
    """
    def __init__(self, ledger_file: str = "esg_compliance_log.json"):
        self.ledger_file = ledger_file
        
        # In a real system, this is roughly 0.85 to 1.5 lbs of CO2 per kWh depending on grid mix
        self.lbs_co2_per_mwh_grid = 850.0 
        
        # Cumulative metrics
        self.total_islanded_hours = 0.0
        self.scope_3_emissions_avoided_lbs = 0.0
        self.total_solar_storage_mwh_used = 0.0
        
        self._load_ledger()
        
    def _load_ledger(self):
        """Loads previous compliance data if it exists."""
        if os.path.exists(self.ledger_file):
            try:
                with open(self.ledger_file, 'r') as f:
                    data = json.load(f)
                    self.total_islanded_hours = data.get("total_islanded_hours", 0.0)
                    self.scope_3_emissions_avoided_lbs = data.get("scope_3_emissions_avoided_lbs", 0.0)
                    self.total_solar_storage_mwh_used = data.get("total_solar_storage_mwh_used", 0.0)
            except Exception as e:
                print(f"Failed to load ledger: {e}")
                
    def _save_ledger(self):
        """Persists compliance data to disk."""
        data = {
            "last_updated": datetime.now().isoformat(),
            "total_islanded_hours": round(self.total_islanded_hours, 2),
            "scope_3_emissions_avoided_lbs": round(self.scope_3_emissions_avoided_lbs, 2),
            "total_solar_storage_mwh_used": round(self.total_solar_storage_mwh_used, 2)
        }
        try:
            with open(self.ledger_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Failed to save ledger: {e}")

    def log_tick(self, is_islanded: bool, duration_hours: float, battery_discharged_mwh: float, factory_consumed_mwh: float):
        """
        Records the impact of a single simulation tick.
        """
        if is_islanded:
            self.total_islanded_hours += duration_hours
            
        # If the factory is running off the battery (or solar/firm capacity) instead of the grid,
        # we calculate the emissions avoided.
        if battery_discharged_mwh > 0:
            self.total_solar_storage_mwh_used += battery_discharged_mwh
            # Simplified calculation: power we didn't pull from the grid = emissions avoided
            self.scope_3_emissions_avoided_lbs += (battery_discharged_mwh * self.lbs_co2_per_mwh_grid)
            
        self._save_ledger()
        
    def get_compliance_report(self) -> dict:
        """Returns the current state for the frontend dashboard."""
        return {
            "islandedHours": round(self.total_islanded_hours, 2),
            "emissionsAvoidedLbs": round(self.scope_3_emissions_avoided_lbs, 2),
            "cleanEnergyUsedMWh": round(self.total_solar_storage_mwh_used, 2)
        }
