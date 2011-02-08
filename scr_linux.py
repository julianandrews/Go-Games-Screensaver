# Copyright (c) 2010 Julian Andrews.
# All rights reserved.
#
# This file is part of Go Games Screensaver.
#
#    Go Games Screensaver is free software: you can redistribute it and/or 
#    modify it under the terms of the GNU General Public License as 
#    published by the Free Software Foundation, either version 3 of the 
#    License, or (at your option) any later version.
#
#    Go Games Screensaver is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Go Games Screensaver.  If not, see 
#    <http://www.gnu.org/licenses/>.

import gtk
import os

class GsThemeWindow(gtk.Window):
    __gtype_name__ = 'GsThemeWindow'
    
    def __init__(self):
        super(GsThemeWindow, self).__init__()
        self.connect("destroy", gtk.main_quit)
        self.set_default_size(1000, 800)

    def do_realize(self):
        ident = os.environ.get('XSCREENSAVER_WINDOW')
        if not ident is None:
            self.window = gtk.gdk.window_foreign_new(int(ident, 16))
            self.window.set_events(gtk.gdk.EXPOSURE_MASK |
                                   gtk.gdk.STRUCTURE_MASK)
            x, y, w, h, depth = self.window.get_geometry()
            self.size_allocate(gtk.gdk.Rectangle(x, y, w, h))
            self.set_default_size(w, h)
            self.set_decorated(False)
        else:
            self.window = gtk.gdk.Window(
                self.get_parent_window(),
                width=self.allocation.width,
                height=self.allocation.height,
                window_type=gtk.gdk.WINDOW_TOPLEVEL,
                wclass=gtk.gdk.INPUT_OUTPUT,
                event_mask=self.get_events() | gtk.gdk.EXPOSURE_MASK)
        self.window.set_user_data(self)
        self.style.attach(self.window)
        self.set_flags(self.flags() | gtk.REALIZED)
