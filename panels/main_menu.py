import gi
import logging

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from panels.menu import MenuPanel

logger = logging.getLogger("KlipperScreen.MainMenu")

def create_panel(*args):
    return MainPanel(*args)

class MainPanel(MenuPanel):
    def __init__(self, screen, title, back=False):
        super().__init__(screen, title, False)

    def initialize(self, panel_name, items, extrudercount):
        print("### Making MainMenu")

        grid = self._gtk.HomogeneousGrid()
        grid.set_hexpand(True)
        grid.set_vexpand(True)

        # Create Extruders and bed icons
        eq_grid = self._gtk.HomogeneousGrid()

        i = 0
        for x in self._printer.get_tools():
            if i > 3:
                break
            self.labels[x] = self._gtk.ButtonImage("extruder-"+str(i), self._gtk.formatTemperatureString(0, 0))
            col = 0 if len(self._printer.get_tools()) == 1 else i%2
            row = i/2
            eq_grid.attach(self.labels[x], col, row, 1, 1)
            i += 1

        if self._printer.has_heated_bed():
            self.labels['heater_bed'] = self._gtk.ButtonImage("bed", self._gtk.formatTemperatureString(0, 0))

            width = 2 if i > 1 else 1
            eq_grid.attach(self.labels['heater_bed'], 0, i/2+1, width, 1)

        self.items = items
        self.create_menu_items()

        self.grid = Gtk.Grid()
        self.grid.set_row_homogeneous(True)
        self.grid.set_column_homogeneous(True)

        grid.attach(eq_grid, 0, 0, 1, 1)
        grid.attach(self.arrangeMenuItems(items, 2, True), 1, 0, 1, 1)

        self.grid = grid

        self.target_temps = {
            "heater_bed": 0,
            "extruder": 0
        }
        
        self.content.add(self.grid)
        self.layout.show_all()

        self._screen.add_subscription(panel_name)

    def activate(self):
        return

    def update_temp(self, dev, temp, target):
        if dev in self.labels:
            self.labels[dev].set_label(self._gtk.formatTemperatureString(temp, target))

    def process_update(self, action, data):
        if action != "notify_status_update":
            return

        self.update_temp("heater_bed",
            self._printer.get_dev_stat("heater_bed","temperature"),
            self._printer.get_dev_stat("heater_bed","target")
        )
        for x in self._printer.get_tools():
            self.update_temp(x,
                self._printer.get_dev_stat(x,"temperature"),
                self._printer.get_dev_stat(x,"target")
            )
        return
