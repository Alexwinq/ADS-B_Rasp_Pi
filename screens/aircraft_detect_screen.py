from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.utils import get_color_from_hex
from kivy.resources import resource_add_path
import os
import json
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button


font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "VT323-Regular.ttf")
resource_add_path(font_path)
LabelBase.register(name="VT323", fn_regular=font_path)

TAN_COLOR = get_color_from_hex("#D2B48C")

class AircraftDetect(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.aircraft_list = []
        self.current_index = 0

        # Root layout to allow absolute positioning
        self.root_layout = FloatLayout()

        # Label showing "Aircraft X of Y" in top-right corner
        self.status_label = Label(
            text="Aircraft 0 of 0",
            size_hint=(0.3, 0.1),
            pos_hint={'right': 0.98, 'top': 0.98},
            font_size=18,
            color=TAN_COLOR,
            font_name="VT323",
            halign='right',
            valign='middle'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        self.root_layout.add_widget(self.status_label)

        # Navigation buttons container at bottom
        nav_layout = BoxLayout(
            size_hint=(1, 0.1),
            pos_hint={'x':0, 'y':0}
        )
        self.prev_button = Button(text="< Prev", size_hint=(0.2, 1))
        self.next_button = Button(text="Next >", size_hint=(0.2, 1))
        self.prev_button.bind(on_press=self.show_prev)
        self.next_button.bind(on_press=self.show_next)
        nav_layout.add_widget(self.prev_button)
        nav_layout.add_widget(Label())  # spacer
        nav_layout.add_widget(self.next_button)

        # ScrollView with Label for aircraft data
        self.scrollview = ScrollView(size_hint=(1, 0.8), pos_hint={'x':0, 'y':0.1})
        self.data_label = Label(
            text="",
            font_size=24,
            color=TAN_COLOR,
            font_name="VT323",
            halign='left',
            valign='top',
            size_hint_y=None,  # height dynamic based on text
            text_size=(self.width - 40, None)  # padding for wrap
        )
        self.data_label.bind(texture_size=self.update_label_height)
        self.bind(size=self.update_label_width)
        self.scrollview.add_widget(self.data_label)

        # Add ScrollView and nav layout to root layout
        self.root_layout.add_widget(self.scrollview)
        self.root_layout.add_widget(nav_layout)

        self.add_widget(self.root_layout)

    def update_label_height(self, instance, texture_size):
        instance.height = texture_size[1]

    def update_label_width(self, instance, value):
        self.data_label.text_size = (self.width - 40, None)
        self.data_label.texture_update()

    def update_data(self, json_data):
        # Expect json_data to contain a list or dict with aircraft info
        # Adjust this depending on your actual JSON structure
        if isinstance(json_data, dict) and "aircraft" in json_data:
            self.aircraft_list = json_data["aircraft"]
        elif isinstance(json_data, list):
            self.aircraft_list = json_data
        else:
            self.aircraft_list = []

        self.current_index = 0

        if self.aircraft_list:
            self.show_aircraft(self.current_index)
        else:
            self.data_label.text = "No aircraft data available."
            self.status_label.text = "Aircraft 0 of 0"

        self.update_nav_buttons()

    def show_aircraft(self, index):
        if 0 <= index < len(self.aircraft_list):
            # Format the aircraft info nicely
            aircraft = self.aircraft_list[index]
            formatted_text = json.dumps(aircraft, indent=2)
            self.data_label.text = formatted_text
            self.status_label.text = f"Aircraft {index + 1} of {len(self.aircraft_list)}"
            self.scrollview.scroll_y = 1  # Scroll to top

        self.update_nav_buttons()

    def show_prev(self, *args):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_aircraft(self.current_index)

    def show_next(self, *args):
        if self.current_index < len(self.aircraft_list) - 1:
            self.current_index += 1
            self.show_aircraft(self.current_index)

    def update_nav_buttons(self):
        # Disable prev button if at start
        self.prev_button.disabled = self.current_index == 0
        # Disable next button if at end
        self.next_button.disabled = self.current_index >= len(self.aircraft_list) - 1
