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
#   properties must have values of the appropriate type
#   point lists must be unique for 
#       ('CR', 'MA', 'SL', 'SQ', 'TR')
#       ('AB', 'AE', 'AW')
#       each point list type individually
#   points must lie within the actual board dimensions
#   DT, RE, KM, HA, and TM have mandatory formatting requirements
#   Convert TE then BM, or BM then TE correctly
#   Deal with L ordering correctly in conversion
#   Support error correction

import string

import sgfparse

property_info = {
    'FF': ('Fileformat', 'root', 'number', '', ''),
    'GM': ('Game', 'root', 'number', '', ''), 
    'SZ': ('Size', 'root', '(number|number:number)', '', ''),
    'CA': ('Charset', 'root', 'simpletext', '', ''),   
    'ST': ('Style', 'root', 'number (range: 0-3)', '', ''),
    'AP': ('Application', 'root', 'simpletext:simpletext', '', ''),

    'PB': ('Player Black', 'game-info', 'simpletext', '', ''), 
    'PW': ('Player White', 'game-info', 'simpletext', '', ''), 
    'HA': ('Handicap', 'game-info', 'number', '', 'Go'),
    'KM': ('Komi', 'game-info', 'real', '', 'Go'), 
    'TM': ('Timelimit', 'game-info', 'real', '', ''), 
    'BR': ('Black rank', 'game-info', 'simpletext', '', ''), 
    'WR': ('White rank', 'game-info', 'simpletext', '', ''),
    'RE': ('Result', 'game-info', 'simpletext', '', ''),   
    'BT': ('Black team', 'game-info', 'simpletext', '', ''), 
    'WT': ('White team', 'game-info', 'simpletext', '', ''), 
    'PC': ('Place', 'game-info', 'simpletext', '', ''),
    'DT': ('Date', 'game-info', 'simpletext', '', ''), 
    'RU': ('Rules', 'game-info', 'simpletext', '', ''), 
    'EV': ('Event', 'game-info', 'simpletext', '', ''), 
    'RO': ('Round', 'game-info', 'simpletext', '', ''),
    'US': ('User', 'game-info', 'simpletext', '', ''),  
    'AN': ('Annotation', 'game-info', 'simpletext', '', ''),
    'GC': ('Game comment', 'game-info', 'text', '', ''), 
    'GN': ('Game name', 'game-info', 'simpletext', '', ''), 
    'OT': ('Overtime', 'game-info', 'simpletext', '', ''), 
    'ON': ('Opening', 'game-info', 'simpletext', '', ''), 
    'SO': ('Source', 'game-info', 'simpletext', '', ''),
    'CP': ('Copyright', 'game-info', 'simpletext', '', ''), 
    
    'AE': ('Add Empty', 'setup', 'l-point', '', ''), 
    'AB': ('Add Black', 'setup', 'l-stone', '', ''), 
    'AW': ('Add White', 'setup', 'l-stone', '', ''), 
    'PL': ('Player to play', 'setup', 'color', '', ''), 

    'W': ('White', 'move', 'move', '', ''), 
    'B': ('Black', 'move', 'move', '', ''), 
    'MN': ('set move number', 'move', 'number', '', ''),

    'WL': ('White time left', 'move-timing', 'real', '', ''), 
    'BL': ('Black time left', 'move-timing', 'real', '', ''),
    'OB': ('OtStones Black', 'move-timing', 'number', '', ''), 
    'OW': ('OtStones White', 'move-timing', 'number', '', ''), 
    
    'TE': ('Tesuji', 'move-annotation', 'double', '', ''), 
    'KO': ('Ko', 'move-annotation', 'none', '', 'Go'), 
    'DO': ('Doubtful', 'move-annotation', 'none', '', ''), 
    'BM': ('Bad move', 'move-annotation', 'double', '', ''), 
    'IT': ('Interesting', 'move-annotation', 'none', '', ''), 
    'N': ('Nodename', 'annotation', 'simpletext', '', ''), 
    'C': ('Comment', 'annotation', 'text', '', ''), 
    'DM': ('Even position', 'annotation', 'double', '', ''), 
    'GB': ('Good for Black', 'annotation', 'double', '', ''), 
    'GW': ('Good for White', 'annotation', 'double', '', ''), 
    'UC': ('Unclear pos', 'annotation', 'double', '', ''), 
    'HO': ('Hotspot', 'annotation', 'double', '', ''), 
    'V': ('Value', 'annotation', 'real', '', ''), 
    
    'TB': ('Territory Black', 'markup', 'el-point', '', 'Go'), 
    'TW': ('Territory White', 'markup', 'el-point', '', 'Go'), 
    'DD': ('Dim points', 'markup', 'el-point', 'inherit', ''), 
    'LB': ('Label', 'markup', 'l-point:simpletext', '', ''), 
    'LN': ('Line', 'markup', 'l-point:point', '', ''), 
    'TR': ('Triangle', 'markup', 'l-point', '', ''),
    'AR': ('Arrow', 'markup', 'l-point:point', '', ''), 
    'CR': ('Circle', 'markup', 'l-point', '', ''), 
    'MA': ('Mark', 'markup', 'l-point', '', ''), 
    'SQ': ('Square', 'markup', 'l-point', '', ''), 
    'SL': ('Selected', 'markup', 'l-point', '', ''), 
    'VW': ('View', 'markup', 'el-point', 'inherit', ''),
     
    'FG': ('Figure', 'print', 'none|number:simpletext', '', ''),
    'PM': ('Print move mode', 'print', 'number', 'inherit', '')}

_property_conflicts = (('B', 'W'), ('DM', 'UC', 'GB', 'GW'), 
                       ('BM', 'TE', 'DO', 'IT'))

class SGFVerifyError(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return self.value

def verify_file(filename):
    collection = sgfparse.parse_file(data)
    _verify_collection(collection)

def verify(data):
    collection = sgfparse.parse(data)
    _verify_collection(collection)

def _verify_collection(collection):
    for node in collection:
        verify_node(node)

def verify_node(node, ff=1):
    if node.parent_node == None:
        for prop_id in node.keys():
            if filter(lambda x: x.isupper(), prop_id) == 'FF':
                ff = node[prop_id]
    if ff == 4:
        for prop_id in node.keys():
            if not prop_id.isupper():
                raise SGFVerifyError("Invalid prop id in a FF[4] file: %s" % 
                                     node)
    all_prop_types = _get_all_prop_types(node)
    if all_prop_types.get('root') and not node.parent_node == None:
        raise SGFVerifyError("Invalid 'root' property: %s" % node)
    elif all_prop_types.get('game-info'):
        working_node = node
        while not working_node.parent_node == None:
            working_node = working_node.parent_node
            if _has_game_info_props(working_node):
                raise SGFVerifyError("Invalid 'game-info' property: %s" % node)
    elif all_prop_types.get('setup') and all_prop_types.get('move') and ff==4:
         raise SGFVerifyError("Invalid mix of 'root' and 'setup' properties: "
                              "%s" % node)
    elif (all_prop_types.get('move-annotation') or 
          all_prop_types.get('move-timing')) and not \
         (node.get('B') or node.get('W')) and ff == 4:
         raise SGFVerifyError("Move annotation or timing in non-move mode: %s" 
                              % node)
    for conflict_list in _property_conflicts:
        if len(tuple(prop_id for prop_id in conflict_list if 
               not node.get(prop_id) == None)) > 1:
            raise SGFVerifyError("Property conflict in set %s: %s" % 
                                 (conflict_list, node))

    for child in node.child_nodes:
        verify_node(child, ff)

def convert_node(node, ff):
    """Convert a node and its children from FF[1]-[3] to FF[4]."""
    for prop_id in node.keys():
        value = node[prop_id]
        new_prop_id = filter(lambda x: x.isupper(), prop_id)
        if not new_prop_id == prop_id:
            node[new_prop_id] = value
            del node[prop_id]
        prop_id = new_prop_id
        if prop_id == 'M' and ff in (1, 2):
            node['MA'] = value
            del node['M']
        if prop_id in ('B', 'W') and value == ['tt'] and ff in (1, 2, 3):
            node[prop_id] = ['']
        if prop_id == 'L' and ff in (1, 2):
            node['LB'] += ["%s:%s" % (x, l) for x, l in zip(value, 
                           string.uppercase)]
            del node['L']
        if prop_id == 'VW' and len(value) == 2 and ff in (1, 2, 3):
            node['VW'] = ["%s:%s" % value]
    all_prop_types = _get_all_prop_types(node)
    if all_prop_types.get('setup') and all_prop_types.get('move') and \
                                                               ff in (1, 2, 3):
        new_node = sgfparse.Node()
        new_node.text = node.text
        for prop_id in node.keys():
            prop_type = property_info.get(prop_id)
            if not prop_type == None:
                prop_type = prop_type[1]
            if not prop_id == 'N' or prop_type in ('game-info', 'setup', 'root'):
                new_node[prop_id] = node[prop_id]
                del node[prop_id]
        new_node.child_nodes = node.child_nodes
        node.child_nodes = [new_node]
        new_node.parent = node
    for child in node.child_nodes:
        convert_node(child, ff)

def _get_all_prop_types(node):
    property_details = _get_property_details(node)
    all_prop_types = {}
    for entry in property_details:
        all_prop_types[entry[1]] = True
    return all_prop_types

def _has_game_info_props(node):
    property_details = _get_property_details(node)
    return any(x[1] == 'game-info' for x in property_details)
    
def _get_property_details(node):
    return tuple(property_info.get(prop_id) for prop_id in node.keys() if not \
                                            property_info.get(prop_id) == None)

