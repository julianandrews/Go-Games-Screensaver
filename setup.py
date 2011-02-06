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
                  'icon_resources': [(1,'data/images/icon.ico')]}],
      options = opts,
      zipfile = None)
if os.access("dist/Go Games.scr", os.F_OK):
    os.remove("dist/Go Games.scr")
os.rename("dist/gogames-screensaver.exe", "dist/Go Games.scr")
