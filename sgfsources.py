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

import time #testing!

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

import gogame

from os_wrapper import data_folder, config_folder
save_bad_sgf_data = False
gameid_cache_file = "gameid_cache"
try:
    with open(os.path.join(config_folder, gameid_cache_file)) as f:
        gameid_cache = pickle.load(f)
except IOError:
    gameid_cache = {}

class SGFSource(object):
    preload_count = 5

    def __init__(self):
        self.preloaded_data = []
        self.get_game_uris()

    def get_random_game(self):
        if self.preloaded_data == []:
            data = self.load_random_game()
        else:
            data = self.preloaded_data.pop(0)
        if data is None:
            return self.backup_source.get_random_game()
        game_node = self.game_node_from_data(data)
        if game_node is None:
            return self.get_random_game()
        else:
            for i in range(self.preload_count - len(self.preloaded_data)):
                self.preload_random_game()
            return game_node
            
    def load_random_game(self):
        if self.game_uris == []:
            return None
        uri = random.choice(self.game_uris)
        gfile = gio.File(uri)
        try:
            data = gfile.load_contents()[0]
        except glib.GError:
            data = None
        return data

    def preload_random_game(self):
        if not self.game_uris == []:
            uri = random.choice(self.game_uris)
            gfile = gio.File(uri)
            gfile.load_contents_async(self._file_load_cb)

    def _file_load_cb(self, gfile, result):
        try:
            data = gfile.load_contents_finish(result)[0]
            self.preloaded_data.append(data)
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
        folder = os.path.join(config_folder, "sgf_fail")
        if not os.path.isdir(folder):
            if not os.path.isdir(config_folder):
                os.mkdir(config_folder)
            os.mkdir(folder)
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

    def get_game_uris(self):
        self.game_uris = []
        if not self.sgf_folder is None:
            if os.path.isdir(self.sgf_folder):
                filenames = filter(lambda x: os.path.splitext(x)[-1] == 
                                        ".sgf", os.listdir(self.sgf_folder))
                self.game_uris = [os.path.join(self.sgf_folder, f) for f in 
                                  filenames]
        if self.game_uris == []:
            self.sgf_folder = self.default_sgf_folder
            filenames = filter(lambda x: os.path.splitext(x)[-1] == ".sgf", 
                               os.listdir(self.sgf_folder))
            self.game_uris = [os.path.join(self.sgf_folder, x) for x in filenames]

FileSource.backup_source = FileSource()

class WebSGFSource(SGFSource):
    backup_source = FileSource()
    startup_delay = 3000
    
    def __init__(self):
        self.source_id = [k for k, v in source_id_map.iteritems() if 
                                                            v == type(self)][0]
        super(WebSGFSource, self).__init__()

    def get_game_uris(self):
        if gameid_cache.get(self.source_id) in ([], None):
            self.get_gameids()
        gameids = gameid_cache.get(self.source_id, [])
        self.game_uris = [self.game_url_str % x for x in gameids]
        glib.timeout_add(self.startup_delay, self.preload_gameids)
        
    def preload_gameids(self):
        gameid_cache[self.source_id] = []
        gfile = gio.File(self.game_list_url)
        gfile.load_contents_async(self._preload_gameid_cb)
        
    def _preload_gameid_cb(self, gfile, result):
        try:
            data = gfile.load_contents_finish(result)[0]
            self.gameids_from_data(data)
            self.save_gameid_cache()
        except glib.GError, e:
            warnings.warn("Error in gameid callback for %s:\n%s" % 
                          (self.source_id, e.message))
        
    def save_gameid_cache(self):
        with open(os.path.join(config_folder, gameid_cache_file), 'w') as f:
            pickle.dump(gameid_cache, f)
        
class KGSSource(WebSGFSource):

    game_list_url = "http://kgs.fuseki.info/games_list.php?bs=wr"
    game_url_str = "http://kgs.fuseki.info/save_game.php?id=%s"
    min_gameid_count = 1000
        
    def get_gameids(self):
        gfile = gio.File(self.game_list_url)
        try:
            data = gfile.load_contents()[0]
            gameid_cache[self.source_id] = re.findall(
                                           "OpenGame\\(\\'(\\w*?)\\'\\)", data)
        except glib.GError:
            warnings.warn("Error getting KGS gameids.")

    def _preload_gameid_cb(self, gfile, result):
        try:
            data = gfile.load_contents_finish(result)[0]
            gameid_cache[self.source_id] += \
                                re.findall("OpenGame\\(\\'(\\w*?)\\'\\)", data)
            self.game_uris = [self.game_url_str % x for x in 
                                                 gameid_cache[self.source_id]]
            if len(gameid_cache[self.source_id]) < self.min_gameid_count:
                start_str = "&id=%s" % gameid_cache[self.source_id][-1]
                new_gfile =gio.File(self.game_list_url + start_str)
                new_gfile.load_contents_async(self._load_gameid_cb)
            else:
                self.save_gameid_cache()
        except glib.GError:
            warnings.warn("Error in callback getting KGS gameids.")

class GoKifuSource(WebSGFSource):

    game_list_url = "http://gokifu.com/index.php"
    game_url_str = "http://gokifu.com/f/%s.sgf"

    def get_gameids(self):
        gfile = gio.File(self.game_list_url)
        try:
            data = gfile.load_contents()[0]
            self.gameids_from_data(data)
        except glib.GError:
            warnings.warn("Error getting GoKifu gameids: %e", e)

    def gameids_from_data(self, data):
        last_game_id = re.findall("/f/(\\w*?)\\.sgf", data)[0]
        gameids = list(itertools.imap(lambda x: x.lstrip('0'), 
                       itertools.takewhile(lambda x: not x == last_game_id, 
                       ("%s%s%s" % (a, b, c) for a in string.digits for b in 
                       string.ascii_lowercase for c in string.ascii_lowercase
                       )))) + [last_game_id]
        gameid_cache[self.source_id] = gameids
        
class EidoGoSource(WebSGFSource):

    game_list_url = "http://eidogo.com/games?q=+"
    game_url_str = "http://eidogo.com/backend/download.php?id=%s"
    
    def get_gameids(self):
        gfile = gio.File(self.game_list_url)
        try:
            data = gfile.load_contents()[0]
            self.gameids_from_data(data)
        except glib.GError:
            warnings.warn("Error getting Eidogo gameids.")

    def gameids_from_data(self, data):
        gameids = re.findall("<td><a href=\"\\./#(.*?)\">", data)
        gameid_cache[self.source_id] = gameids

        
class MultiSource(SGFSource):
    
    def __init__(self, source_ids, sgf_folder=None):
        self.sources = []
        for sid in source_ids:
            if sid == 'file':
                source = source_id_map[sid](sgf_folder)
            else:
                source = source_id_map[sid]()
            self.sources.append(source)
        if self.sources == ():
            self.sources = (FileSource(sgf_folder), )
    
    def get_random_game(self):
        return random.choice(self.sources).get_random_game()

source_id_map = {"file": FileSource,
                 "kgs": KGSSource,
                 "gokifu": GoKifuSource,
                 "eidogo": EidoGoSource}
