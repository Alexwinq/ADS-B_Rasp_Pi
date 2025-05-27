import json
import time
import folium
import os

JSON_PATH = "/home/alex/dump1090-json/aircraft.json"
OUTPUT_MAP = "/home/alex/aircraft_map.html"

def load_aircraft_data():
    if not os.path.exists(JSON_PATH):
        return []

    try:
        with open(JSON_PATH) as f:
            data = json.load(f)
            return [ac for ac in data.get("aircraft", []) if "lat" in ac and "lon" in ac]
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return []

def create_map(aircraft_list):
    if not aircraft_list:
        print("No aircraft with position found.")
        return

    # Use first aircraft's position to center the map
    center_lat = aircraft_list[0]['lat']
    center_lon = aircraft_list[0]['lon']
    m = folium.Map(location=[center_lat, center_lon], zoom_start=7)

    for ac in aircraft_list:
        lat = ac['lat']
        lon = ac['lon']
        alt = ac.get('alt_baro', 'Unknown')
        hexcode = ac['hex']
        callsign = ac.get('flight', '').strip()

        popup_text = f"Hex: {hexcode}<br>Flight: {callsign}<br>Alt: {alt} ft"
        folium.Marker([lat, lon], popup=popup_text).add_to(m)

    m.save(OUTPUT_MAP)
    print(f"Map updated: {OUTPUT_MAP}")

if __name__ == "__main__":
    while True:
        aircraft = load_aircraft_data()
        create_map(aircraft)
        time.sleep(10)  # update every 10 seconds
