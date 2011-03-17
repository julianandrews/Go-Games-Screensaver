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
#   improve kgs and eidogo game_uri acquisition
#   timeout on failed reads

import gio
import glib
import itertools
import os
import pickle
import random
import re
import string
import sys
import warnings
import xml.dom.minidom

import gogame

from config import sources
from constants import data_folder, cache_folder, save_bad_sgf_data
gameid_cache_file = "gameid_cache"

try:
    with open(os.path.join(cache_folder, gameid_cache_file)) as f:
        gameid_cache = pickle.load(f)
except IOError:
    gameid_cache = {}

class SGFSource(object):
    preload_count = 5

    def __init__(self):
        self.preloaded_data = []
        self.preload_game_uris()

    def get_random_game(self):
        if self.preloaded_data == []:
            return None
        else:
            data, uri = self.preloaded_data.pop(0)
        game_node = self.game_node_from_data(data)
        if game_node is None:
            self.game_uris.remove(uri)
            return self.get_random_game()
        else:
            for i in range(self.preload_count - len(self.preloaded_data)):
                self.preload_game()
            return game_node

    def preload_game(self):
        if not self.game_uris == []:
            uri = random.choice(self.game_uris)
            gfile = gio.File(uri)
            gfile.load_contents_async(self._file_preload_cb, user_data=uri)

    def _file_preload_cb(self, gfile, result, uri):
        try:
            data = gfile.load_contents_finish(result)[0]
            self.preloaded_data.append((data, uri))
        except glib.GError:
            pass

    def game_node_from_data(self, data):
        game_node = None
        try:
            collection = gogame.game_nodes_from_data(data)
            game_node = collection[0]
        except gogame.GogameError, e:
            if not e.data == "":
                if save_bad_sgf_data:
                    self.save_sgf(e.data)
        return game_node

    @staticmethod
    def save_sgf(data):
        folder = os.path.join(cache_folder, "sgf_fail")
        if not os.path.isdir(folder):
            os.makedirs(folder, 0700)
        num = ([0] + sorted(int(a) for a, b in map(os.path.splitext, 
               os.listdir(folder)) if b == '.sgf'))[-1] + 1
        filename = os.path.join(folder, "%s.sgf" % num)
        warnings.warn("Error reading file, saving to '%s'" % filename)
        with open(filename, 'w') as f:
            f.write(data)

class FileSource(SGFSource):
    default_sgf_folder = os.path.join(data_folder, "sgf")
    
    def __init__(self, sgf_folder=None):
        self.sgf_folder = sgf_folder
        SGFSource.__init__(self)

    def preload_game_uris(self):
        self.game_uris = []
        if not self.sgf_folder is None:
            if os.path.isdir(self.sgf_folder):
                filenames = filter(lambda x: os.path.splitext(x)[-1] == 
                                        ".sgf", os.listdir(self.sgf_folder))
                self.game_uris = [os.path.join(self.sgf_folder, f) for f in 
                                  filenames]
        if self.game_uris == []:
            warnings.warn("No sgf files found in folder - using default folder")
            self.sgf_folder = self.default_sgf_folder
            filenames = filter(lambda x: os.path.splitext(x)[-1] == ".sgf", 
                               os.listdir(self.sgf_folder))
            self.game_uris = [os.path.join(self.sgf_folder, x) for x in filenames]
        self.preload_game()

    def preload_game(self):
        if not self.game_uris == []:
            uri = random.choice(self.game_uris)
            gfile = gio.File(uri)
            data = gfile.load_contents()[0]
            self.preloaded_data.append((data, uri))

class WebSource(SGFSource):
    def __init__(self, sid):
        self.sid = sid
        ix = [x[0] for x in sources].index(sid)
        sid, self.uri_str, self.regex, self.help_str, self.pages = sources[ix]
        super(WebSource, self).__init__()
                
    def preload_game_uris(self):
        self.game_uris = []
        gameids = gameid_cache.get(self.sid, [])
        self.game_uris += [self.uri_str % x for x in gameids]
        if len(self.game_uris) > 0:
            self.preload_game()
        self.preload_gameids()

    def preload_gameids(self):
        self.game_uris = []
        gameid_cache[self.sid] = []
        for base_url in self.pages:
            gfile = gio.File(base_url)
            gfile.load_contents_async(self._preload_gameid_cb)
        
    def _preload_gameid_cb(self, gfile, result):
        try:
            data = gfile.load_contents_finish(result)[0]
        except glib.GError:
            warnings.warn("Error loading '%s'" % self.sid)
            return
        ids = list(set(re.findall(self.regex, data)))
        gameid_cache[self.sid] += ids
        self.save_gameid_cache()
        uri_list = [self.uri_str % i for i in ids]
        self.game_uris += uri_list
        if len(self.preloaded_data) == 0 and len(self.game_uris) > 0:
            self.preload_game()
        
    def save_gameid_cache(self):
        if not os.path.isdir(cache_folder):
            os.makedirs(cache_folder, 0700)
        with open(os.path.join(cache_folder, gameid_cache_file), 'w') as f:
            pickle.dump(gameid_cache, f)
        
class MultiSource(SGFSource):
    
    def __init__(self, sids, sgf_folder=None):
        self.sources = []
        for sid in sids:
            if sid == 'file':
                self.sources.append(FileSource(sgf_folder))
            else:
                self.sources.append(WebSource(sid))
        if self.sources == ():
            self.sources.append(FileSource(sgf_folder))
    
    def get_random_game(self):
        return random.choice(self.sources).get_random_game()

