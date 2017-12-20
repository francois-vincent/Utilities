# https://python-gtk-3-tutorial.readthedocs.io/en/latest/index.html

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def first():
    win = Gtk.Window()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()


class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")
        self.button = Gtk.Button(label="Click Here")
        self.button.connect("clicked", self.on_button_clicked)
        self.add(self.button)

    def on_button_clicked(self, widget):
        print("Hello World")


def second():
    win = MyWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    first()
    second()
