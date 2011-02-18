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
rm /usr/bin/gogames-screensaver;
rm /usr/bin/gogames-sgf-thumbnailer;
unlink /usr/lib/gnome-screensaver/gnome-screensaver/gogames-screensaver
x=`gconftool-2 --get /desktop/gnome/thumbnailers/application@x-go-sgf/command`;
if [ "$x"=="/usr/bin/gogames-sgf-thumbnailer -s%s %u %o" ]; then 
    gconftool-2 --direct \
        --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults \
        --recursive-unset /desktop/gnome/thumbnailers/application@x-go-sgf;
fi;
