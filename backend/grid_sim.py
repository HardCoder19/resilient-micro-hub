import asyncio
import random
from datetime import datetime, timezone
import gridstatus

class GridSimulator:
    def __init__(self, iso_name: str = "ERCOT"):
        self.iso_name = iso_name
        self.iso = gridstatus.ISOs.get(iso_name)() if iso_name in gridstatus.ISOs else gridstatus.ERCOT()
        self.current_price_mwh = 50.0 # Default starting fallback
        
    async def get_latest_price(self) -> float:
        """Fetches the latest real-time LMP from the ISO."""
        try:
            # We fetch the latest 5-min LMP. For simplicity in this mock, 
            # we grab the SPP (Settlement Point Price) for a major hub like HB_HOUSTON
            # In a real heavy app, this would be an async HTTP call directly, 
            # but gridstatus provides a clean wrapper.
            # Note: gridstatus calls can be synchronous block, so running in executor is safer
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(None, self._fetch_spp)
            
            if df is not None and not df.empty:
                # Get the most recent price for Houston Hub
                houston_data = df[df['Location'] == 'HB_HOUSTON']
                if not houston_data.empty:
                    latest_row = houston_data.iloc[-1]
                    self.current_price_mwh = float(latest_row['SPP'])
                    
            return self.current_price_mwh
            
        except Exception as e:
            print(f"Error fetching grid price: {e}")
            # Fallback to a slightly randomized price to keep simulation running if API fails
            self.current_price_mwh += random.uniform(-2, 2)
            return self.current_price_mwh
            
    def _fetch_spp(self):
        # gridstatus synchronous call
        try:
            if isinstance(self.iso, gridstatus.ERCOT):
                return self.iso.get_spp(date="latest") # Gets latest real-time prices
            return None
        except Exception:
            return None

if __name__ == "__main__":
    # Quick test
    async def test():
        grid = GridSimulator()
        price = await grid.get_latest_price()
        print(f"Current ERCOT Price (HB_HOUSTON): ${price:.2f}/MWh")
        
    asyncio.run(test())
