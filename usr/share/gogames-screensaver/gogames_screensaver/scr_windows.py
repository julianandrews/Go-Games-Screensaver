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
#
# Todo
#   deal with unwated sys.argv variables
#   Find gtk native solution to windows messages stuff
#   Make preview window shutdown gracefully if interupted while getting uris
#   handle parenting issues for config windows

import gtk
import gobject
import sys
import win32api
import win32con
import win32gui

def get_mode():
    mode = None
    handle = None
    #del_list = []
    for i, (opt, next_opt) in enumerate(zip(sys.argv, sys.argv[1:] + [None])):
        if opt[0] in ('/', '-') and len(opt) > 1:
            if opt[1].lower() in ('c', 'p', 's'):
                mode = mode or opt[1].lower()
                #del_list.append(i)
                try:
                    if len(opt) > 3 and opt[2] == ':':
                        new_handle = int(opt[3:])
                    elif not next_opt is None:
                        new_handle = int(next_opt)
                        #del_list.append(i+1)
                    else:
                        new_handle = None
                    handle = handle or new_handle
                except ValueError:
                    handle = handle or None
    #for i in reversed(del_list):
    #    del sys.argv[i]
    return mode or 's', handle

class WinSSWindow(gtk.Window):
    __gtype_name__ = 'WinSSWindow'
    mouse_threshold = 20

    def __init__(self):
        super(WinSSWindow, self).__init__(gtk.WINDOW_POPUP)
        self.mouse_pos = None
        self.connect("destroy", gtk.main_quit)
        self.mode, self.handle = get_mode()

    def do_realize(self):
        if self.mode == 's':
            self.fullscreen()
            self.window = gtk.gdk.Window(
                self.get_parent(),
                gtk.gdk.screen_width(),
                gtk.gdk.screen_height(),
                gtk.gdk.WINDOW_TOPLEVEL,
                gtk.gdk.ALL_EVENTS_MASK,
                gtk.gdk.INPUT_OUTPUT)
            pixmap = gtk.gdk.Pixmap(None, 1, 1, 1)
            color = gtk.gdk.Color()
            gtk.gdk.pointer_grab(self.window, False, gtk.gdk.ALL_EVENTS_MASK, 
                      cursor=gtk.gdk.Cursor(pixmap, pixmap, color, color, 0, 0))
            gtk.gdk.keyboard_grab(self.window)
            self.window.set_keep_above(True)
            self.connect("motion-notify-event", self.handle_mouse_motion)
            self.connect("key-press-event", self.shutdown)
            self.connect("button-press-event", self.shutdown)
            self.oldwndproc = win32gui.SetWindowLong(self.window.handle,   
                                             win32con.GWL_WNDPROC, self.wndproc)
            gobject.idle_add(gtk.gdk.threads_init)
        elif self.mode == 'p':
            parent_window = gtk.gdk.window_foreign_new(self.handle)
            x, y, w, h, depth = parent_window.get_geometry()
            self.window = gtk.gdk.Window(
                parent_window,
                width = w,
                height = h,
                window_type = gtk.gdk.WINDOW_TOPLEVEL,
                wclass = gtk.gdk.INPUT_OUTPUT,
                event_mask = gtk.gdk.EXPOSURE_MASK | gtk.gdk.STRUCTURE_MASK)
            self.set_destroy_with_parent(True)
            self.size_allocate(gtk.gdk.Rectangle(x, y, w, h))
            self.set_size_request(w, h)
        self.set_decorated(False)
        self.window.set_user_data(self)
        self.style.attach(self.window)
        self.set_flags(self.flags() | gtk.REALIZED)

    @staticmethod
    def handle_mouse_motion(self, event):
        """Only respond to mouse motion above a threshold."""
        if self.mouse_pos is None:
            self.mouse_pos = (event.x, event.y)
        elif abs(self.mouse_pos[0]-event.x) > self.mouse_threshold or \
                          abs(self.mouse_pos[1]-event.y) > self.mouse_threshold:
            self.shutdown()

    def shutdown(self, *args):
        """Avoid repeat calls to gtk.main_quit()."""
        win32api.SetWindowLong(self.window.handle, win32con.GWL_WNDPROC, 
                                                                self.oldwndproc)
        self.destroy()

    def wndproc(self, hwnd, msg, wparam, lparam):
        """We want to shutdown on certain windows messages."""
        if msg == win32con.WM_CLOSE or (msg in (win32con.WM_ACTIVATE, 
                                       win32con.WM_ACTIVATEAPP) and not wparam):
            self.shutdown()
        else:
            return win32gui.CallWindowProc(self.oldwndproc, hwnd, msg, wparam,
                                           lparam)
