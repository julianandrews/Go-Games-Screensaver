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
