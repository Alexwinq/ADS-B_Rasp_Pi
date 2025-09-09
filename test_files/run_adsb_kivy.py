import subprocess
import time
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import requests

# === Part 1: Launch dump1090-fa in background ===

DUMP1090_PATH = "/usr/bin/dump1090-fa"
dump1090_cmd = [DUMP1090_PATH, "--interactive", "--net"]

try:
    print("Starting dump1090-fa in background...")
    dump1090_proc = subprocess.Popen(dump1090_cmd)
    time.sleep(2)  # Wait a moment to let dump1090 start
except FileNotFoundError:
    print("Error: dump1090-fa not found at the specified path.")
    exit(1)

# === Part 2: Kivy GUI ===

DATA_URL = "http://localhost:8080/data/aircraft.json"

class AircraftDisplay(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.label = Label(text="Loading aircraft data...",
                           font_size='20sp',
                           halign='left',
                           valign='top',
                           text_size=(800, None),
                           size_hint_y=None)
        self.label.bind(texture_size=self.label.setter('size'))

        scroll = ScrollView()
        scroll.add_widget(self.label)
        self.add_widget(scroll)

        Clock.schedule_interval(self.update_data, 3)  # Refresh every 3 seconds

    def update_data(self, dt):
        try:
            response = requests.get(DATA_URL, timeout=2)
            aircraft_list = response.json().get("aircraft", [])
        except Exception as e:
            self.label.text = f"Error fetching data:\n{str(e)}"
            return

        if not aircraft_list:
            self.label.text = "No aircraft detected."
        else:
            lines = []
            for ac in aircraft_list[:10]:
                flight = ac.get("flight", "N/A").strip()
                alt = ac.get("altitude", "N/A")
                lat = ac.get("lat", "N/A")
                lon = ac.get("lon", "N/A")
                lines.append(f"[b]Flight:[/b] {flight or 'N/A'} | Alt: {alt}\nLat: {lat}, Lon: {lon}\n")

            self.label.text = '\n\n'.join(lines)

class ADSBApp(App):
    def build(self):
        return AircraftDisplay()

if __name__ == '__main__':
    ADSBApp().run()

    # When GUI closes, terminate dump1090-fa process
    dump1090_proc.terminate()
    dump1090_proc.wait()