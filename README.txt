Gogames Screensaver 0.10
========================

Gogames Screensaver is a gnome screensaver which replays games from SGF 
files from both local and online sources.  Also includes a thumbnailer
for sgf files.


Installation
============

First install all dependencies - Gogames Screensaver requires python 2.6 
(2.7 probably works) and the following python modules:

cairo
gio
glib
gtk
pango
rsvg
simpleparse

under ubuntu 10.10, most of these modules should already be installed, 
all of them are provided by the combination of

python-gnome2,
python-cairo,
python-simpleparse, and
python-rsvg

Next, as root, in the source folder run

python setup.py install

Done!

Alternatively, a .deb package can be found at:

http://julianandrews.github.com/Go-Games-Screensaver/


Uninstallation
==============

Gogames Screensaver comes with an uninstall script, simply run 

./uninstall.sh 

as root in the source folder.


Usage
=====
The screensaver should appear in your gnome-screensaver configuration
dialog after install, and the thumbnailer should work automatically.  
Gogames Screensaver can be configured by running

gogames-screensaver -c

