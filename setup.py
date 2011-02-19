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
import distutils.command.install
import glob
import os
import platform
import sys

class LinuxInstall(distutils.command.install.install):
    def run(self):
        distutils.command.install.install.run(self)
        os.popen("./post-install.sh")

class LinuxGogamesDistribution(Distribution):
    def __init__(self, *args):
        Distribution.__init__(self, *args)
        self.scripts = ["gogames-screensaver", "gogames-sgf-thumbnailer"]

class WindowsGogamesDistribution(Distribution):
    def __init__(self, *args):
        Distribution.__init__(self, *args)
        self.windows = [{'script': 'gogames-screensaver',
                         'icon_resources': [(1,'icons/icon.ico')]}]
        self.zipfile = None
                       
if platform.system() == "Windows":
    import py2exe
    my_distclass = WindowsGogamesDistribution
    my_install = distutils.command.install.install
elif platform.system() == "Linux":
    my_distclass = LinuxGogamesDistribution
    my_install = LinuxInstall
    
modules = [os.path.splitext(fn)[0] for fn in glob.glob("lib/*.py")]

setup(name="Go Games",
      version="0.11",
      url="https://github.com/JulianAndrews/Go-Games-Screensaver",
      description = "A screensaver which displays go games from sgf files.",
      author = "Julian Andrews",
      author_email = "jandrews271@gmail.com",
      py_modules = modules, 
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
      requires = ["cairo", "gio", "glib", "gtk", "pango", "rsvg", 
                  "simpleparse"],
      distclass = my_distclass,
      cmdclass={'install': my_install})
      
if platform.system() == "Windows":
    if os.access("dist/Go Games.scr", os.F_OK):
        os.remove("dist/Go Games.scr")
    os.rename("dist/gogames-screensaver.exe", "dist/Go Games.scr")

