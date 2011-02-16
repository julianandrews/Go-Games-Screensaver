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

from distutils.core import setup
import py2exe
import glob
import os

opts = {
    'py2exe': {
        'optimize': 2,
        'includes': 'cairo, pango, pangocairo, atk, gobject, gio',
        'dll_excludes': ["iconv.dll","intl.dll","libatk-1.0-0.dll",
                         "libgdk_pixbuf-2.0-0.dll","libgdk-win32-2.0-0.dll",
                         "libglib-2.0-0.dll","libgmodule-2.0-0.dll",
                         "libgobject-2.0-0.dll","libgthread-2.0-0.dll",
                         "libgtk-win32-2.0-0.dll","libpango-1.0-0.dll",
                         "libpangowin32-1.0-0.dll", "libcairo-2.dll",
                         "libfontconfig-1.dll", "libgio-2.0-0.dll", 
                         "libpangocairo-1.0-0.dll", "libpng14-14.dll",
                         "zlib1.dll", "w9xpopen.exe"]
    }
}

setup(name = 'Go Games',
      version = '0.9',
      description = 'A scressnsaver which displays go games from sgf files.',
      author = 'Julian Andrews',
      windows = [{'script': 'gogames-screensaver.py',
                  'icon_resources': [(1,'misc/icon.ico')]}],
      options = opts,
      zipfile = None)
if os.access("dist/Go Games.scr", os.F_OK):
    os.remove("dist/Go Games.scr")
os.rename("dist/gogames-screensaver.exe", "dist/Go Games.scr")
