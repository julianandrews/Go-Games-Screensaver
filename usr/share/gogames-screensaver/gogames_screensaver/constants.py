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

import os
import platform

save_bad_sgf_data = False
data_folder = os.path.join(os.curdir, "usr", "share", "gogames-screensaver")

if platform.system() == 'Windows':
    config_folder = os.path.join(os.getenv("APPDATA"), "gogames-screensaver")
    cache_folder = config_folder
    default_config_folder = os.path.join(os.curdir, "etc", "xdg", 
                                         "gogames-screensaver")
elif platform.system() == 'Linux':
    import xdg.BaseDirectory
    config_folder = os.path.join(xdg.BaseDirectory.xdg_config_home, 
                                 'gogames-screensaver')
    default_config_folder = os.path.join(os.curdir, xdg.BaseDirectory.\
                xdg_config_dirs[-1].lstrip(os.path.sep), 'gogames-screensaver')
    
    cache_folder = os.path.join(xdg.BaseDirectory.xdg_cache_home, 
                                'gogames-screensaver')
else:
    raise RuntimeError("Unsuported OS: %s" % platform.system())

