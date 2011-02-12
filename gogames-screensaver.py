#!/usr/bin/env python
#
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
import glib

import annotation_display
import config
import goban_display
import sgfsources

from os_wrapper import *
        
class GobanHBox(gtk.HBox):
    __gsignals__ = {'size-allocate': 'override'}

    margin_ratio = 0.07
    abox_ratio = 0.3
    abox_margin = 0.02
    
    def __init__(self):
        gtk.HBox.__init__(self)
        self.sgf_source = sgfsources.MultiSource(conf['sources'], 
                                                 conf['sgf_folder'])
        self.goban_display = goban_display.GobanDisplay(conf['markup'], 
                                                        conf.get('dark', False))
        self.pack_start(self.goban_display)
        self.abox = annotation_display.AnnotationDisplay()
        if conf['annotations']:
            self.pack_start(self.abox)
        self.new_game()
        
    def do_size_allocate(self, alloc):
        margin = alloc.height * self.margin_ratio
        width_ratio = 1.0 + (self.abox_ratio if conf['annotations'] else 0)
        if (alloc.width + 2 * margin)/ (alloc.height + 2 * margin) > width_ratio:
            height = int(alloc.height - 2 * margin)
        else:
            height = int((alloc.width - 2 * margin) / width_ratio)
        width = int(height * width_ratio)
        x = alloc.x + (alloc.width - width)/2
        y = alloc.y + (alloc.height - height)/2
        self.goban_display.size_allocate((x, y, height, height))
        self.abox.size_allocate((int(x + height * (1.0 + self.abox_margin)), 
                                 int(y + height * self.abox_margin), 
                                 int(width - height * (1.0 - self.abox_margin)), 
                                 int(height * (1.0 - 2 * self.abox_margin))))

    def load_game_node(self):
        self.goban_display.game_node = self.sgf_source.get_random_game()
        self.goban_display.queue_draw()
        self.update_annotations()
        
    def new_game(self):
        self.load_game_node()
        glib.timeout_add(conf['start_delay'], self.run)
    
    def run(self):
        if not self.goban_display.game_node.child_nodes == []:
            self.goban_display.game_node = self.goban_display.game_node[0]
            self.goban_display.queue_draw()
            self.update_annotations()
            glib.timeout_add(conf['move_delay'], self.run)
        else:
            glib.timeout_add(conf['end_delay'], self.new_game)
            
    def update_annotations(self):
        self.abox.game_info = self.goban_display.game_node.game_info
        self.abox.annotations = self.goban_display.game_node.annotations
        self.abox.prisoners = self.goban_display.game_node.goban.prisoners
        self.abox.update_text_output()

if __name__ == "__main__":
    conf = config.Configuration()
    if conf.get('mode') == 'c':
        window = config.SSConfigWindow(conf)
    else:
        window = SSWindow()
        window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0, 0, 0, 0))
        if conf["fullscreen"]:
            window.fullscreen()
        window.add(GobanHBox())
    window.show_all()
    gtk.main()
