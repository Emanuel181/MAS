import pandas as pd
import json
import time
import os

print("Data updater started. Reading 'courier_status.csv' and writing to 'static/map_data.json'.")
print("Press Ctrl+C to stop.")


def create_geojson_feature(lon, lat, properties):
    """Creates a GeoJSON polygon feature for 3D extrusion."""
    size = 0.0001
    return {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [[
            [lon - size, lat - size], [lon + size, lat - size],
            [lon + size, lat + size], [lon - size, lat + size],
            [lon - size, lat - size],
        ]]},
        "properties": properties
    }


# Create a 'static' directory for the JSON file if it doesn't exist
if not os.path.exists("static"):
    os.makedirs("static")

while True:
    try:
        # Read the latest data from the CSV your simulation creates
        df = pd.read_csv("courier_status.csv")
        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
        df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
        df["battery"] = pd.to_numeric(df["battery"], errors="coerce")
        df["is_busy"] = df["is_busy"].astype(bool)
        df.dropna(subset=["lat", "lon", "battery"], inplace=True)

        # Convert the DataFrame to GeoJSON
        courier_features = [
            create_geojson_feature(
                row['lon'], row['lat'],
                {"name": row['jid'].split('@')[0], "is_busy": bool(row['is_busy']), "battery": int(row['battery'])}
            ) for _, row in df.iterrows()
        ]
        courier_geojson = {"type": "FeatureCollection", "features": courier_features}
        map_data = {"couriers": courier_geojson}

        # Write the GeoJSON to a file that the web browser can fetch
        with open("static/map_data.json", "w") as f:
            json.dump(map_data, f)

        # print(f"[{time.ctime()}] map_data.json updated.") # Uncomment for debugging

        time.sleep(1)  # Check for new data every second

    except FileNotFoundError:
        print("Waiting for courier_status.csv to be created by the simulation...")
        time.sleep(2)
    except Exception as e:
        print(f"An error occurred in updater.py: {e}")
        time.sleep(2)