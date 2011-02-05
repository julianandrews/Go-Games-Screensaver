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
#   Support alternative board sizes

import sys

import sgfparse
import sgfverify

color_mapping = {'B':1, 'W':-1, 'E':0}

class GogameError(Exception):
    def __init__(self, value, data):
        self.value = value
        self.data = data
        
    def __str__(self):
        return "Error Generating Gogame - %s" % value

class Goban(dict):

    _char_map = {None: ' ', 1: 'B', -1: 'W', 0: '.'}

    def __init__(self, goban = None, size = 19):
        if not goban is None:
            self.size = goban.size
            self.prisoners = dict(goban.prisoners)
            self.move_number = goban.move_number
        else:
            self.size = size
            self.move_number = 0
            self.prisoners = {1:0, -1:0}
        dict.__init__(self, goban or self._default_goban(size))
        self.last_stone = None
                        
    def __str__(self):
        x_range = (min(x[0] for x in self.keys()), 
                   max(x[0] for x in self.keys()))
        y_range = (min(x[1] for x in self.keys()), 
                   max(x[1] for x in self.keys()))
        legend = "    " + ' '.join(chr(x) for x in range(x_range[0] + 
                            ord('A') - 1, x_range[1] + ord('A'))) + '\n'
        s = '\n' + legend
        for i in range(y_range[1], y_range[0] - 1, -1):
            s += self._row_str(i, x_range)
        s += legend
        return s
            
    def _row_str(self, i, x_range):
        s = " %2d " % i
        for j in range(x_range[0], x_range[1] + 1):
            s += self._char_map[self.get((i, j))] + ' '
        s += "%2d\n" %i
        return s

    def add_stone(self, color, point):
        self[point] = color
        
    def play_move(self, color, point):
        self.add_stone(color, point)
        for n in self.neighbors(point):
            if self[n] == -color:
                g = Group(n, self)
                if len(g.liberties) == 0:
                    self.kill_group(g)
        g = Group(point, self)
        if len(g.liberties) == 0:
            self.kill_group(g)
        self.move_number += 1
        self.last_stone = point
        
    def kill_group(self, g):
        self.prisoners[g.color] += len(g)
        for point in g.keys():
            self.add_stone(0, point)

    def neighbors(self, point):
        points = ((point[0]-1, point[1]), (point[0]+1, point[1]),
                  (point[0], point[1]-1), (point[0], point[1]+1))
        return tuple(p for p in points if not self.get(p) == None)
    
    @staticmethod
    def _default_goban(size):
        goban = {}
        for i in range(1, size + 1):
            for j in range(1, size + 1):
                goban[(i, j)] = 0
        return goban
    
class Group(dict):
    def __init__(self, start_point, goban):
        self.goban = goban
        self.color = goban[start_point]
        self.liberties = {}
        if self.color == 0:
            return
        else:
            self._expand(start_point)
            
    def _expand(self, p):
        self[p] = True
        for n in self.goban.neighbors(p):
            if self.get(n) == None:
                if self.goban[n] == self.color:
                    self._expand(n)
                elif self.goban[n] == 0:
                    self.liberties[n] = True
    
class GameNode(object):
    def __init__(self, node, goban = None, parent = None):
        self.child_nodes = []
        self.goban = goban or Goban(size=int(node.get("SZ", [19])[0]))
        self.game_info = parent.game_info if not parent == None else {}
        self.annotations = {}
        self.markup = {}
        for prop_id in ('B', 'W'):
            if not node.get(prop_id) == None:
                if not node[prop_id][0] == '':
                    point = _point_from_string(node[prop_id][0])
                    self.goban.play_move(color_mapping[prop_id], point)
        if not node.get('MN') == None:
            self.goban.move_number = int(node['MN'][0])
        for prop_id in ('AB', 'AW', 'AE'):
            if not node.get(prop_id) == None:
                for point in _points_from_pointlist(node[prop_id]):
                    self.goban.add_stone(color_mapping[prop_id[1]], point)
        if not parent == None:
            for prop_id, prop_vals in parent.markup.iteritems():
                if sgfverify.property_info[prop_id][3] == 'inherit':
                    self.markup[prop_id] = prop_vals
        for prop_id, prop_vals in node.iteritems():
            if sgfverify.property_info.get(prop_id) == None:
                continue
            name, p_type, value, attr, game = sgfverify.property_info[prop_id]
            if p_type == 'game-info':
                self.game_info[prop_id] = prop_vals[0]
            elif p_type in ('annotation', 'move-annotation'):
                val = prop_vals[0]
                if value == "double":
                    val = int(val)
                elif value == "real":
                    val = float(val)
                self.annotations[prop_id] = val
            elif p_type == 'markup':
                if attr == 'inherit' and prop_vals == ['']:
                    if not self.markup.get(prop_id) == None:
                        del self.markup[prop_id]
                elif value in ('l-point', 'el-point'):
                    self.markup[prop_id] = _points_from_pointlist(prop_vals)
                elif value in 'l-point:point':
                    self.markup[prop_id] = [tuple(map(_point_from_string, 
                                            s.split(':'))) for s in prop_vals]

        for child in node.child_nodes:
            self.child_nodes.append(GameNode(child, Goban(self.goban), self))
        
    def __getitem__(self, key):
        return self.child_nodes[key]

def _points_from_pointlist(l):
    points = []
    for s in l:
        if ':' in s:
            points += _points_from_compose(s)
        else:
            points.append(_point_from_string(s))
    return points

def _points_from_compose(s):
    start, end = map(_point_from_string, s.split(':'))
    points = []
    for x in range(start[0], end[0]+1):
        for y in range(start[1], end[1]+1):
            points.append((x, y))
    return points

def _point_from_string(s):
    return tuple(map(_char_to_int_coord, s))
    
def _char_to_int_coord(c):
    val = ord(c) + 1
    if val > ord('a'):
        return val - ord('a')
    else:
        return val - ord('A')

def game_nodes_from_file(filename):
    with open(filename) as f:
        data = f.read()
    return game_nodes_from_data(data)

def game_nodes_from_data(data):
    sys.setrecursionlimit(5000)
    try:
        c = sgfparse.parse(data)
    except sgfparse.SGFParseError, e:
        raise GogameError("SGF parse failed: %s" % e.value, data)
    for node in c:
        try:
            sgfverify.verify_node(node)
        except sgfverify.SGFVerifyError, e:
            raise GogameError("SGF verification failed: %s" % e.value, data)
        if not node.get("FF") == ['4']:
            sgfverify.convert_node(node)
        if not node.get("GM", ['1']) == ['1']:
            raise GogameError("SGF is not a Go Game!", data)
        if not node.get("SZ") in (['19'], ['13'], ['9'], None):
            raise GogameError("Unsupported board size property: %s" % node["SZ"], data)
    return map(GameNode, c)

