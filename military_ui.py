import json
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.utils import get_color_from_hex
from kivy.config import Config

# Fullscreen and hide mouse cursor
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'show_cursor', '0')

# Register custom military-style font (make sure the font file is present)
LabelBase.register(name="Military", fn_regular="VT323-Regular.ttf")

# COLORS
MILITARY_GREEN = get_color_from_hex("#00FF00")
BLACK = get_color_from_hex("#000000")

JSON_FOLDER = "json_output"
JSON_FILE = os.path.join(JSON_FOLDER, "aircraft_data.json")

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
        self.manager.current = "scanning"
        self.manager.get_screen("scanning").start()

class ScanningScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dot_index = 0
        self.dot_sequence = [".", "..", "...", "...."]

        self.label = Label(
            text="Scanning for aircraft.",
            font_size=48,
            color=MILITARY_GREEN,
            font_name="Military",
            halign="center",
            valign="middle"
        )
        self.label.bind(size=self.label.setter('text_size'))

        layout = BoxLayout(orientation='vertical', padding=50)
        layout.add_widget(self.label)
        self.add_widget(layout)

        self.update_event = None

    def animate_dots(self, dt):
        dots = self.dot_sequence[self.dot_index]
        self.label.text = f"Scanning for aircraft{dots}"
        self.dot_index = (self.dot_index + 1) % len(self.dot_sequence)

    def start(self):
        self.dot_index = 0
        self.label.text = "Scanning for aircraft."
        if self.update_event:
            self.update_event.cancel()
        self.update_event = Clock.schedule_interval(self.check_for_aircraft, 1)

        # Animate dots every 0.5s
        self.dot_anim_event = Clock.schedule_interval(self.animate_dots, 0.5)

    def check_for_aircraft(self, dt):
        aircraft_list = self.load_aircraft_data()
        if aircraft_list:
            # Aircraft detected, switch to first aircraft screen
            self.update_event.cancel()
            self.dot_anim_event.cancel()
            self.manager.get_screen("aircraft_display").load_aircraft_list(aircraft_list)
            self.manager.current = "aircraft_display"

    def load_aircraft_data(self):
        if not os.path.exists(JSON_FILE):
            return []
        try:
            with open(JSON_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            return []

        # data expected as list of aircraft dicts
        if isinstance(data, list):
            return data
        else:
            return []

class AircraftScreen(Screen):
    def __init__(self, aircraft, index, total, **kwargs):
        # name is mandatory for ScreenManager; set here
        super().__init__(name=f"aircraft_{index}", **kwargs)
        self.aircraft = aircraft
        self.index = index
        self.total = total

        self.layout = RelativeLayout()
        self.add_widget(self.layout)

        # Display aircraft info labels
        self.create_ui()

    def create_ui(self):
        ac = self.aircraft

        hexid = ac.get("hex", "???")
        lat = ac.get("lat", "N/A")
        lon = ac.get("lon", "N/A")
        alt = ac.get("alt_baro", "N/A")
        speed = ac.get("gs", "N/A")
        flight = ac.get("flight", "").strip()
        seen = ac.get("seen", 0)

        tail = ac.get("tail", "Unknown")

        # Large labels centered
        label_text = (
            f"ICAO Hex: {hexid}\n"
            f"Tail #: {tail}\n"
            f"Flight: {flight}\n"
            f"Altitude: {alt} ft\n"
            f"Speed: {speed} knots\n"
            f"Lat/Lon: {lat}, {lon}\n"
            f"Last seen: {seen:.1f} sec ago"
        )

        self.info_label = Label(
            text=label_text,
            font_size=32,
            color=MILITARY_GREEN,
            font_name="Military",
            halign="left",
            valign="top",
            size_hint=(0.9, 0.8),
            pos_hint={"x": 0.05, "top": 0.9}
        )
        self.info_label.bind(size=self.info_label.setter('text_size'))
        self.layout.add_widget(self.info_label)

        # Aircraft count label top-right
        self.count_label = Label(
            text=f"{self.index + 1} / {self.total} aircraft",
            font_size=24,
            color=MILITARY_GREEN,
            font_name="Military",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={"right": 0.98, "top": 0.98}
        )
        self.layout.add_widget(self.count_label)

        # Navigation buttons
        btn_prev = Button(
            text="<< Prev",
            font_size=24,
            size_hint=(0.2, 0.1),
            pos_hint={"x": 0.05, "y": 0.05},
            background_color=BLACK,
            color=MILITARY_GREEN,
            font_name="Military"
        )
        btn_prev.bind(on_press=self.go_prev)
        self.layout.add_widget(btn_prev)

        btn_next = Button(
            text="Next >>",
            font_size=24,
            size_hint=(0.2, 0.1),
            pos_hint={"right": 0.95, "y": 0.05},
            background_color=BLACK,
            color=MILITARY_GREEN,
            font_name="Military"
        )
        btn_next.bind(on_press=self.go_next)
        self.layout.add_widget(btn_next)

    def go_prev(self, instance):
        prev_index = (self.index - 1) % self.total
        self.manager.get_screen("aircraft_display").show_aircraft(prev_index)

    def go_next(self, instance):
        next_index = (self.index + 1) % self.total
        self.manager.get_screen("aircraft_display").show_aircraft(next_index)

    def update_info(self, aircraft, index, total):
        self.aircraft = aircraft
        self.index = index
        self.total = total

        hexid = aircraft.get("hex", "???")
        lat = aircraft.get("lat", "N/A")
        lon = aircraft.get("lon", "N/A")
        alt = aircraft.get("alt_baro", "N/A")
        speed = aircraft.get("gs", "N/A")
        flight = aircraft.get("flight", "").strip()
        seen = aircraft.get("seen", 0)
        tail = aircraft.get("tail", "Unknown")

        label_text = (
            f"ICAO Hex: {hexid}\n"
            f"Tail #: {tail}\n"
            f"Flight: {flight}\n"
            f"Altitude: {alt} ft\n"
            f"Speed: {speed} knots\n"
            f"Lat/Lon: {lat}, {lon}\n"
            f"Last seen: {seen:.1f} sec ago"
        )
        self.info_label.text = label_text
        self.count_label.text = f"{self.index + 1} / {self.total} aircraft"


class AircraftDisplayScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="aircraft_display", **kwargs)
        self.aircraft_list = []
        self.current_index = 0
        self.aircraft_screen = None
        self.update_event = None

    def load_aircraft_list(self, aircraft_list):
        self.aircraft_list = aircraft_list
        self.current_index = 0

        if not self.aircraft_list:
            # No aircraft, go back to scanning
            self.manager.current = "scanning"
            self.manager.get_screen("scanning").start()
            return

        if self.aircraft_screen:
            # Update existing screen without transition animation
            self.aircraft_screen.update_info(
                self.aircraft_list[self.current_index], self.current_index, len(self.aircraft_list)
            )
        else:
            # Create first AircraftScreen
            self.aircraft_screen = AircraftScreen(
                self.aircraft_list[self.current_index], self.current_index, len(self.aircraft_list)
            )
            self.clear_widgets()
            self.add_widget(self.aircraft_screen)

        # Schedule update to refresh aircraft data every 2 seconds
        if self.update_event:
            self.update_event.cancel()
        self.update_event = Clock.schedule_interval(self.update_aircraft_data, 2)

    def update_aircraft_data(self, dt):
        new_list = self.load_aircraft_data()
        if not new_list:
            # No aircraft, go back to scanning
            if self.update_event:
                self.update_event.cancel()
            self.manager.current = "scanning"
            self.manager.get_screen("scanning").start()
            return

        self.aircraft_list = new_list
        total = len(self.aircraft_list)

        # Keep current index valid
        if self.current_index >= total:
            self.current_index = 0

        # Update current screen data without animation
        self.aircraft_screen.update_info(
            self.aircraft_list[self.current_index], self.current_index, total
        )

    def load_aircraft_data(self):
        if not os.path.exists(JSON_FILE):
            return []
        try:
            with open(JSON_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            return []

        # Expected data: list of dicts (aircraft)
        if not isinstance(data, list):
            return []

        return data

    def show_aircraft(self, index):
        if not self.aircraft_list:
            return
        self.current_index = index % len(self.aircraft_list)
        self.aircraft_screen.update_info(
            self.aircraft_list[self.current_index], self.current_index, len(self.aircraft_list)
        )


class MilitaryApp(App):
    def build(self):
        self.sm = ScreenManager(transition=FadeTransition())

        self.sm.add_widget(InitScreen(name="init"))
        self.sm.add_widget(MainScreen(name="main"))
        self.sm.add_widget(ScanningScreen(name="scanning"))
        self.sm.add_widget(AircraftDisplayScreen(name="aircraft_display"))

        return self.sm

if __name__ == "__main__":
    MilitaryApp().run()
