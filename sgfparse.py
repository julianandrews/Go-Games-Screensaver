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
# Todo:
#    Handle error correction

import collections
import simpleparse.parser
import simpleparse.dispatchprocessor
import warnings

_EBNFDeclaration = r"""
    Collection := WhiteSpace*, GameTree, (WhiteSpace*, GameTree)*
    GameTree := '(', WhiteSpace*, Sequence, 
                (WhiteSpace*, GameTree)*, WhiteSpace*, ')'
    Sequence := Node, (WhiteSpace*, Node)*
    Node := ";", (WhiteSpace*, Property)*
    Property := PropIdent, (WhiteSpace*, PropValue)+
    PropIdent := [A-Za-z]+
    >PropValue< := '[', ValueType, ']'
    ValueType := (('\\', []\])/-']')*, ?']'

    <WhiteSpace> := [ \t\r\n\v]
"""

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

def parse(data):
    parser = simpleparse.parser.Parser(_EBNFDeclaration, "Collection")
    processor = _SGFProcessor()
    success, collection, next_char = parser.parse(data, processor=processor)
    if not success:
        raise SGFParseError("Parse Failed!")
    else:
        return collection

def parse_file(filename):
    with open(filename) as f:
        data = f.read()
    return parse(data)

