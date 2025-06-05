import json
import os
import threading
import time

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.utils import get_color_from_hex
from kivy.config import Config

# CONFIG
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'show_cursor', '0')

LabelBase.register(name="Military", fn_regular="VT323-Regular.ttf")

MILITARY_GREEN = get_color_from_hex("#00FF00")
BLACK = get_color_from_hex("#000000")

AIRCRAFT_FILE = "/run/dump1090-fa/aircraft.json"
JSON_PATH = "json_output/aircraft_status.json"
hex_to_tail = {
    "a7302f": "N12345",
    "ab4af1": "N67890",
}


def load_aircraft_with_position():
    if not os.path.exists(AIRCRAFT_FILE):
        return []
    with open(AIRCRAFT_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []
    aircraft = data.get("aircraft", [])
    positioned = [ac for ac in aircraft if "lat" in ac and "lon" in ac]
    return positioned


def summarize_aircraft(ac):
    hexid = ac.get("hex", "???")
    lat = ac.get("lat", "N/A")
    lon = ac.get("lon", "N/A")
    alt = ac.get("alt_baro", "N/A")
    speed = ac.get("gs", "N/A")
    flight = ac.get("flight", "").strip()
    seen = ac.get("seen", 0)
    tail = hex_to_tail.get(hexid.lower(), "Unknown")

    return {
        "ICAO Hex": hexid,
        "Tail #": tail,
        "Flight": flight,
        "Altitude (ft)": alt,
        "Speed (knots)": speed,
        "Latitude": lat,
        "Longitude": lon,
        "Last Seen (sec ago)": round(seen, 1)
    }


def save_aircraft_to_json():
    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)

    while True:
        aircraft = load_aircraft_with_position()
        summarized = [summarize_aircraft(ac) for ac in aircraft]
        data = {
            "timestamp": time.time(),
            "total_aircraft": len(summarized),
            "aircraft": summarized
        }
        with open(JSON_PATH, "w") as f:
            json.dump(data, f, indent=2)
        time.sleep(5)


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

        Clock.schedule_interval(self.animate_dots, 0.5)
        Clock.schedule_once(self.goto_main_screen, 4)

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
        # Start aircraft scanner thread (only once)
        if not hasattr(self.manager, "scanner_started"):
            self.manager.scanner_started = True
            threading.Thread(target=save_aircraft_to_json, daemon=True).start()

        self.manager.load_aircraft_screens()
        self.manager.current = "aircraft_0"


class AircraftScreen(Screen):
    def __init__(self, ac_data, index, total, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=15)

        for key, value in ac_data.items():
            layout.add_widget(Label(
                text=f"{key}: {value}",
                font_size=32,
                color=MILITARY_GREEN,
                font_name="Military"
            ))

        nav_layout = BoxLayout(size_hint_y=0.2, spacing=20, padding=20)
        if index > 0:
            prev_btn = Button(text="Previous", font_name="Military", font_size=24,
                              background_color=BLACK, color=MILITARY_GREEN)
            prev_btn.bind(on_press=lambda x: self.manager.transition_to(index - 1))
            nav_layout.add_widget(prev_btn)

        if index < total - 1:
            next_btn = Button(text="Next", font_name="Military", font_size=24,
                              background_color=BLACK, color=MILITARY_GREEN)
            next_btn.bind(on_press=lambda x: self.manager.transition_to(index + 1))
            nav_layout.add_widget(next_btn)

        layout.add_widget(nav_layout)
        self.add_widget(layout)


class MilitaryScreenManager(ScreenManager):
    def load_aircraft_screens(self):
        for screen in list(self.screen_names):
            if screen.startswith("aircraft_"):
                self.remove_widget(self.get_screen(screen))

        if not os.path.exists(JSON_PATH):
            return

        with open(JSON_PATH, "r") as f:
            try:
                data = json.load(f)
                aircraft = data.get("aircraft", [])
            except json.JSONDecodeError:
                return

        for i, ac in enumerate(aircraft):
            screen = AircraftScreen(ac_data=ac, index=i, total=len(aircraft), name=f"aircraft_{i}")
            self.add_widget(screen)

    def transition_to(self, index):
        name = f"aircraft_{index}"
        if name in self.screen_names:
            self.transition = SlideTransition(direction='left')
            self.current = name


class MilitaryApp(App):
    def build(self):
        sm = MilitaryScreenManager(transition=FadeTransition())
        sm.add_widget(InitScreen(name='init'))
        sm.add_widget(MainScreen(name='main'))
        return sm


if __name__ == '__main__':
    MilitaryApp().run()
