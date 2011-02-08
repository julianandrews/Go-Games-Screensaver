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
#    Handle error correction

import collections
import simpleparse.parser
import simpleparse.dispatchprocessor
import warnings

_base_EBNFDeclaration = r"""
    Collection := WhiteSpace*, GameTree, (WhiteSpace*, GameTree)*
    GameTree := '(', WhiteSpace*, Sequence, 
                (WhiteSpace*, GameTree)*, WhiteSpace*, ')'
    Sequence := Node, (WhiteSpace*, Node)*
    Node := ";", (WhiteSpace*, Property)*
    Property := PropIdent, (WhiteSpace*, PropValue)+
    PropIdent := [A-Za-z]+
    >PropValue< := '[', ValueType, ']'

    <WhiteSpace> := [ \t\r\n\v]
"""

_EBNFDeclaration = _base_EBNFDeclaration + \
                                     r"ValueType := (('\\', []\])/-']')*, ?']'"

_forgiving_EBNFDeclaration = _base_EBNFDeclaration + r"""
    ValueType := (Parenth / ('\\', []\]) / -[][])*, ?']'
    >Parenth< := '[', -']'*, ']'"""

class SGFParseError(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return "Error Parsing SGF - %s" % value

class Node(collections.defaultdict):
    def __init__(self):
        self.default_factory = list
        self.child_nodes = []
        self.parent_node = None
        self.text = ''
        
    def __str__(self):
        return dict.__str__(self)
    
    def __repr__(self):
        return "Node(" + dict.__repr__(self) + ")"
    
    def __str__(self):
        return self.text

class _SGFProcessor(simpleparse.dispatchprocessor.DispatchProcessor):
    def GameTree(self, (tag, start, stop, subtags), buff):
        seqs = simpleparse.dispatchprocessor.dispatchList(self, subtags, buff)
        tail_node = seqs[0]
        while len(tail_node.child_nodes) > 0:
            tail_node = tail_node.child_nodes[0]
        for tree in seqs[1:]:
            tail_node.child_nodes.append(tree)
        return seqs[0]
        
    def Sequence(self, (tag, start, stop, subtags), buff):
        nodes = simpleparse.dispatchprocessor.dispatchList(self, subtags, buff)
        for nodeA, nodeB in zip(nodes, nodes[1:]):
            nodeA.child_nodes.append(nodeB)
            nodeB.parentNode = nodeA
        return nodes[0]
    
    def Node(self, (tag, start, stop, subtags), buff):
        props = simpleparse.dispatchprocessor.dispatchList(self, subtags, buff)
        n = Node()
        text = simpleparse.dispatchprocessor.getString((tag, start, stop, 
                                                               subtags), buff)
        n.text = text
        for prop in props:
            if not n.get(prop[0]) is None:
                # Erase duplicate properties and issue a warning!
                warnings.warn("Duplicate '%s' property in node '%s'" % 
                              (prop[0], text))
                continue
            n[prop[0]] += prop[1:]
        return n

    def Property(self, (tag, start, stop, subtags), buff):
        return simpleparse.dispatchprocessor.dispatchList(self, subtags, buff)

    def PropIdent(self, (tag, start, stop, subtags), buff):
        return simpleparse.dispatchprocessor.getString((tag, start, stop, 
                                                        subtags), buff)

    def ValueType(self, (tag, start, stop, subtags), buff):
        return simpleparse.dispatchprocessor.getString((tag, start, stop, subtags), buff)

def parse(data, forgiving_mode=False):
    decl = _forgiving_EBNFDeclaration if forgiving_mode else _EBNFDeclaration
    parser = simpleparse.parser.Parser(decl, "Collection")
    processor = _SGFProcessor()
    success, collection, next_char = parser.parse(data, processor=processor)
    if not success:
        if forgiving_mode:
            raise SGFParseError("Parse Failed!")
        else:
            warnings.warn("Parse failed, attempting parse in forgiving mode")
            return parse(data, forgiving_mode=True)
    else:
        return collection

def parse_file(filename):
    with open(filename) as f:
        data = f.read()
    return parse(data)

