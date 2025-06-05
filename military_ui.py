import json
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, NoTransition
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.utils import get_color_from_hex
from kivy.config import Config
from kivy.uix.screenmanager import Screen

# Fullscreen and hide mouse
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'show_cursor', '0')

# Optional: Register a custom military-style font
LabelBase.register(name="Military", fn_regular="VT323-Regular.ttf")  # Ensure font file present

# COLORS
MILITARY_GREEN = get_color_from_hex("#00FF00")  # Bright green
BLACK = get_color_from_hex("#000000")

# Path to dump1090 JSON output
AIRCRAFT_FILE = "/run/dump1090-fa/aircraft.json"

# Optional tail number mapping
hex_to_tail = {
    "a7302f": "N12345",
    "ab4af1": "N67890",
}

def load_aircraft():
    """Load all aircraft from dump1090 JSON, no filtering."""
    if not os.path.exists(AIRCRAFT_FILE):
        return []

    with open(AIRCRAFT_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []

    return data.get("aircraft", [])

class InitScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dot_index = 0
        self.dot_sequence = [".", "..", "...", "...."]

        self.label = Label(
            text="Initializing.",
            font_size=48,
            color=MILITARY_GREEN,
            font_name="Military",
            halign="center",
            valign="middle"
        )
        self.label.bind(size=self.label.setter('text_size'))

        self.layout = BoxLayout(orientation='vertical', padding=50)
        self.layout.add_widget(self.label)
        self.add_widget(self.layout)

        # Animate dots every 0.5s
        Clock.schedule_interval(self.animate_dots, 0.5)
        # Move to main screen after 8 seconds
        Clock.schedule_once(self.goto_main_screen, 8)

    def animate_dots(self, dt):
        dots = self.dot_sequence[self.dot_index]
        self.label.text = f"Initializing{dots}"
        self.dot_index = (self.dot_index + 1) % len(self.dot_sequence)

    def goto_main_screen(self, dt):
        self.manager.current = 'main'

class AircraftScreen(Screen):
    def __init__(self, index, **kwargs):
        super().__init__(name=f"aircraft_{index}", **kwargs)

        self.index = index

        self.layout = BoxLayout(orientation='vertical', padding=50, spacing=20)

        self.info_label = Label(
            text="Loading aircraft info...",
            font_size=32,
            color=MILITARY_GREEN,
            font_name="Military",
            halign="left",
            valign="top"
        )
        self.info_label.bind(size=self.info_label.setter('text_size'))

        self.aircraft_count_label = Label(
            text="",
            font_size=18,
            color=MILITARY_GREEN,
            font_name="Military",
            size_hint=(None, None),
            size=(200, 30),
            halign="right",
            valign="top",
            pos_hint={"right": 1, "top": 1},
        )
        self.aircraft_count_label.bind(size=self.aircraft_count_label.setter('text_size'))

        # Add count label and info label to layout
        self.layout.add_widget(self.aircraft_count_label)
        self.layout.add_widget(self.info_label)
        self.add_widget(self.layout)

    def update_info(self, aircraft, total_count):
        hexid = aircraft.get("hex", "???")
        lat = aircraft.get("lat", "N/A")
        lon = aircraft.get("lon", "N/A")
        alt = aircraft.get("alt_baro", "N/A")
        speed = aircraft.get("gs", "N/A")
        flight = aircraft.get("flight", "").strip()
        seen = aircraft.get("seen", 0)

        tail = hex_to_tail.get(hexid.lower(), "Unknown")

        self.info_label.text = (
            f"--- Aircraft Detected ---\n"
            f"ICAO Hex : {hexid}\n"
            f"Tail #   : {tail}\n"
            f"Flight   : {flight}\n"
            f"Altitude : {alt} ft\n"
            f"Speed    : {speed} knots\n"
            f"Lat/Lon  : {lat}, {lon}\n"
            f"Last seen: {seen:.1f} sec ago"
        )

        self.aircraft_count_label.text = f"Total Aircraft: {total_count}"

class ScanningScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dot_index = 0
        self.dot_sequence = [".", "..", "...", "...."]

        self.layout = BoxLayout(orientation='vertical', padding=50)
        self.label = Label(
            text="Scanning for aircraft.",
            font_size=48,
            color=MILITARY_GREEN,
            font_name="Military",
            halign="center",
            valign="middle"
        )
        self.label.bind(size=self.label.setter('text_size'))
        self.layout.add_widget(self.label)
        self.add_widget(self.layout)

        # Animate dots every 0.5s
        Clock.schedule_interval(self.animate_dots, 0.5)

    def animate_dots(self, dt):
        dots = self.dot_sequence[self.dot_index]
        self.label.text = f"Scanning for aircraft{dots}"
        self.dot_index = (self.dot_index + 1) % len(self.dot_sequence)

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=100, spacing=20)
        self.button = Button(
            text="Begin scanning for aircraft",
            font_size=32,
            size_hint=(0.6, 0.2),
            pos_hint={'center_x': 0.5},
            background_color=BLACK,
            color=MILITARY_GREEN,
            font_name="Military"
        )
        self.layout.add_widget(self.button)
        self.add_widget(self.layout)

        self.button.bind(on_press=self.start_scanning)

    def start_scanning(self, instance):
        app = App.get_running_app()
        app.start_aircraft_updates()

class MilitaryApp(App):
    def build(self):
        self.sm = ScreenManager(transition=FadeTransition())
        self.sm.add_widget(InitScreen(name='init'))
        self.sm.add_widget(MainScreen(name='main'))
        self.scanning_screen = ScanningScreen(name='scanning')
        self.sm.add_widget(self.scanning_screen)

        self.aircraft_screens = {}  # cache screens by index
        self.aircraft_data = []
        self.current_index = 0

        return self.sm

    def start_aircraft_updates(self):
        self.sm.current = "scanning"
        # Schedule the first update immediately, then every 5 seconds
        Clock.schedule_once(self.update_aircraft_data, 0)

    def update_aircraft_data(self, dt):
        aircraft = load_aircraft()
        total = len(aircraft)

        if total == 0:
            # No aircraft, stay on scanning screen
            if self.sm.current != "scanning":
                self.sm.current = "scanning"
            # reschedule next update
            Clock.schedule_once(self.update_aircraft_data, 5)
            return

        # Clamp current_index if out of range
        if self.current_index >= total:
            self.current_index = 0

        current_ac = aircraft[self.current_index]

        # Check if aircraft screen exists, else create
        screen_name = f"aircraft_{self.current_index}"
        if screen_name not in self.aircraft_screens:
            screen = AircraftScreen(self.current_index, name=screen_name)
            self.aircraft_screens[screen_name] = screen
            self.sm.add_widget(screen)
        else:
            screen = self.aircraft_screens[screen_name]

        # If already on this aircraft screen, just update text (no animation)
        if self.sm.current == screen_name:
            screen.update_info(current_ac, total)
        else:
            # Switch screen without animation
            self.sm.transition = NoTransition()
            self.sm.current = screen_name
            screen.update_info(current_ac, total)
            # Restore transition to FadeTransition for other changes
            self.sm.transition = FadeTransition()

        self.current_index += 1
        if self.current_index >= total:
            self.current_index = 0

        # Schedule next update
        Clock.schedule_once(self.update_aircraft_data, 5)

if __name__ == '__main__':
    MilitaryApp().run()
