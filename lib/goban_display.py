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
#   Support LB markup property
#   Clean up VW property
#   Optionally draw coordinates around board edge?

import cairo
import gtk
import math
import os
import rsvg

from os_wrapper import data_folder

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
    
    def __init__(self, should_draw_markup=True, darken=False):
        super(GobanDisplay, self).__init__()
        self.should_draw_markup = should_draw_markup
        self.darken = darken
        self.board_size = 19
        self.game_node = None

    def do_expose_event(self, event):
        cr = self.window.cairo_create()
        new_size = self.window.get_size()[0]
        if (not hasattr(self, 'clean_board_surf') or 
            not self.clean_board_surf.get_width() == new_size or 
            (not self.game_node is None and 
             not self.game_node.goban.size == self.board_size)):
            if not self.game_node is None:
                self.board_size = self.game_node.goban.size
            self.gen_board(new_size)
        cr.rectangle(event.area.x, event.area.y, 
                     event.area.width, event.area.height)
        cr.clip()
        self.draw(cr)
        
    def draw_to_file(self, size, filename):
        draw_size = max(128, size)
        self.gen_board(draw_size)
        surf = cairo.ImageSurface(0, draw_size, draw_size)
        self.draw(cairo.Context(surf))
        if not draw_size == size:
            new_surf = cairo.ImageSurface(0, size, size)
            cr = cairo.Context(new_surf)
            pat = cairo.SurfacePattern(surf)
            cr.set_source(pat)
            cr.paint()
            surf = new_surf
        surf.write_to_png(filename)

    @staticmethod
    def draw_MA(cr, offset, scale):
        cr.move_to(offset[0] + scale/4, offset[1]+scale/4)
        cr.rel_line_to(scale/2, scale/2)
        cr.move_to(offset[0]+scale/4, offset[1]+3*scale/4)
        cr.rel_line_to(scale/2, -scale/2)
        cr.stroke()

    @staticmethod
    def draw_CR(cr, offset, scale):
        cr.move_to(offset[0] + 4*scale/5, offset[1] + scale/2)
        cr.arc(offset[0] + scale/2, offset[1] + scale/2, scale*3/10, 0, 
               2 * math.pi)
        cr.stroke()
        
    @staticmethod
    def draw_TR(cr, offset, scale):
        a = scale
        s = math.sqrt(3)
        cr.move_to(offset[0] + scale / 2, offset[1] + scale / 5)
        cr.line_to(offset[0] + (1 - 3 * s / 10) * scale / 2, 
                   offset[1] + 13 * scale / 20)
        cr.line_to(offset[0] + (1 + 3 * s / 10) * scale / 2, 
                   offset[1] + 13 * scale / 20)
        cr.close_path()
        cr.stroke()
        
    @staticmethod
    def draw_SQ(cr, offset, scale):
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
        
    @staticmethod
    def draw_Plus(cr, offset, scale):
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
        cr.set_source_surface(self.clean_board_surf)
        cr.rectangle(offset[0]-2, offset[1]-2, scale + 4, scale + 4)
        cr.fill()
    
    def draw(self, cr):
        if not self.game_node is None:
            self.draw_stones()
        cr.set_source_surface(self.board_cr.get_target())
        cr.paint()
        if self.should_draw_markup and not self.game_node is None:
            self.draw_markup(cr)
        if self.darken:
            cr.set_source_rgba(0, 0, 0, 0.80)
            cr.paint()
        
    def gen_board(self, bw):
        """Sets self.clean_board_surf, self.board_cr, and self.scale"""
        self.scale = bw / (2.0 * self.board_margin + 
                               (self.board_size - 1.0) * self.line_spacing)
        w = self.line_spacing * (self.board_size - 1) * self.scale
        m = self.board_margin * self.scale
        self.clean_board_surf = cairo.ImageSurface(0, bw, bw)
        cr = cairo.Context(self.clean_board_surf)
        cr.set_source_rgb(*self.board_color)
        cr.rectangle(0, 0, bw, bw)
        cr.fill()
        cr.set_source_rgb(*self.line_color)
        cr.set_line_width(max(1, int(self.heavy_line_width * self.scale)))
        cr.rectangle(m, m, w, w)
        cr.stroke()
        cr.set_line_width(max(1, int(self.line_width * self.scale)))
        for i in (0, 1):
            for j in range(2, self.board_size):
                start = self.point_map((1, j) if i == 0 else (j, 1))
                end = self.point_map((self.board_size, j) if i == 0 else 
                                     (j, self.board_size))
                cr.move_to(*start)
                cr.line_to(*end)
            cr.stroke()
        hoshi_list = self.hoshi_lists.get(self.board_size, ())
        cr.set_source_rgb(*self.line_color)
        for point in hoshi_list:
            x, y = self.point_map(point)
            cr.arc(x, y, int(self.hoshi_radius * self.scale), 0, 2 * math.pi)
            cr.fill()
        board_surf = cairo.ImageSurface(0, bw, bw)
        self.board_cr = cairo.Context(board_surf)
        self.board_cr.set_source_surface(self.clean_board_surf)
        self.board_cr.paint()
        self.old_stones = {}
        
    def draw_stones(self):
        cr = self.board_cr
        new_stones = []
        removed_points = tuple(p for (p, c) in self.old_stones.iteritems() 
                               if not self.game_node.goban.get(p) == c)
        redraw_points = []
        for point in removed_points:
            if not self.old_stones.get(point) == None:
                del self.old_stones[point]
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    if i == j == 0:
                        continue
                    p = (point[0] + i, point[1] + j)
                    if not self.old_stones.get(p) == None:
                        redraw_points.append(p)
                        del self.old_stones[p]
        for point, color in self.game_node.goban.iteritems():
            if color == 0:
                continue
            if not self.old_stones.get(point, 0) == color:
                new_stones.append((point, color))
                self.old_stones[point] = color
        for point in removed_points:
            self.draw_markup_at_point(self.board_cr, 'EmptyPoint', 0, point)
        for point, color in new_stones:
            alpha = 0.5 if any(point in self.game_node.markup.get(prop_id, ()) 
                               for prop_id in ("TB", "TW", "DD")) else 1.0
            svg = self.stone_ims[color]
            s = 2.0 * self.stone_radius * self.scale / svg.props.width
            cr.translate(*map(lambda x: x - int(self.stone_radius * 
                                           self.scale), self.point_map(point)))
            cr.scale(s, s)
            if point in redraw_points:
                cr.push_group()
                svg.render_cairo(cr)
                pat = cr.pop_group()
                cr.set_source_surface(self.clean_board_surf)
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
            self.draw_markup_at_point(cr, "Plus", color, last_stone)
        if not self.game_node.markup.get('VW') == None:
            for point in self.game_node.goban:
                if not point in self.game_node.markup['VW']:
                    self.draw_markup_at_point(cr, 'NotShowing', 0, point)
                               
    def draw_markup_at_point(self, cr, prop_id, stone_color, point):
        cr.set_line_width(int(self.markup_line_width * self.scale))
        cr.set_source_rgb(*self.markup_colors[stone_color])
        offset = map(lambda x: x - self.stone_radius * self.scale, 
                     self.point_map(point))
        cr.move_to(0, 0)
        eval("self.draw_%s" % prop_id)(cr, offset, 
                                       self.scale * self.line_spacing)
    
    def draw_line(self, cr, (a, b), prop_id):
        col = self.markup_line_cols[prop_id]
        cr.set_line_width(int(self.markup_line_width * self.scale))
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
            cr.rel_line_to(arrowhead_width * self.scale / 2, 
                           arrowhead_height * self.scale / 2)
            cr.rel_line_to(-arrowhead_width * self.scale, 0)
            cr.close_path()
            cr.fill()
            cr.identity_matrix()

    def point_map(self, point):
        return map(lambda x: int(self.scale * (self.board_margin + 
                                 self.line_spacing * (x - 1))), point)

