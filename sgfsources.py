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
#   improve kgs and eidogo game_uri acquisition
#   timeout on failed reads
#   handle gameid acquisition failure

import gio
import gobject
import itertools
import os
import pickle
import random
import re
import string
import sys

import gogame

from os_wrapper import data_folder
save_bad_sgf_data = True
gameid_cache_file = "gameid_cache"
try:
    with open(os.path.join(data_folder, gameid_cache_file)) as f:
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
        uri = random.choice(self.game_uris)
        gfile = gio.File(uri)
        try:
            data = gfile.read().read()
        except glib.GError:
            data = None
        return data

    def preload_random_game(self):
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
                print "Error reading file, trying again"
                if save_bad_sgf_data:
                    self.save_sgf(e.data)
        return game_node

    @staticmethod
    def save_sgf(data):
        num = ([0] + sorted(int(a) for a, b in map(os.path.splitext, 
               os.listdir('.')) if b == '.sgf'))[-1] + 1
        filename = os.path.join(data_folder, "sgf_fail", "%s.sgf" % num)
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
                self.game_uris = filter(lambda x: os.path.splitext(x)[-1] == 
                                        ".sgf", os.listdir(self.sgf_folder))
        if self.game_uris == []:
            self.sgf_folder = self.default_sgf_folder
            filenames = filter(lambda x: os.path.splitext(x)[-1] == ".sgf", 
                               os.listdir(self.sgf_folder))
            self.game_uris = [os.path.join(self.sgf_folder, x) for x in filenames]

FileSource.backup_source = FileSource()

class WebSGFSource(SGFSource):
    backup_source = FileSource()
    
    def __init__(self):
        self.source_id = [k for k, v in source_id_map.iteritems() if 
                                                            v == type(self)][0]
        super(WebSGFSource, self).__init__()

    def get_game_uris(self):
        if gameid_cache.get(self.source_id) in ([], None):
            self.get_gameids()
        gameids = gameid_cache[self.source_id]
        self.game_uris = [self.game_url_str % x for x in gameids]
        self.load_gameids()
        
    def save_gameid_cache(self):
        with open(os.path.join(data_folder, gameid_cache_file), 'w') as f:
            pickle.dump(gameid_cache, f)
        
class KGSSource(WebSGFSource):

    game_list_url = "http://kgs.fuseki.info/games_list.php?sb=full&bs=wr"
    game_url_str = "http://kgs.fuseki.info/save_game.php?id=%s"
    min_gameid_count = 1000
        
    def get_gameids(self):
        gfile = gio.File(self.game_list_url)
        data = gfile.read().read()
        gameid_cache[self.source_id] = re.findall(
                                           "OpenGame\\(\\'(\\w*?)\\'\\)", data)

    def load_gameids(self):
        gameid_cache[self.source_id] = []
        gfile = gio.File(self.game_list_url)
        gfile.load_contents_async(self._load_gameid_cb)

    def _load_gameid_cb(self, gfile, result):
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
            print 'error'

class GoKifuSource(WebSGFSource):

    game_list_url = "http://gokifu.com/index.php"
    game_url_str = "http://gokifu.com/f/%s.sgf"

    def get_gameids(self):
        gfile = gio.File(self.game_list_url)
        data = gfile.read().read()
        self.gameids_from_data(data)
        
    def gameids_from_data(self, data):
        last_game_id = re.findall("/f/(\\w*?)\\.sgf", data)[0]
        gameids = list(itertools.imap(lambda x: x.lstrip('0'), 
                       itertools.takewhile(lambda x: not x == last_game_id, 
                       ("%s%s%s" % (a, b, c) for a in string.digits for b in 
                       string.ascii_lowercase for c in string.ascii_lowercase
                       )))) + [last_game_id]
        gameid_cache[self.source_id] = gameids

    def load_gameids(self):
        gfile = gio.File(self.game_list_url)
        gfile.load_contents_async(self._load_gameid_cb)
        
    def _load_gameid_cb(self, gfile, result):
        data = gfile.load_contents_finish(result)[0]
        self.gameids_from_data(data)
        
class EidoGoSource(WebSGFSource):

    game_list_url = "http://eidogo.com/games?q=+"
    game_url_str = "http://eidogo.com/backend/download.php?id=%s"
    
    def get_gameids(self):
        gfile = gio.File(self.game_list_url)
        data = gfile.read().read()
        self.gameids_from_data(data)

    def gameids_from_data(self, data):
        gameids = re.findall("<td><a href=\"\\./#(.*?)\">", data)
        gameid_cache[self.source_id] = gameids
        
    def load_gameids(self):
        gfile = gio.File(self.game_list_url)
        gfile.load_contents_async(self._load_gameid_cb)
        
    def _load_gameid_cb(self, gfile, result):
        data = gfile.load_contents_finish(result)[0]
        self.gameids_from_data(data)
        
class MultiSource(SGFSource):
    
    def __init__(self, source_ids):
        self.sources = tuple(source_id_map[sid]() for sid in source_ids)
        if self.sources == ():
            self.sources = (FileSource(), )
    
    def get_random_game(self):
        return random.choice(self.sources).get_random_game()

source_id_map = {"file": FileSource,
                 "kgs": KGSSource,
                 "gokifu": GoKifuSource,
                 "eidogo": EidoGoSource}
