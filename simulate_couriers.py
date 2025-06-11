import pandas as pd
import time
import random

def random_move(lat, lon):
    # Move faster (bigger step size)
    lat += random.uniform(-0.002, 0.002)
    lon += random.uniform(-0.002, 0.002)
    return round(lat, 6), round(lon, 6)

def main():
    couriers = [
        {"jid": "courier1@server", "lat": 45.7489, "lon": 21.2087, "battery": 100, "load": "2/5", "is_busy": True, "last_updated": time.strftime('%Y-%m-%d %H:%M:%S')},
        {"jid": "courier2@server", "lat": 45.7573, "lon": 21.2291, "battery": 95, "load": "1/5", "is_busy": False, "last_updated": time.strftime('%Y-%m-%d %H:%M:%S')},
    ]
    while True:
        for c in couriers:
            c["lat"], c["lon"] = random_move(c["lat"], c["lon"])
            # Battery drains slower
            c['battery'] = max(0, c['battery'] - random.randint(0, 1))
            c['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        df = pd.DataFrame(couriers)
        df.to_csv("courier_status.csv", index=False)
        time.sleep(0.8)   # Update even more frequently

if __name__ == "__main__":
    main()