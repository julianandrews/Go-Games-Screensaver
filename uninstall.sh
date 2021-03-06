#!/usr/bin/env sh
#
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

ss_dir=$(pkg-config --variable=themesdir gnome-screensaver)
rm $ss_dir/gogames-screensaver.desktop;
rm -r /usr/share/gogames-screensaver;
rm -r /etc/xdg/gogames-screensaver
rm /usr/bin/gogames-screensaver;
rm /usr/bin/gogames-sgf-thumbnailer;
rm /usr/share/gconf/defaults/10_gogames-screensaver
rm /usr/share/man/man1/gogames-screensaver.1.gz
rm /usr/share/man/man1/gogames-sgf-thumbnailer.1.gz
update-gconf-defaults
gconftool-2 --shutdown
unlink $(pkg-config --variable=privlibexecdir gnome-screensaver)/gogames-screensaver

