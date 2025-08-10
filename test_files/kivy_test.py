from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


class MyFirstApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        label = Label(text='Hello, Kivy on Raspberry Pi!', font_size=24)
        button = Button(text='Press Me', font_size=24)
        button.bind(on_press=self.on_button_press)

        layout.add_widget(label)
        layout.add_widget(button)

        return layout

    def on_button_press(self, instance):
        instance.text = 'You pressed me!'


if __name__ == '__main__':
    MyFirstApp().run()
