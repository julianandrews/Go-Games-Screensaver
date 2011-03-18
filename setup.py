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

import platform

if platform.system() == "Windows":
    import py2exe

from distutils.core import setup, Distribution
import distutils.command.install
import distutils.command.install_egg_info
import distutils.util
import distutils.dir_util
import glob
import os

class LinuxInstall(distutils.command.install.install):

    def finalize_options(self):
        distutils.command.install.install.finalize_options(self)
        root = self.root or '/'
        self.install_lib = root
        self.install_scripts = distutils.util.change_root(root, "/usr/bin")
        self.install_data = root

    def run(self):
        distutils.command.install.install.run(self)
        ss_dir = os.popen("pkg-config --variable=themesdir "
                          "gnome-screensaver").read().strip()
        ss_exec_dir = os.popen("pkg-config --variable=privlibexecdir "
                               "gnome-screensaver").read().strip()
        gconf_dir = "/usr/share/gconf/defaults"
        bin_file = "/usr/bin/gogames-screensaver"
        if not self.root is None:
            ss_dir = distutils.util.change_root(self.root, ss_dir)
            ss_exec_dir = distutils.util.change_root(self.root, ss_exec_dir)
            gconf_dir = distutils.util.change_root(self.root, gconf_dir)
            bin_file = distutils.util.change_root(self.root, bin_file)
        distutils.dir_util.mkpath(ss_dir)
        self.copy_file("gogames-screensaver.desktop", ss_dir)
        distutils.dir_util.mkpath(gconf_dir)
        self.copy_file("10_gogames-screensaver", gconf_dir)
        distutils.dir_util.mkpath(ss_exec_dir)
        source = os.path.relpath(bin_file, ss_exec_dir)
        target = os.path.join(ss_exec_dir, os.path.basename(bin_file))
        distutils.util.execute(os.symlink, (source, target))
        distutils.util.execute(os.popen, ("update-gconf-defaults", ))
        
class LinuxEggInfoInstall(distutils.command.install_egg_info.install_egg_info):
    
    def run(self):
        pass

class LinuxGogamesDistribution(Distribution):
    def __init__(self, *args):
        Distribution.__init__(self, *args)
        self.scripts = ["usr/bin/gogames-screensaver", 
                        "usr/bin/gogames-sgf-thumbnailer"]

class WindowsGogamesDistribution(Distribution):
    def __init__(self, *args):
        Distribution.__init__(self, *args)
        self.com_server = []
        self.services = []
        self.windows = [{'script': 'gogames-screensaver',
                         'icon_resources': [(1,'icons/icon.ico')]}]
        self.console = []
        self.zipfile = None

modules = [os.path.splitext(fn)[0] for fn in 
           glob.glob(os.path.join("usr", "share", "gogames-screensaver", 
                                  "gogames_screensaver", "*.py"))]
classifiers = ["Development Status :: 4 - Beta",
               "Environment :: X11 Applications :: Gnome",
               "License :: OSI Approved :: GNU General Public License "
               "(GPL)",
               "Natural Language :: English",
               "Programming Language :: Python :: 2.6",
               "Topic :: Desktop Environment :: Screen Savers",
               "Topic :: Games/Entertainment :: Board Games"]

if platform.system() == "Windows":
    my_distclass = WindowsGogamesDistribution
    my_install = distutils.command.install.install
    my_egg_info_install = distutils.command.install_egg_info.install_egg_info
    try:
        modules.remove(os.path.join("usr", "share", "gogames-screensaver", 
                                    "gogames_screensaver", "scr_linux"))
    except ValueError:
        pass
    classifiers.append("Operating System :: Microsoft :: Windows")
elif platform.system() == "Linux":
    my_distclass = LinuxGogamesDistribution
    my_install = LinuxInstall
    my_egg_info_install = LinuxEggInfoInstall
    try:
        modules.remove("usr/share/gogames-screensaver/gogames_screensaver/"
                       "scr_windows")
    except ValueError:
        pass
    classifiers.append("Operating System :: POSIX :: Linux")

setup(name="gogames-screensaver",
      version="0.18",
      url="http://github.com/JulianAndrews/Go-Games-Screensaver",
      description = "A screensaver which displays go games from sgf files.",
      author = "Julian Andrews",
      author_email = "jandrews271@gmail.com",
      py_modules = modules, 
      keywords = ["Go", "Weiqi", "Baduk", "Screensaver", "Gnome"],
      classifiers = classifiers,
      data_files = [("usr/share/gogames-screensaver/images", 
                     glob.glob("usr/share/gogames-screensaver/images/*.svg")),
                    ("usr/share/gogames-screensaver/sgf", 
                     glob.glob("usr/share/gogames-screensaver/sgf/*.sgf")),
                    ("etc/xdg/gogames-screensaver", 
                     glob.glob("etc/xdg/gogames-screensaver/*.xml"))],
      requires = ["cairo", "gio", "glib", "gtk", "pango", "rsvg", 
                  "simpleparse"],
      distclass = my_distclass,
      cmdclass={'install': my_install,
                'install_egg_info': my_egg_info_install})
