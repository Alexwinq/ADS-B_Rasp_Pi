from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from screens.init_screen import InitScreen
# Later: from screens.home_screen import HomeScreen

class TrackerApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(InitScreen(name="loading"))
        # Later: sm.add_widget(HomeScreen(name="home"))
        sm.current = "loading"
        return sm

if __name__ == "__main__":
    TrackerApp().run()
