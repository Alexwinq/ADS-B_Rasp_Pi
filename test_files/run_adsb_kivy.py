import json
import subprocess
from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock

# Adjust these paths as needed
DUMP1090_PATH = "/usr/bin/dump1090-fa"
JSON_DIR = "/home/alex/dump1090-json"
JSON_FILE = f"{JSON_DIR}/aircraft.json"

class ADSBApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dump_process = None
        self.label = None

    def start_dump1090(self):
        # Start dump1090-fa in background and write JSON
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
        self.label = Label(text="Starting ADS-B...", font_size='20sp')
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
            else:
                display_text = f"Aircraft detected: {len(aircraft_list)}\n\n"

                for ac in aircraft_list[:5]:  # Limit to 5 entries
                    flight = ac.get("flight", "").strip()
                    if not flight:
                        flight = "Unknown Flight"

                    altitude = ac.get("altitude")
                    if altitude is None:
                        altitude_str = "Unknown Altitude"
                    else:
                        altitude_str = f"{altitude} ft"

                    display_text += f"{flight} @ {altitude_str}\n"

                self.label.text = display_text

        except Exception as e:
            self.label.text = f"Error fetching data:\n{e}"

    def on_stop(self):
        self.stop_dump1090()

if __name__ == '__main__':
    ADSBApp().run()
