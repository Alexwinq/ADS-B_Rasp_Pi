from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.resources import resource_add_path
import os

font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
resource_add_path(font_path)


TAN_COLOR = get_color_from_hex("#D2B48C")

class InitScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.dot_index = 0
        self.dot_sequence = [".", "..", "...", "...."]

        self.label = Label(
            text="Initializing.",
            font_size=48,
            color=TAN_COLOR,
            font_name="VT323-Regular.ttf",
            halign="center",
            valign="middle"
        )
        self.label.bind(size=self.label.setter('text_size'))

        layout = BoxLayout(orientation='vertical', padding=50)
        layout.add_widget(self.label)
        self.add_widget(layout)

    def on_enter(self):
        self.dot_index = 0
        Clock.schedule_interval(self.animate_dots, 0.5)
        Clock.schedule_once(self.goto_main_screen, 8)

    def on_leave(self):
        Clock.unschedule(self.animate_dots)

    def animate_dots(self, dt):
        dots = self.dot_sequence[self.dot_index]
        self.label.text = f"Initializing{dots}"
        self.dot_index = (self.dot_index + 1) % len(self.dot_sequence)

    def goto_main_screen(self, dt):
        self.manager.current = "home"  # or whatever your next screen is
