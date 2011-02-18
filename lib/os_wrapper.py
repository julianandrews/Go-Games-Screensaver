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

data_folder = os.path.join(os.path.split(os.path.dirname(__file__))[0], "data")

if platform.system() == 'Windows':
    from scr_windows import get_mode, WinSSWindow as SSWindow
    config_folder = data_folder #Stupid hack for now
elif platform.system() == 'Linux':
    from scr_linux import GsThemeWindow as SSWindow
    config_folder = os.path.join(os.getenv("HOME"), ".gogames-screensaver")
    def get_mode():
        return None, None
else:
    raise RuntimeError("Unsuported OS: %s" % platform.system())
