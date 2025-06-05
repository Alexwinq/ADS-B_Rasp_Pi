import os
import json
import time
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.text import LabelBase
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition
from kivy.utils import get_color_from_hex

# Display settings
Config.set('graphics', 'fullscreen', '1')
Config.set('graphics', 'show_cursor', '0')
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

# Register custom font
LabelBase.register(name="Military", fn_regular="VT323-Regular.ttf")

# Colors
MILITARY_GREEN = get_color_from_hex("#00FF00")
BLACK = get_color_from_hex("#000000")

# JSON output path
JSON_OUTPUT_FILE = "json_output/aircraft_data.json"
os.makedirs("json_output", exist_ok=True)

# Tail mapping (optional)
hex_to_tail = {
    "a7302f": "N12345",
    "ab4af1": "N67890",
}

# Function to get aircraft with position
def load_aircraft_with_position():
    if not os.path.exists("/run/dump1090-fa/aircraft.json"):
        return []
    with open("/run/dump1090-fa/aircraft.json", "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []
    return [ac for ac in data.get("aircraft", []) if "lat" in ac and "lon" in ac]

# Save aircraft details to json_output/aircraft_data.json every 5 seconds
def save_aircraft_to_json():
    while True:
        aircraft = load_aircraft_with_position()
        enriched = []
        for ac in aircraft:
            hexid = ac.get("hex", "???")
            enriched.append({
                "hex": hexid,
                "tail": hex_to_tail.get(hexid.lower(), "Unknown"),
                "flight": ac.get("flight", "").strip(),
                "altitude": ac.get("alt_baro", "N/A"),
                "speed": ac.get("gs", "N/A"),
                "lat": ac.get("lat", "N/A"),
                "lon": ac.get("lon", "N/A"),
                "seen": ac.get("seen", 0)
            })
        with open(JSON_OUTPUT_FILE, "w") as out:
            json.dump(enriched, out, indent=2)
        time.sleep(5)

# Screens
class InitScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dot_index = 0
        self.dot_sequence = [".", "..", "...", "...."]
        self.label = Label(text="Initializing.", font_size=48, color=MILITARY_GREEN,
                           font_name="Military", halign="center", valign="middle")
        self.label.bind(size=self.label.setter('text_size'))
        layout = BoxLayout(orientation='vertical', padding=50)
        layout.add_widget(self.label)
        self.add_widget(layout)
        Clock.schedule_interval(self.animate_dots, 0.5)
        Clock.schedule_once(self.goto_main_screen, 8)

    def animate_dots(self, dt):
        dots = self.dot_sequence[self.dot_index]
        self.label.text = f"Initializing{dots}"
        self.dot_index = (self.dot_index + 1) % len(self.dot_sequence)

    def goto_main_screen(self, dt):
        self.manager.current = 'main'

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=100, spacing=20)
        button = Button(
            text="Begin scanning for aircraft",
            font_size=32,
            size_hint=(0.6, 0.2),
            pos_hint={'center_x': 0.5},
            background_color=BLACK,
            color=MILITARY_GREEN,
            font_name="Military"
        )
        button.bind(on_press=self.start_scanning)
        layout.add_widget(button)
        self.add_widget(layout)

    def start_scanning(self, instance):
        if not hasattr(self.manager, "scanner_started"):
            self.manager.scanner_started = True
            threading.Thread(target=save_aircraft_to_json, daemon=True).start()
        self.manager.current = "scanning"

class ScanningScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dot_index = 0
        self.dot_sequence = [".", "..", "...", "...."]
        self.label = Label(text="Scanning for aircraft.", font_size=48,
                           color=MILITARY_GREEN, font_name="Military",
                           halign="center", valign="middle")
        self.label.bind(size=self.label.setter('text_size'))
        layout = BoxLayout(orientation='vertical', padding=50)
        layout.add_widget(self.label)
        self.add_widget(layout)

    def on_enter(self):
        self.dot_event = Clock.schedule_interval(self.animate_dots, 0.5)
        self.check_event = Clock.schedule_interval(self.check_for_aircraft, 2)

    def on_leave(self):
        if hasattr(self, 'dot_event'):
            self.dot_event.cancel()
        if hasattr(self, 'check_event'):
            self.check_event.cancel()

    def animate_dots(self, dt):
        dots = self.dot_sequence[self.dot_index]
        self.label.text = f"Scanning for aircraft{dots}"
        self.dot_index = (self.dot_index + 1) % len(self.dot_sequence)

    def check_for_aircraft(self, dt):
        self.manager.load_aircraft_screens()
        if "aircraft_0" in self.manager.screen_names:
            self.manager.current = "aircraft_0"

class AircraftScreen(Screen):
    def __init__(self, aircraft, index, **kwargs):
        super().__init__(name=f"aircraft_{index}", **kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=10)
        props = [
            f"ICAO Hex : {aircraft['hex']}",
            f"Tail #   : {aircraft['tail']}",
            f"Flight   : {aircraft['flight']}",
            f"Altitude : {aircraft['altitude']} ft",
            f"Speed    : {aircraft['speed']} knots",
            f"Lat/Lon  : {aircraft['lat']}, {aircraft['lon']}",
            f"Last seen: {aircraft['seen']} sec ago"
        ]
        for line in props:
            layout.add_widget(Label(text=line, font_name="Military",
                                    color=MILITARY_GREEN, font_size=28, halign="left"))
        self.add_widget(layout)

class MilitaryScreenManager(ScreenManager):
    def load_aircraft_screens(self):
        # Remove old screens
        for screen in list(self.screen_names):
            if screen.startswith("aircraft_"):
                self.remove_widget(self.get_screen(screen))

        # Load aircraft from JSON
        try:
            with open(JSON_OUTPUT_FILE, "r") as f:
                aircraft = json.load(f)
        except:
            aircraft = []

        for i, ac in enumerate(aircraft):
            self.add_widget(AircraftScreen(ac, i))

        if aircraft:
            self.transition_to(0)

    def transition_to(self, index):
        name = f"aircraft_{index}"
        if name in self.screen_names:
            self.transition = SlideTransition(direction='left')
            self.current = name
            Clock.schedule_once(self.recheck_aircraft, 5)

    def recheck_aircraft(self, dt):
        self.load_aircraft_screens()
        if not any(s.startswith("aircraft_") for s in self.screen_names):
            self.current = "scanning"

class MilitaryApp(App):
    def build(self):
        sm = MilitaryScreenManager(transition=FadeTransition())
        sm.add_widget(InitScreen(name='init'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(ScanningScreen(name='scanning'))
        return sm

if __name__ == '__main__':
    MilitaryApp().run()
