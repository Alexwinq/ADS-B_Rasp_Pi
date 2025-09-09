import json
import subprocess
from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock

# Paths
DUMP1090_PATH = "/usr/bin/dump1090-fa"
JSON_DIR = "/home/alex/dump1090-json"
JSON_FILE = f"{JSON_DIR}/aircraft.json"

class ADSBApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dump_process = None
        self.label = None

    def start_dump1090(self):
        # Launch dump1090-fa and write JSON to target dir
        self.dump_process = subprocess.Popen([
            "sudo", DUMP1090_PATH,
            "--net",
            "--gain", "-10",
            "--write-json", JSON_DIR
        ])

    def stop_dump1090(self):
        if self.dump_process:
            self.dump_process.terminate()
            self.dump_process.wait()

    def build(self):
        self.label = Label(text="Starting ADS-B...", font_size='16sp')
        self.start_dump1090()
        Clock.schedule_interval(self.update_display, 2)
        return self.label

    def update_display(self, dt):
        try:
            with open(JSON_FILE, 'r') as f:
                data = json.load(f)

            aircraft_list = data.get("aircraft", [])
            if not aircraft_list:
                self.label.text = "No aircraft detected."
                return

            display_text = f"Aircraft detected: {len(aircraft_list)}\n\n"

            for ac in aircraft_list[:5]:  # Show first 5 aircraft
                hexid = ac.get("hex", "N/A").upper()
                tail = ac.get("r", "N/A")
                flight = ac.get("flight", "").strip() or "Unknown"
                alt = ac.get("altitude")
                alt = f"{alt} ft" if alt else "Unknown"

                speed = ac.get("gs")
                speed = f"{speed:.0f} knots" if speed else "Unknown"

                lat = ac.get("lat", "Unknown")
                lon = ac.get("lon", "Unknown")

                seen = ac.get("seen", 0)
                seen_str = f"{round(seen, 1)} sec ago"

                display_text += (
                    f"ICAO Hex: {hexid}\n"
                    f"Tail #: {tail}\n"
                    f"Flight: {flight}\n"
                    f"Altitude: {alt}\n"
                    f"Speed: {speed}\n"
                    f"Lat: {lat}, Lon: {lon}\n"
                    f"Last Seen: {seen_str}\n"
                    f"{'-'*30}\n"
                )

            self.label.text = display_text

        except Exception as e:
            self.label.text = f"Error fetching data:\n{e}"

    def on_stop(self):
        self.stop_dump1090()

if __name__ == '__main__':
    ADSBApp().run()
