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

under ubuntu, most of these modules should already be installed, simpleparse
is provided by the python-simpleparse module in the repository.

Next, as root, in the source folder run

python setup.py install

Done!


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

