from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.utils import get_color_from_hex
from kivy.resources import resource_add_path
import os
import json

font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "VT323-Regular.ttf")
resource_add_path(font_path)
LabelBase.register(name="VT323", fn_regular=font_path)

TAN_COLOR = get_color_from_hex("#D2B48C")

class AircraftDetect(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20)
        self.data_label = Label(
            text="",
            font_size=24,
            color=TAN_COLOR,
            font_name="VT323",
            halign='left',
            valign='top'
        )
        self.data_label.bind(size=self._update_label_height)

        self.layout.add_widget(self.data_label)
        self.add_widget(self.layout)

    def _update_label_height(self, instance, value):
        instance.text_size = (instance.width, None)
        instance.texture_update()
        instance.height = instance.texture_size[1]

    def update_data(self, json_data):
        formatted_text = json.dumps(json_data, indent=2)
        self.data_label.text = formatted_text
