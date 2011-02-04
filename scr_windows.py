# Copyright (c) 2010 Julian Andrews.
# All rights reserved.
#
# This software is provided for personal use only, and may not be 
# redistributed in whole or in part or used for any comercial purpose without
# the permision of the copyright holder.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY 
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL 
# JULIAN ANDREWS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# I will probably release this with a more permissive license at some later
# date, but for the moment want to keep my options open until I decide how
# best to distribute it.

import gtk
import os
import sys
import win32api
import win32con
import win32gui

def get_mode():
    mode = 's'
    handle = None
    for i, (opt, next_opt) in enumerate(zip(sys.argv, sys.argv[1:] + [None])):
        if opt[0] in ('/', '-'):
            if opt[1] in ('s', 'c', 'p', 'S', 'C', 'P'):
                mode = opt[1].lower()
                if mode in ('p', 'c'):
                    if len(opt) > 3 and opt[2] == ':':
                        handle = int(opt[3:])
                    else:
                        try:
                            handle = int(next_opt)
                        except (TypeError, ValueError):
                            handle = None
                break
    return mode, handle

class WinSSWindow(gtk.Window):
    __gtype_name__ = 'WinSSWindow'
    __gsignals__ = {'size-request': 'override'}
    
    def __init__(self):
        super(WinSSWindow, self).__init__(gtk.WINDOW_POPUP)
        self.connect("destroy", gtk.main_quit)
        self.mode, self.handle = get_mode()

    def do_realize(self):
        if self.mode == 's':
            self.fullscreen()
            self.window = gtk.gdk.Window(
                self.get_parent(),
                width = self.allocation.width,
                height = self.allocation.height,
                window_type = gtk.gdk.WINDOW_TOPLEVEL,
                wclass = gtk.gdk.INPUT_OUTPUT,
                event_mask = gtk.gdk.ALL_EVENTS_MASK)
            self.window.set_keep_above(True)
            pixmap = gtk.gdk.Pixmap(None, 1, 1, 1)
            color = gtk.gdk.Color()
            cursor = gtk.gdk.Cursor(pixmap, pixmap, color, color, 0, 0)
            self.window.set_cursor(cursor)
            self.mne_id = self.connect("motion-notify-event", self.eat_event)
            self.connect("button-press-event", gtk.main_quit)
            self.connect("key-press-event", gtk.main_quit)
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
            self.size_allocate(gtk.gdk.Rectangle(x, y, w, h))
            self.set_default_size(w, h)
        self._oldwndproc = win32gui.SetWindowLong(self.window.handle,   
                                            win32con.GWL_WNDPROC, self._wndproc)
        self.set_decorated(False)
        self.window.set_user_data(self)
        self.set_flags(self.flags() | gtk.REALIZED)
        self.style.attach(self.window)

    @staticmethod
    def do_size_request(req):
        pass
    
    def eat_event(self, *args):
        self.disconnect(self.mne_id)
        self.connect("motion-notify-event", gtk.main_quit)
        
    def _wndproc(self, hwnd, msg, wparam, lparam):
        if msg in (win32con.WM_CLOSE, win32con.WM_ACTIVATE, 
                                                       win32con.WM_ACTIVATEAPP):
            try:
                gtk.main_quit()
            except RuntimeError, e:
                if not str(e) == "called outside of a mainloop":
                    raise
        else:
            return win32gui.CallWindowProc(self._oldwndproc, hwnd, msg, wparam,
                                           lparam)
