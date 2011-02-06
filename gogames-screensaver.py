#!/usr/bin/env python
#
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
#
# Todo
#   Support LB markup property
#   Display Pass moves
#   Rework text formating
#   Clean up VW property

import cairo
import gtk
import gobject
import math
import optparse
import os
import pango
import random
import re
import rsvg

import config
import sgfsources

from os_wrapper import *
        
class GobanHBox(gtk.HBox):
    __gsignals__ = {'size-allocate': 'override'}

    margin_ratio = 0.07
    abox_ratio = 0.3
    abox_margin = 0.02
    
    def __init__(self):
        gtk.HBox.__init__(self)
        self.sgf_source = sgfsources.MultiSource(conf['sources'])
        self.goban_display = GobanDisplay()
        self.pack_start(self.goban_display)
        self.abox = AnnotationDisplay()
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
        gobject.timeout_add(conf['start_delay'], self.run)
    
    def run(self):
        if not self.goban_display.game_node.child_nodes == []:
            self.goban_display.game_node = self.goban_display.game_node[0]
            self.goban_display.queue_draw()
            self.update_annotations()
            gobject.timeout_add(conf['move_delay'], self.run)
        else:
            gobject.timeout_add(conf['end_delay'], self.new_game)
            
    def update_annotations(self):
        self.abox.game_info = self.goban_display.game_node.game_info
        self.abox.annotations = self.goban_display.game_node.annotations
        self.abox.prisoners = self.goban_display.game_node.goban.prisoners
        self.abox.update_text_output()
           
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

    def __init__(self):
        super(AnnotationDisplay, self).__init__()
        self.game_info = {}
        self.annotations = {}
        self.labels = []
        self.font_desc = pango.FontDescription()
        self.font_desc.set_size(self.base_size*pango.SCALE)
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
        hr_pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 1000, 1)
        hr_pixbuf.fill(0xffffffff)
        hr_im = gtk.image_new_from_pixbuf(hr_pixbuf)
        self.pack_start(hr_im, expand=False)
    
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
        self.vbox.set_spacing(int(scale*self.game_info_spacing))
        
    def update_text_output(self):
        self.update_game_info()
        self.update_annotations()
    
    def update_game_info(self):
        b_str = self._format_simpletext(self.game_info.get("PB", "?"))
        if not self.game_info.get("BR") == None:
            b_str += " (%s)" % self._format_simpletext(self.game_info["BR"])
        w_str = self._format_simpletext(self.game_info.get("PW", "?"))
        if not self.game_info.get("WR") == None:
            w_str += " (%s)" % self._format_simpletext(self.game_info["WR"])
        h_str = self._format_simpletext(self.game_info.get("HA", "?"))
        k_str = self._format_simpletext(self.game_info.get("KM", "?"))
        r_str = self._format_simpletext(self.game_info.get("RE", "?"))
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
            text = self._format_simpletext(self.annotations["N"]) + "\n"
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
            buff.insert(my_iter, self._format_text(self.annotations["C"]))

    @staticmethod
    def _format_text(text):
        text = re.sub(r"[\t\v]", " ", text)
        text = re.sub(r"\r\n|\n\r|\r|\n", "\n", text)
        text = text.replace("\\\n", "")
        text = re.sub(r"\\(.)", r'\1', text)
        return text
        
    @staticmethod
    def _format_simpletext(text):
        text = AnnotationDisplay._format_text(text)
        text = text.replace("\n", " ")
        return text

class GobanDisplay(gtk.DrawingArea):
    __gsignals__ = {"expose_event": "override"}
    stone_ims = {-1: rsvg.Handle(os.path.join(data_folder, "images", 
                                              "white_stone.svg")),
                 1: rsvg.Handle(os.path.join(data_folder, "images", 
                                             "black_stone.svg"))}
    hoshi_lists = {9: ((3,3), (3,7), (7,3), (7,7)),
                   13: ((4,4), (4,10), (7,7), (10,4), (10,10)),
                   19: ((4,4), (4,10), (4,16),
                        (10,4), (10,10), (10,16),
                        (16,4), (16,10), (16,16))}
    bg_color = (0.0, 0.0, 0.0)
    board_color = (0.9, 0.73, 0.37)
    line_color = (0.0, 0.0, 0.0)
    markup_colors = {1: (0.8, 0.8, 0.8), -1: (0.2, 0.2, 0.2), 
                     0: (1.0, 1.0, 1.0)}
    markup_line_cols = {"LN": (0.0, 0.0, 1.0), "AR": (0.0, 1.0, 0.0)}
    SL_color = (0.2, 0.75, 0.2)
    board_margin = 14.1
    line_spacing = 22.0
    stone_radius = 11.2
    line_width = 1.0
    heavy_line_width = 2.0
    markup_line_width = 1.5
    hoshi_radius = 2.0
    
    def __init__(self):
        super(GobanDisplay, self).__init__()
        self.board_size = 19
        self.size = None
        self.game_node = None
        self.current_stones = {}
        self.clean_board_cr = None
        self.board_cr = None
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0, 0, 0, 0))

    def do_expose_event(self, event):
        new_size = self.window.get_size()
        if not (new_size == self.size and self.game_node.goban.size == 
                                                               self.board_size):
            self.board_size = self.game_node.goban.size
            self.size = new_size
            self.gen_board()
            self.current_stones = {}
        cr = self.window.cairo_create()
        cr.rectangle(event.area.x, event.area.y, 
                     event.area.width, event.area.height)
        cr.clip()
        self.draw(cr)

    @classmethod
    def draw_MA(cls, cr, offset, scale):
        cr.move_to(offset[0] + scale/4, offset[1]+scale/4)
        cr.rel_line_to(scale/2, scale/2)
        cr.move_to(offset[0]+scale/4, offset[1]+3*scale/4)
        cr.rel_line_to(scale/2, -scale/2)
        cr.stroke()

    @classmethod
    def draw_CR(cls, cr, offset, scale):
        cr.move_to(offset[0] + 4*scale/5, offset[1] + scale/2)
        cr.arc(offset[0] + scale/2, offset[1] + scale/2, scale*3/10, 0, 
               2 * math.pi)
        cr.stroke()
        
    @classmethod
    def draw_TR(cls, cr, offset, scale):
        a = scale
        s = math.sqrt(3)
        cr.move_to(offset[0] + scale / 2, offset[1] + scale / 5)
        cr.line_to(offset[0] + (1 - 3 * s / 10) * scale / 2, 
                   offset[1] + 13 * scale / 20)
        cr.line_to(offset[0] + (1 + 3 * s / 10) * scale / 2, 
                   offset[1] + 13 * scale / 20)
        cr.close_path()
        cr.stroke()
        
    @classmethod
    def draw_SQ(cls, cr, offset, scale):
        cr.rectangle(offset[0]+scale/4+0.5, offset[1]+scale/4+0.5, 
                     scale/2-1, scale/2-1)
        cr.stroke()
    
    @classmethod
    def draw_SL(cls, cr, offset, scale):
        cr.set_source_rgb(*cls.SL_color)
        cls.draw_MA(cr, offset, scale)
        
    @classmethod
    def draw_TB(cls, cr, offset, scale):
        cls.draw_Tx(cr, offset, scale, 1)
    
    @classmethod
    def draw_TW(cls, cr, offset, scale):
        cls.draw_Tx(cr, offset, scale, -1)
        
    @classmethod
    def draw_Tx(cls, cr, offset, scale, col):
        svg = cls.stone_ims[col]
        s = 0.5 * scale / svg.props.width
        cr.translate(offset[0]+scale/4, offset[1]+scale/4)
        cr.scale(s, s)
        svg.render_cairo(cr)
        cr.identity_matrix()
        
    @classmethod
    def draw_DD(cls, cr, offset, scale):
        pass
        
    @classmethod
    def draw_LastStone(cls, cr, offset, scale):
        cr.move_to(*offset)
        cr.rel_move_to(scale/2, scale/4)
        cr.rel_line_to(0, scale/2)
        cr.move_to(*offset)
        cr.rel_move_to(scale/4, scale/2)
        cr.rel_line_to(scale/2, 0)
        cr.stroke()
    
    @classmethod
    def draw_NotShowing(cls, cr, offset, scale):
        cr.set_source_rgba(*(list(cls.bg_color) + [0.8]))
        cr.rectangle(offset[0], offset[1], scale+0.5, scale+0.5)
        cr.fill()

    def draw_EmptyPoint(self, cr, offset, scale):
        cr.set_source(cairo.SurfacePattern(self.clean_board_cr.get_target()))
        cr.rectangle(offset[0]-2, offset[1]-2, scale + 4, scale + 4)
        cr.fill()
    
    def draw(self, cr):
        self.draw_stones()
        cr.set_source(cairo.SurfacePattern(self.board_cr.get_target()))
        cr.paint()
        if conf['markup']:
            self.draw_markup(cr)
        
    def gen_board(self):
        scale = self.get_scale()
        cr = self.new_board_scaled_cr()
        bw = cr.get_target().get_width()
        m = scale * self.board_margin
        w = bw - 2 * m
        cr.set_source_rgb(*self.board_color)
        cr.rectangle(0, 0, bw, bw)
        cr.fill()
        cr.set_source_rgb(*self.line_color)
        cr.set_line_width(max(1, int(self.heavy_line_width*scale)))
        cr.rectangle(m, m, w, w)
        cr.stroke()
        cr.set_line_width(max(1, int(self.line_width*scale)))
        for i in (0, 1):
            for j in range(2, self.board_size):
                start = self.point_map((1, j) if i == 0 else (j, 1))
                end = self.point_map((self.board_size, j) if i == 0 else 
                                     (j, self.board_size))
                cr.move_to(*start)
                cr.line_to(*end)
            cr.stroke()
        if not self.board_size in (9, 13, 19):
            hoshi_list = ()
        else:
            hoshi_list = self.hoshi_lists[self.board_size]
        cr.set_source_rgb(*self.line_color)
        for point in hoshi_list:
            x, y = self.point_map(point)
            cr.arc(x, y, int(self.hoshi_radius * scale), 0, 2 * math.pi)
            cr.fill()
        self.clean_board_cr = cr
        self.board_cr = self.new_board_scaled_cr()
        self.board_cr.set_source(cairo.SurfacePattern(
                                 self.clean_board_cr.get_target()))
        self.board_cr.paint()
        
    def draw_stones(self):
        cr = self.board_cr
        scale = self.get_scale()
        new_stones = []
        removed_points = tuple(p for (p, c) in self.current_stones.iteritems() 
                               if not self.game_node.goban.get(p) == c)
        redraw_points = []
        for point in removed_points:
            if not self.current_stones.get(point) == None:
                del self.current_stones[point]
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    if i == j == 0:
                        continue
                    p = (point[0] + i, point[1] + j)
                    if not self.current_stones.get(p) == None:
                        redraw_points.append(p)
                        del self.current_stones[p]
        for point, color in self.game_node.goban.iteritems():
            if color == 0:
                continue
            if not self.current_stones.get(point, 0) == color:
                new_stones.append((point, color))
                self.current_stones[point] = color
        for point in removed_points:
            self.draw_markup_at_point(self.board_cr, 'EmptyPoint', 0, point)
        for point, color in new_stones:
            alpha = 0.5 if any(point in self.game_node.markup.get(prop_id, ()) 
                               for prop_id in ("TB", "TW", "DD")) else 1.0
            svg = self.stone_ims[color]
            s = 2.0 * self.stone_radius * scale / svg.props.width
            cr.translate(*map(lambda x: x - int(self.stone_radius * scale), 
                              self.point_map(point)))
            cr.scale(s, s)
            if point in redraw_points:
                cr.push_group()
                svg.render_cairo(cr)
                pat = cr.pop_group()
                cr.set_source(cairo.SurfacePattern(
                              self.clean_board_cr.get_target()))
                cr.mask(pat)
            cr.push_group()
            svg.render_cairo(cr)
            cr.pop_group_to_source()
            cr.paint_with_alpha(alpha)
            cr.identity_matrix()
            
    def draw_markup(self, cr):
        for prop_id, prop_vals in self.game_node.markup.iteritems():
            if prop_id in ('LB', 'VW'):
                continue
            elif prop_id in ('AR', 'LN'):
                for point_pair in prop_vals:
                    self.draw_line(cr, point_pair, prop_id)
            else:
                for point in prop_vals:
                    color = self.game_node.goban[point]
                    self.draw_markup_at_point(cr, prop_id, color, point)
        last_stone = self.game_node.goban.last_stone
        if not last_stone == None:
            color = self.game_node.goban[last_stone]
            self.draw_markup_at_point(cr, "LastStone", color, last_stone)
        if not self.game_node.markup.get('VW') == None:
            for point in self.game_node.goban:
                if not point in self.game_node.markup['VW']:
                    self.draw_markup_at_point(cr, 'NotShowing', 0, point)
                               
    def draw_markup_at_point(self, cr, prop_id, stone_color, point):
        scale = self.get_scale()
        cr.set_line_width(int(self.markup_line_width*scale))
        cr.set_source_rgb(*self.markup_colors[stone_color])
        offset = map(lambda x: x - self.stone_radius * scale, 
                     self.point_map(point))
        cr.move_to(0, 0)
        eval("self.draw_%s" % prop_id)(cr, offset, scale*self.line_spacing)
    
    def draw_line(self, cr, (a, b), prop_id):
        col = self.markup_line_cols[prop_id]
        scale = self.get_scale()
        cr.set_line_width(int(self.markup_line_width*scale))
        cr.set_source_rgb(*col)
        start = self.point_map(a)
        end = self.point_map(b)
        cr.move_to(*start)
        cr.line_to(*end)
        cr.stroke()
        if prop_id == 'AR':
            arrowhead_height = 20
            arrowhead_width = 7
            theta = math.atan2(a[1]-b[1], a[0]-b[0]) - math.pi/2
            cr.translate(*end)
            cr.rotate(theta)
            cr.translate(-end[0], -end[1])
            cr.move_to(*end)
            cr.rel_line_to(arrowhead_width*scale/2, arrowhead_height*scale/2)
            cr.rel_line_to(-arrowhead_width*scale, 0)
            cr.close_path()
            cr.fill()
            cr.identity_matrix()

    def point_map(self, point):
        scale = self.get_scale()
        return map(lambda x: int(scale * (self.board_margin + 
                                 self.line_spacing * (x - 1))), point)
        
    def new_board_scaled_cr(self):
        scale = self.get_scale()
        w = self.line_spacing * (self.board_size - 1) * scale
        m = self.board_margin * scale
        bw = int(w + 2 * m)
        surf = cairo.ImageSurface(0, bw, bw)
        return cairo.Context(surf)

    def get_scale(self):
        return self.size[0] / (2.0 * self.board_margin + 
                               (self.board_size - 1.0) * self.line_spacing)

if __name__ == "__main__":
    conf = config.Configuration()
    if conf.get('mode') == 'c':
        window = config.SSConfigWindow(conf)
    else:
        window = SSWindow()
        window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0, 0, 0, 0))
        window.add(GobanHBox())
    window.show_all()
    gtk.main()
