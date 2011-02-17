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

from distutils.core import setup, Distribution
import glob
import os
import platform

class LinuxDistribution(Distribution):
    def __init__(self, *args):
        Distribution.__init__(self, *args)
        self.scripts = ["gogames-screensaver", "gogames-sgf-thumbnailer"]
        self.options = "--install-lib=/usr/lib/gogames-screensaver " \
                       "--install-data=/usr/share/gogames-screensaver " \
                       "--install-scripts=/usr/bin"

class WindowsDistribution(Distribution):
    def __init__(self, *args):
        Distribution.__init__(self, *args)
        self.windows = [{'script': 'gogames-screensaver.py',
                         'icon_resources': [(1,'misc/icon.ico')]}]
        self.options = {
            'py2exe': {
            'optimize': 2,
            'includes': 'cairo, pango, pangocairo, atk, gobject, gio',
            'dll_excludes': ["iconv.dll","intl.dll","libatk-1.0-0.dll",
                             "libgdk_pixbuf-2.0-0.dll","libcairo-2.dll",
                             "libgdk-win32-2.0-0.dll","libglib-2.0-0.dll",
                             "libgmodule-2.0-0.dll","libgobject-2.0-0.dll",
                             "libgthread-2.0-0.dll","libgtk-win32-2.0-0.dll",
                             "libpango-1.0-0.dll","libpangowin32-1.0-0.dll",
                             "libfontconfig-1.dll", "libgio-2.0-0.dll", 
                             "libpangocairo-1.0-0.dll", "libpng14-14.dll",
                             "zlib1.dll", "w9xpopen.exe"]}}
        self.zipfile = None
                       
if platform.system() == "Windows":
    import py2exe
    my_distclass = WindowsDistribution
elif platform.system() == "Linux":
    my_distclass = LinuxDistribution

setup(name="Go Games",
      version="0.10",
      url="https://github.com/JulianAndrews/Go-Games-Screensaver",
      description = "A screensaver which displays go games from sgf files.",
      author = "Julian Andrews",
      author_email = "jandrews271@gmail.com",
      packages = ["gogames_screensaver"],
      package_dir = {"lib": "gogames_screensaver"},
      py_modules = glob.glob("*.py"),
      keywords = ["Go", "Weiqi", "Baduk", "Screensaver", "Gnome"],
      classifiers = ["Development Status :: 4 - Beta",
                     "Environment :: X11 Applications :: Gnome",
                     "License :: OSI Approved :: GNU General Public License "
                     "(GPL)",
                     "Natural Language :: English",
                     "Operating System :: POSIX :: Linux",
                     "Programming Language :: Python :: 2.6",
                     "Topic :: Desktop Environment :: Screen Savers",
                     "Topic :: Games/Entertainment :: Board Games"],
      data_files = [("images", glob.glob("data/images/*.svg")),
                    ("sgf", glob.glob("data/sgf/*.sgf"))],
      distclass=my_distclass)
      
if platform.system() == "Windows":
    if os.access("dist/Go Games.scr", os.F_OK):
        os.remove("dist/Go Games.scr")
    os.rename("dist/gogames-screensaver.exe", "dist/Go Games.scr")
