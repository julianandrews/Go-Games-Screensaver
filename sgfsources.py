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
#   timeout on game list acquisition failure

import gio
import gobject
import itertools
import os
import pickle
import random
import re
import string
import sys
import time

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
        return gfile.read().read()

    def preload_random_game(self):
        uri = random.choice(self.game_uris)
        gfile = gio.File(uri)
        gfile.load_contents_async(self._file_load_cb)

    def _file_load_cb(self, gfile, result):
        data = gfile.load_contents_finish(result)[0]
        self.preloaded_data.append(data)

    def game_node_from_data(self, data):
        game_node = None
        try:
            collection = gogame.game_nodes_from_data(data)
            game_node = collection[0]
        except gogame.GogameError, e:
            self.game_uris.remove(uri)
            if not e.data == "":
                print "Error reading file, trying again"
                if save_bad_sgf_data:
                    with open(self._save_sgf_filename(), 'w') as f:
                        f.write(e.data)
        return game_node

    @staticmethod
    def _save_sgf_filename():
        num = ([0] + sorted(int(a) for a, b in map(os.path.splitext, 
               os.listdir('.')) if b == '.sgf'))[-1] + 1
        return os.path.join(data_folder, "sgf_fail", "%s.sgf" % num)

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

class WebSGFSource(SGFSource):
    backup_source = FileSource()
    timeout = 3
    
    def __init__(self):
        self.source_id = [k for k, v in source_id_map.iteritems() if 
                                                             v == type(self)][0]
        super(WebSGFSource, self).__init__()

    def get_game_uris(self):
        gameids = gameid_cache.get(self.source_id, [])
        if len(gameids) == 0:
            self.refresh_game_uris()
        else:
            self.game_uris = [self.game_url_str % x for x in gameids]
            gobject.idle_add(self.refresh_game_uris)
            
    def refresh_game_uris(self):
        print "refreshing uris"
        global gameid_cache
        gameids = self.get_gameids()
        self.game_uris = [self.game_url_str % x for x in gameids]
        gameid_cache[self.source_id] = gameids
        with open(gameid_cache_file, 'w') as f:
            pickle.dump(gameid_cache, f)
        
class KGSSource(WebSGFSource):

    game_list_url = "http://kgs.fuseki.info/games_list.php?sb=full&bs=wr"
    game_url_str = "http://kgs.fuseki.info/save_game.php?id=%s"
    game_count = 300
    
    def get_gameids(self):
        gameids = []
        start_str = ""
        while len(gameids) < self.game_count:
            data = ""
            filehandle = urllib2.urlopen(self.game_list_url + start_str)
            data = filehandle.read()
            filehandle.close()
            gameids += re.findall("OpenGame\\(\\'(\\w*?)\\'\\)", data)
            if len(gameids) == 0:
                break
            start_str = "&id=%s" % gameids[-1]
        return gameids

class GoKifuSource(WebSGFSource):

    game_list_url = "http://gokifu.com/index.php"
    game_url_str = "http://gokifu.com/f/%s.sgf"

    def get_gameids(self):
        filehandle = urllib2.urlopen(self.game_list_url)
        data = filehandle.read()
        filehandle.close()
        try:
            last_game_id = re.findall("/f/(\\w*?)\\.sgf", data)[0]
        except IndexError:
            self.game_uris = []
            return
        return list(itertools.imap(lambda x: x.lstrip('0'), 
                    itertools.takewhile(lambda x: not x == last_game_id, 
                    ("%s%s%s" % (a, b, c) for a in string.digits for b in 
                    string.ascii_lowercase for c in string.ascii_lowercase
                    )))) + [last_game_id]
        
class EidoGoSource(WebSGFSource):

    game_list_url = "http://eidogo.com/games?q=+"
    game_url_str = "http://eidogo.com/backend/download.php?id=%s"
    
    def get_gameids(self):
        filehandle = urllib2.urlopen(self.game_list_url)
        data = filehandle.read()
        filehandle.close()
        return re.findall("<td><a href=\"\\./#(.*?)\">", data)
        
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
