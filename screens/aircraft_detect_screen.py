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

font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "VT323-Regular.ttf")
resource_add_path(font_path)
LabelBase.register(name="VT323", fn_regular=font_path)

TAN_COLOR = get_color_from_hex("#D2B48C")

class AircraftDetect(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Root FloatLayout for absolute positioning of gps_label and other widgets
        root_layout = FloatLayout()

        # BoxLayout inside ScrollView for JSON data (vertical scroll)
        scrollview = ScrollView(size_hint=(1, 1), pos_hint={'x':0, 'y':0})
        data_box = BoxLayout(orientation='vertical', padding=20, size_hint_y=None)
        data_box.bind(minimum_height=data_box.setter('height'))  # Auto height grows with content

        # Label to display JSON data inside data_box
        self.data_label = Label(
            text="",
            font_size=24,
            color=TAN_COLOR,
            font_name="VT323",
            halign='left',
            valign='top',
            size_hint_y=None,
            text_size=(780, None),  # Fixed width (screen width minus some padding)
        )
        self.data_label.bind(texture_size=self.update_label_height)

        data_box.add_widget(self.data_label)
        scrollview.add_widget(data_box)

        root_layout.add_widget(scrollview)

        # GPS coordinates label positioned top-right (absolute positioning)
        self.gps_label = Label(
            text="Lat: ---, Lon: ---",
            size_hint=(None, None),
            size=(320, 40),  # Fixed size for GPS label
            pos_hint={'right': 0.98, 'top': 0.98},
            font_size=18,
            color=TAN_COLOR,
            font_name=font_path,
            halign="right",
            valign="middle",
        )
        self.gps_label.bind(size=self.gps_label.setter('text_size'))
        root_layout.add_widget(self.gps_label)

        # Add root layout to screen
        self.add_widget(root_layout)

        # Dummy GPS data (replace with real GPS updates as needed)
        self.latitude = 37.7749
        self.longitude = -122.4194

    def update_label_height(self, instance, texture_size):
        instance.height = texture_size[1]

    def update_data(self, json_data):
        formatted_text = json.dumps(json_data, indent=2)
        self.data_label.text = formatted_text
        # Update GPS label text here if you want dynamic GPS data on this screen as well
        self.gps_label.text = f"Lat: {self.latitude:.4f}, Lon: {self.longitude:.4f}"
