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
# Todo:
#   Display Pass moves?
#   Display Error messages?
#   Restructure code to not be quite so hideous

import gtk
import pango
import re

class AnnotationDisplay(gtk.VBox):

    prop_mapping = {'TE': "good move",
                    'KO': "ko",
                    'DO': "doubtful move",
                    'BM': "bad move",
                    'IT': "interesting move",
                    'DM': "even position",
                    'GB': "good for black",
                    'GW': "good for white",
                    'UC': "unclear position",
                    'HO': "hotspot"}

    base_size = 12
    game_info_spacing = 7
    ratio = 0.3
    margin = 0.02

    def __init__(self):
        super(AnnotationDisplay, self).__init__()
        self.game_info = {}
        self.annotations = {}
        self.labels = []
        self.font_desc = pango.FontDescription()
        self.font_desc.set_size(self.base_size * pango.SCALE)
        self.set_spacing(self.base_size)
        self.pack_game_info_display()
        self.pack_hr()
        self.pack_annotation_display()
        self.connect("expose_event", self.set_text_size)
    
    def pack_game_info_display(self):
        self.vbox = gtk.VBox()
        self.vbox.set_spacing(self.game_info_spacing)
        
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        label = gtk.Label()
        label.set_markup("<b>Black</b>")
        label.set_alignment(0.0, 0.5)
        self.labels.append(label)
        hbox.pack_start(label)
        self.bc_label = gtk.Label()
        self.bc_label.set_text("0 captures")
        self.bc_label.set_alignment(1.0, 0.5)
        self.labels.append(self.bc_label)
        hbox.pack_start(self.bc_label)
        vbox.pack_start(hbox)
        
        self.pb_label = gtk.Label()
        self.pb_label.set_alignment(0.0, 0.5)
        self.labels.append(self.pb_label)
        vbox.pack_start(self.pb_label)
        self.vbox.pack_start(vbox)
        
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        label = gtk.Label()
        label.set_markup("<b>White</b>")
        label.set_alignment(0.0, 0.5)
        self.labels.append(label)
        hbox.pack_start(label)
        self.wc_label = gtk.Label()
        self.wc_label.set_text("0 captures")
        self.wc_label.set_alignment(1.0, 0.5)
        self.labels.append(self.wc_label)
        hbox.pack_start(self.wc_label)
        vbox.pack_start(hbox)
        
        self.pw_label = gtk.Label()
        self.pw_label.set_alignment(0.0, 0.5)
        self.labels.append(self.pw_label)
        vbox.pack_start(self.pw_label)
        self.vbox.pack_start(vbox)
        
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        self.h_label = gtk.Label()
        self.h_label.set_alignment(0.0, 0.5)
        self.labels.append(self.h_label)
        hbox.pack_start(self.h_label)
        self.k_label = gtk.Label()
        self.k_label.set_alignment(1.0, 0.5)
        self.labels.append(self.k_label)
        hbox.pack_start(self.k_label)
        vbox.pack_start(hbox)
        
        self.r_label = gtk.Label()
        self.r_label.set_alignment(0.0, 0.5)
        self.labels.append(self.r_label)
        vbox.pack_start(self.r_label)
        self.vbox.pack_start(vbox)
        
        self.pack_start(self.vbox, expand=False)
        
        for label in self.labels:
            label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(1.0, 1.0, 1.0, 0))
            label.modify_font(self.font_desc)
        
    def pack_hr(self):
        self.hr_im = gtk.Image()
        self.set_hr_pixbuf(self.base_size * 200)
        self.pack_start(self.hr_im, expand=False)
    
    def set_hr_pixbuf(self, size):
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 500, 1)
        pixbuf.fill(0xffffffff)
        self.hr_im.set_from_pixbuf(pixbuf)

    def pack_annotation_display(self):
        self.text_view = gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_cursor_visible(False)
        self.text_view.set_wrap_mode(gtk.WRAP_WORD_CHAR)
        buff = self.text_view.get_buffer()
        buff.create_tag("bold", weight = pango.WEIGHT_BOLD)
        buff.create_tag("italic", style = pango.STYLE_ITALIC)
        self.text_view.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(0, 0, 0, 0))
        self.text_view.modify_text(gtk.STATE_NORMAL, 
                                                gtk.gdk.Color(1.0, 1.0, 1.0, 0))
        self.pack_start(self.text_view)
        
    @staticmethod
    def set_text_size(self, event):
        scale = float(self.get_toplevel().get_size()[0]) / \
                                                    gtk.gdk.Screen().get_width()
        self.set_spacing(int(scale*self.base_size))
        self.font_desc.set_size(int(round(scale*self.base_size*pango.SCALE)))
        for label in self.labels:
            label.modify_font(self.font_desc)
        self.text_view.modify_font(self.font_desc)
        self.vbox.set_spacing(int(scale * self.game_info_spacing))
        self.set_hr_pixbuf(int(scale * self.base_size * 200))
        
    def update_text_output(self):
        self.update_game_info()
        self.update_annotations()
    
    def update_game_info(self):
        b_str = format_simpletext(self.game_info.get("PB", "?"))
        if not self.game_info.get("BR") == None:
            b_str += " (%s)" % format_simpletext(self.game_info["BR"])
        w_str = format_simpletext(self.game_info.get("PW", "?"))
        if not self.game_info.get("WR") == None:
            w_str += " (%s)" % format_simpletext(self.game_info["WR"])
        h_str = format_simpletext(self.game_info.get("HA", "?"))
        k_str = format_simpletext(self.game_info.get("KM", "?"))
        r_str = format_simpletext(self.game_info.get("RE", "?"))
        self.pb_label.set_text(b_str)
        self.pw_label.set_text(w_str)
        self.bc_label.set_text("%s captures" % self.prisoners[1])
        self.wc_label.set_text("%s captures" % self.prisoners[-1])
        self.h_label.set_markup("<b>Handicap:</b> %s" % h_str)
        self.k_label.set_markup("<b>Komi:</b> %s" % k_str)
        self.r_label.set_markup("<b>Result:</b> %s" % r_str)
        
    def update_annotations(self):
        buff = self.text_view.get_buffer()
        buff.delete(buff.get_start_iter(), buff.get_end_iter())
        my_iter = buff.get_start_iter()
        
        buff.set_modified(False)
        if not self.annotations.get("N") == None:
            text = self.format_simpletext(self.annotations["N"]) + "\n"
            buff.insert_with_tags_by_name(my_iter, text, "bold")
        if not self.annotations.get("V") == None:
            buff.insert_with_tags_by_name(my_iter, "Estimated score: %s" % 
                                          self.annotations["V"], "italic")
        for prop, val in self.annotations.iteritems():
            if not self.prop_mapping.get(prop) == None:
                text = (("very " if val == 2 else "") + self.prop_mapping[prop]
                        + ".\n").capitalize()
                buff.insert_with_tags_by_name(my_iter, text, "italic")
        if not self.annotations.get("C") == None:
            if buff.get_modified():
                buff.insert(my_iter, "\n")
            buff.insert(my_iter, format_text(self.annotations["C"]))

def format_text(text):
    text = re.sub(r"[\t\v]", " ", text)
    text = re.sub(r"\r\n|\n\r|\r|\n", "\n", text)
    text = text.replace("\\\n", "")
    text = re.sub(r"\\(.)", r'\1', text)
    return text

def format_simpletext(text):
    return format_text(text).replace("\n", " ")

