from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.resources import resource_add_path
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.app import App
import os

font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "VT323-Regular.ttf")
print(font_path)
resource_add_path(font_path)


TAN_COLOR = get_color_from_hex("#D2B48C")

class InitScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dot_index = 0
        self.dot_sequence = [".", "..", "...", "...."]

        # Main loading label centered
        self.label = Label(
            text="Scanning for Aircraft.",
            font_size=48,
            color=[210 / 255, 180 / 255, 140 / 255, 1],  # D2B48C tan color in RGBA
            font_name=font_path,
            halign="center",
            valign="middle"
        )
        self.label.bind(size=self.label.setter('text_size'))

        # GPS coordinates label top-right corner
        self.gps_label = Label(
            text="Lat: ---, Lon: ---",
            font_size=18,
            color=TAN_COLOR,
            font_name="VT323",
            size_hint=(None, None),
            size=(250, 30),
            halign="right",
            valign="top"
        )
        self.gps_label.bind(size=self.gps_label.setter('text_size'))

        # Layout to center loading label
        layout = BoxLayout(orientation='vertical', padding=50)
        layout.add_widget(self.label)
        self.add_widget(layout)

        # Add GPS label to screen (position manually top-right)
        self.add_widget(self.gps_label)
        self.position_gps_label()

        # Update GPS label position on window resize
        Window.bind(on_resize=lambda *args: self.position_gps_label())

        # Animate loading dots every 0.5 seconds
        Clock.schedule_interval(self.animate_dots, 0.5)

        # For demo, quit app after 5 seconds
        Clock.schedule_once(lambda dt: self.stop_app(), 5)

        # Simulate GPS updates every second
        Clock.schedule_interval(self.update_gps, 1)

        # Dummy lat/lon for demo
        self.latitude = 37.7749
        self.longitude = -122.4194

    def position_gps_label(self):
        # Position GPS label top-right with some margin
        margin_x = 20
        margin_y = 20
        self.gps_label.pos = (Window.width - self.gps_label.width - margin_x,
                              Window.height - self.gps_label.height - margin_y)

    def animate_dots(self, dt):
        dots = self.dot_sequence[self.dot_index]
        self.label.text = f"Initializing{dots}"
        self.dot_index = (self.dot_index + 1) % len(self.dot_sequence)

    def update_gps(self, dt):
        # Here you'd update self.latitude, self.longitude with actual GPS data
        self.gps_label.text = f"Lat: {self.latitude:.4f}, Lon: {self.longitude:.4f}"
        self.position_gps_label()  # Reposition if text size changes

    def stop_app(self):
        from kivy.app import App
        App.get_running_app().stop()