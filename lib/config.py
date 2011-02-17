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
#
# Todo:
#   Restructure config data to simplify code

import gtk
import optparse
import os
import shutil
import xml.dom.minidom
from xml.dom.minidom import getDOMImplementation

from os_wrapper import data_folder, config_folder, get_mode

class Configuration(dict):

    filename = 'config.xml'
    default_filename = 'default_config.xml'
    xml_props = ('move_delay', 'start_delay', 'end_delay','markup', 
                 'annotations', 'sgf_folder')
    xml_prop_types = (int, int, int, int, int, str)
    xml_prop_dict = dict(zip(xml_props, xml_prop_types))
    
    def __init__(self):
        super(Configuration, self).__init__()
        self.load()
        self['mode'], self['handle'] = get_mode()
        self.parse_options()
            
    def save(self):
        impl = getDOMImplementation()
        xml_doc = impl.createDocument(None, 'config', None)
        for prop in self.xml_props:
            value = self[prop]
            data_node = xml_doc.createElement(prop)
            data_node.appendChild(xml_doc.createTextNode(str(value)))
            xml_doc.documentElement.appendChild(data_node)
        for source in self['sources']:
            data_node = xml_doc.createElement('source')
            data_node.appendChild(xml_doc.createTextNode(source))
            xml_doc.documentElement.appendChild(data_node)
        xml = xml_doc.toprettyxml()
        with open(os.path.join(config_folder, self.filename), 'w') as f:
            f.write(xml)
        
    def load(self):
        if not os.path.isfile(os.path.join(config_folder, self.filename)):
            if not os.path.isdir(config_folder):
                os.mkdir(config_folder)
            shutil.copy(os.path.join(data_folder, self.default_filename), 
                        os.path.join(config_folder, self.filename))
        self["sources"] = []
        xml_doc = xml.dom.minidom.parse(os.path.join(config_folder, 
                                                     self.filename))
        for node in xml_doc.firstChild.childNodes:
            if not node.nodeType == node.TEXT_NODE:
                key = str(node.nodeName)
                val = str(node.firstChild.data).strip()
                if key == 'source':
                    self['sources'].append(val)
                else:
                    self[key] = self.xml_prop_dict[key](val)
            
    def parse_options(self):
        parser = optparse.OptionParser(usage="usage: %prog [options]")
        parser.add_option("-d", dest="sgf_folder", default=self['sgf_folder'],
                          help="directory containing sgf files to display", 
                          metavar="DIR")
        parser.add_option("-m", dest="move_delay", metavar="MS", type="int",
                          default=self['move_delay'], 
                          help="delay between move in ms")
        parser.add_option("-s", dest="start_delay", metavar="MS", type="int",
                          default=self['start_delay'],
                          help="delay at start of new game in ms")
        parser.add_option("-e", dest="end_delay", metavar="MS", type="int",
                          default=self['end_delay'],  
                          help="delay at end of a finished game in ms")
        parser.add_option("-a", dest="annotations", action="store_const", 
                          const=0, default=self['annotations'], 
                          help="disable annotations")
        parser.add_option("-k", dest="markup", action="store_const", const=0, 
                          default=self['markup'], help="disable markup")
        parser.add_option("-f", dest="fullscreen", action="store_true",
                          default=False, help="fullscreen mode")
        parser.add_option("--kgs", action="append_const", dest="sources",
                          const="kgs", help="use games from kgs.fuseki.info")
        parser.add_option("--gokifu", action="append_const", dest="sources",
                          const="gokifu", help="use games from gokifu.com")
        parser.add_option("--eidogo", action="append_const", dest="sources",
                          const="eidogo", help="use games from eidogo.com")
        parser.add_option("--file", action="append_const", dest="sources",
                          const="file", help="use games from local files")
        parser.add_option("-c", dest="mode", action="store_const", const="c",
                          default=self['mode'], 
                          help="open the configuration dialog")
        parser.add_option("--dark", dest="dark", action="store_true",
                          default=False, help="make the board dark")
        options, args = parser.parse_args()
        if options.sources is None:
            options.sources = self['sources']
        self.update(vars(options))

class SSConfigWindow(gtk.Window):
    def __init__(self, conf):
        super(SSConfigWindow, self).__init__()
        self.conf = conf
        self.set_title("Go Games Screensaver Preferences")
        self.connect("destroy", gtk.main_quit)
        self.set_resizable(False)
        self.handle = conf.get('handle')
        vbox = gtk.VBox(spacing=6)
        align = gtk.Alignment()
        align.set_padding(12, 12, 12, 12)
        align.add(vbox)
        delays_label = gtk.Label()
        delays_label.set_markup("<b>Delays</b>")
        delays_align = gtk.Alignment()
        delays_align.add(delays_label)
        vbox.pack_start(delays_align)
        delays_align = gtk.Alignment()
        delays_align.set_padding(0, 0, 12, 0)
        vbox.pack_start(delays_align)
        
        table = gtk.Table(3, 2)
        table.set_row_spacings(6)
        table.set_col_spacings(12)
        move_delay_label = gtk.Label("Move Delay (s):")
        move_delay_label.set_alignment(0, 0.5)
        table.attach(move_delay_label, 0, 1, 0, 1)
        self.move_delay_spinner = DelaySpinButton()
        table.attach(self.move_delay_spinner, 1, 2, 0, 1)
        start_delay_label = gtk.Label("Start Delay (s):")
        start_delay_label.set_alignment(0, 0.5)
        table.attach(start_delay_label, 0, 1, 1, 2)
        self.start_delay_spinner = DelaySpinButton()
        table.attach(self.start_delay_spinner, 1, 2, 1, 2)
        end_delay_label = gtk.Label("End Delay (s):")
        end_delay_label.set_alignment(0, 0.5)
        table.attach(end_delay_label, 0, 1, 2, 3)
        self.end_delay_spinner = DelaySpinButton()
        table.attach(self.end_delay_spinner, 1, 2, 2, 3)
        delays_align.add(table)
        
        sources_label = gtk.Label()
        sources_label.set_markup("<b>Sources</b>")
        sources_label_align = gtk.Alignment()
        sources_label_align.add(sources_label)
        vbox.pack_start(sources_label_align)
        
        sources_align = gtk.Alignment()
        sources_align.set_padding(0, 12, 12, 0)
        vbox.pack_start(sources_align)
        sources_vbox = gtk.VBox()
        self.kgs_check = gtk.CheckButton("KGS sgf files")
        sources_vbox.pack_start(self.kgs_check)
        self.gokifu_check = gtk.CheckButton("GoKifu.com sgf files")
        sources_vbox.pack_start(self.gokifu_check)
        self.eidogo_check = gtk.CheckButton("EidoGo.com sgf files")
        sources_vbox.pack_start(self.eidogo_check)
        self.file_check = gtk.CheckButton("Local sgf files")
        sources_vbox.pack_start(self.file_check)
        file_chooser_hbox = gtk.HBox(spacing = 12)
        file_chooser_label = gtk.Label("Local SGF file directory:")
        file_chooser_hbox.pack_start(file_chooser_label)
        self.file_chooser = gtk.FileChooserButton("Select Folder")
        self.file_chooser.set_width_chars(50)
        self.file_chooser.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        file_chooser_hbox.pack_start(self.file_chooser)
        sources_vbox.pack_start(file_chooser_hbox)
        sources_align.add(sources_vbox)
        
        display_label = gtk.Label()
        display_label.set_markup("<b>Display</b>")
        display_label_align = gtk.Alignment()
        display_label_align.add(display_label)
        vbox.pack_start(display_label_align)
        
        display_align = gtk.Alignment()
        display_align.set_padding(0, 12, 12, 0)
        vbox.pack_start(display_align)
        display_vbox = gtk.VBox()
        self.markup_check = gtk.CheckButton("Display Markup")
        display_vbox.pack_start(self.markup_check)
        self.annotations_check = gtk.CheckButton("Display Annotations")
        display_vbox.pack_start(self.annotations_check)
        display_align.add(display_vbox)
        
        button_box = gtk.HButtonBox()
        button_box.set_layout(gtk.BUTTONBOX_END)
        button_box.set_spacing(12)
        apply_button = gtk.Button(stock=gtk.STOCK_APPLY)
        apply_button.connect("clicked", self.on_apply)
        button_box.add(apply_button)
        cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
        cancel_button.connect("clicked", self.on_cancel)
        button_box.add(cancel_button)
        ok_button = gtk.Button(stock=gtk.STOCK_OK)
        ok_button.connect("clicked", self.on_ok)
        button_box.add(ok_button)
        vbox.pack_start(button_box)
        self.add(align)
        
        self.load_conf()
        
    def load_conf(self):
        self.move_delay_spinner.set_value(self.conf["move_delay"]/1000.0)
        self.start_delay_spinner.set_value(self.conf["start_delay"]/1000.0)
        self.end_delay_spinner.set_value(self.conf["end_delay"]/1000.0)
        if 'kgs' in self.conf["sources"]:
            self.kgs_check.set_active(True)
        if "eidogo" in self.conf["sources"]:
            self.eidogo_check.set_active(True)
        if "gokifu" in self.conf["sources"]:
            self.gokifu_check.set_active(True)
        if "file" in self.conf["sources"]:
            self.file_check.set_active(True)
        self.markup_check.set_active(self.conf["markup"])
        self.annotations_check.set_active(self.conf["annotations"])
        self.file_chooser.set_filename(self.conf["sgf_folder"])

    def update_conf(self):
        self.conf['move_delay'] = int(round(self.move_delay_spinner.get_value() 
                                            * 1000))
        self.conf['start_delay'] = int(round(
                                   self.start_delay_spinner.get_value() * 1000))
        self.conf['end_delay'] = int(round(self.end_delay_spinner.get_value() 
                                           * 1000))
        self.conf['annotations'] = int(self.annotations_check.get_active())
        self.conf['markup'] = int(self.markup_check.get_active())
        self.conf['sgf_folder'] = self.file_chooser.get_filename()
        self.conf['sources'] = []
        if self.file_check.get_active():
            self.conf['sources'].append('file') 
        if self.kgs_check.get_active():
            self.conf['sources'].append('kgs')
        if self.gokifu_check.get_active():
            self.conf['sources'].append('gokifu')
        if self.eidogo_check.get_active():
            self.conf['sources'].append('eidogo')
        self.conf.save()
        
    def on_apply(self, widget):
        self.update_conf()

    def on_cancel(self, widget):
        self.destroy()

    def on_ok(self, widget):
        self.update_conf()
        self.destroy()

class DelaySpinButton(gtk.SpinButton):
    def __init__(self):
        super(DelaySpinButton, self).__init__()
        self.configure(None, 2, 1)
        self.set_range(0, 3600)
        self.set_increments(.1, 5)
