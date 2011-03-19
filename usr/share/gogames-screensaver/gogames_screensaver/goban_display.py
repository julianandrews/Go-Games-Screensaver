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
#   Optionally draw coordinates around board edge?

import cairo
import gtk
import math
import os
import rsvg

from constants import data_folder

class GobanDisplay(gtk.DrawingArea):
    __gsignals__ = {"expose_event": "override"}
    stone_svgs = {-1: rsvg.Handle(os.path.join(data_folder, "images", 
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
        self.board_size = self.game_node.goban.size
        self.gen_board(draw_size)
        surf = cairo.ImageSurface(0, draw_size, draw_size)
        self.draw(cairo.Context(surf))
        if not draw_size == size:
            new_surf = cairo.ImageSurface(0, size, size)
            new_cr = cairo.Context(new_surf)
            new_cr.set_source_surface(surf)
            new_cr.paint()
            surf = new_surf
        surf.write_to_png(filename)
        
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

    @staticmethod
    def draw_MA(cr):
        cr.move_to(0.25, 0.25)
        cr.rel_line_to(0.5, 0.5)
        cr.move_to(0.25, 0.75)
        cr.rel_line_to(0.5, -0.5)
        cr.stroke()

    @staticmethod
    def draw_CR(cr):
        cr.move_to(0.8, 0.5)
        cr.arc(0.5, 0.5, 0.3, 0, 2 * math.pi)
        cr.stroke()
        
    @staticmethod
    def draw_TR(cr):
        s = math.sqrt(3)
        cr.move_to(0.5, 0.2)
        cr.line_to(0.5 - 0.15 * s, 0.65)
        cr.line_to(0.5 + 0.15 * s, 0.65)
        cr.close_path()
        cr.stroke()
        
    @staticmethod
    def draw_SQ(cr):
        cr.rectangle(0.25, 0.25, 0.5, 0.5)
        cr.stroke()
    
    @classmethod
    def draw_SL(cls, cr):
        cr.set_source_rgb(*cls.SL_color)
        cls.draw_MA(cr)
        
    @classmethod
    def draw_TB(cls, cr):
        cls.draw_Tx(cr, 1)
    
    @classmethod
    def draw_TW(cls, cr):
        cls.draw_Tx(cr, -1)
        
    @classmethod
    def draw_Tx(cls, cr, col):
        svg = cls.stone_svgs[col]
        s = 0.5 / svg.props.width
        cr.save()
        cr.translate(0.25, 0.25)
        cr.scale(s, s)
        svg.render_cairo(cr)
        cr.restore()
        
    @classmethod
    def draw_DD(cls, cr):
        pass
        
    @staticmethod
    def draw_plus(cr):
        cr.move_to(0.5, 0.25)
        cr.rel_line_to(0, 0.5)
        cr.move_to(0, 0)
        cr.rel_move_to(0.25, 0.5)
        cr.rel_line_to(0.5, 0)
        cr.stroke()
        
    @classmethod
    def draw_hoshi(cls, cr):
        cr.set_source_rgb(*cls.line_color)
        cr.arc(0.5, 0.5, cls.hoshi_radius/cls.line_spacing, 0, 2 * math.pi)
        cr.fill()
    
    @classmethod
    def draw_not_showing(cls, cr):
        cr.set_source_rgba(*(list(cls.bg_color) + [0.8]))
        cr.rectangle(0, 0, 1, 1)
        cr.fill()

    def draw_empty(self, cr):
        cr.save()
        cr.rectangle(0, 0, 1, 1)
        cr.identity_matrix()
        cr.set_source_surface(self.clean_board_surf)
        cr.fill()
        cr.restore()
        return

    def draw_svg(self, cr, svg, alpha):
        self.draw_empty(cr)
        cr.push_group()
        s = 1.0/svg.props.width
        cr.scale(s, s)
        svg.render_cairo(cr)
        cr.pop_group_to_source()
        cr.paint_with_alpha(alpha)
        
    def gen_board(self, bw):
        """Sets self.clean_board_surf, self.board_cr, and self.scale"""
        self.scale = bw / (2.0 * self.board_margin + 
                               (self.board_size - 1.0) * self.line_spacing)
        self.clean_board_surf = cairo.ImageSurface(0, bw, bw)
        cr = cairo.Context(self.clean_board_surf)
        cr.set_source_rgb(*self.board_color)
        cr.rectangle(0, 0, bw, bw)
        cr.fill()
        cr.set_source_rgb(*self.line_color)
        cr.set_line_width(max(1, int(self.heavy_line_width * self.scale)))
        cr.rectangle(*(self.point_map((1, 1)) + [self.real_line_spacing() * 
                       (self.board_size -1)]*2))
        cr.stroke()
        cr.set_line_width(max(1, int(self.line_width * self.scale)))
        for i in (0, 1):
            for j in range(2, self.board_size):
                start = self.point_map((1, j) if i == 0 else (j, 1))
                end = self.point_map((self.board_size, j) if i == 0 else 
                                     (j, self.board_size))
                if self.scale < 1:
                    start = self.sharp_line_endpoint(cr, start)
                    end = self.sharp_line_endpoint(cr, end)
                cr.move_to(*start)
                cr.line_to(*end)
            cr.stroke()
        hoshi_list = self.hoshi_lists.get(self.board_size, ())
        cr.set_source_rgb(*self.line_color)
        for point in hoshi_list:
            self.draw_at_point(cr, self.draw_hoshi, 0, point)
        board_surf = cairo.ImageSurface(0, bw, bw)
        self.board_cr = cairo.Context(board_surf)
        self.board_cr.set_source_surface(self.clean_board_surf)
        self.board_cr.paint()
        self.old_stones = {}

    @staticmethod
    def sharp_line_endpoint(cr, point):
        return cr.device_to_user(*(int(x) + 0.5 for x in 
                                   cr.user_to_device(*point)))
        
    def draw_stones(self):
        alphas = {}
        for prop_id in ("TB", "TW", "DD"):
            for point in self.game_node.markup.get(prop_id, ()):
                alphas[point] = True
        changed_points = []
        for point, color in self.game_node.goban.iteritems():
            if self.old_stones.get(point) is None:
                if not color == 0:
                    changed_points.append(point)
            elif not self.old_stones.get(point) == (color, alphas.get(point, 
                                                                      False)):
                changed_points.append(point)
        for point in changed_points:
            color = self.game_node.goban[point]
            alpha = alphas.get(point, False)
            if color == 0:
                del self.old_stones[point]
                self.draw_at_point(self.board_cr, self.draw_empty, 0, point)
            else:
                self.old_stones[point] = (color, alpha)
                self.draw_at_point(self.board_cr, self.draw_svg, 0, point, 
                               (self.stone_svgs[color], 0.5 if alpha else 1.0))

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
                    draw_func = eval("self.draw_%s" % prop_id)
                    self.draw_at_point(cr, draw_func, color, point)
        last_stone = self.game_node.goban.last_stone
        if not last_stone == None:
            stone_color = self.game_node.goban[last_stone]
            self.draw_at_point(cr, self.draw_plus, stone_color, last_stone)
        if not self.game_node.markup.get('VW') == None:
            for point in self.game_node.goban:
                if not point in self.game_node.markup['VW']:
                    self.draw_at_point(cr, self.draw_not_showing, 0, point)
                               
    def draw_at_point(self, cr, draw_func, stone_color, point, args=()):
        cr.save()
        cr.identity_matrix()
        cr.set_source_rgb(*self.markup_colors[stone_color])
        s = self.real_line_spacing()
        cr.translate(*self.point_map(point))
        cr.scale(s, s)
        cr.translate(*cr.device_to_user(*map(int, cr.user_to_device(-0.5, 
                                                                    -0.5))))
        cr.set_line_width(self.markup_line_width/self.real_line_spacing())
        draw_func(cr, *args)
        cr.restore()

    def draw_line(self, cr, (a, b), prop_id):
        col = self.markup_line_cols[prop_id]
        cr.set_line_width(max(1, int(self.markup_line_width * self.scale)))
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
        bw = int(self.scale * (2 * self.board_margin + (self.board_size - 1) * 
                               self.line_spacing))
        l = self.real_line_spacing()
        m = (bw - (self.board_size - 1) * l) / 2
        return [m + l * (x - 1) for x in point]
        
    def real_line_spacing(self):
        if self.scale > 1:
            return 2 * int(round(self.scale * (self.board_size - 1) * \
                   self.line_spacing) / (self.board_size - 1) / 2)
        else:
            return self.scale * self.line_spacing

