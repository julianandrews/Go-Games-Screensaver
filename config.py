# Copyright (c) 2010 Julian Andrews.
# All rights reserved.
#
# This software is provided for personal use only, and may not be 
# redistributed in whole or in part or used for any comercial purpose without
# the permision of the copyright holder.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY 
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL 
# JULIAN ANDREWS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# I will probably release this with a more permissive license at some later
# date, but for the moment want to keep my options open until I decide how
# best to distribute it.

import gtk
import optparse
import os
import xml.dom.minidom
from xml.dom.minidom import getDOMImplementation

from os_wrapper import data_folder, get_mode

class Configuration(dict):

    filename = os.path.join(data_folder, "config.xml")
    
    def __init__(self):
        super(Configuration, self).__init__()
        self.key_order = []
        self.load()
        self["mode"], self["handle"] = get_mode()
        self.parse_options()
            
    def save(self):
        impl = getDOMImplementation()
        xml_doc = impl.createDocument(None, 'config', None)
        for prop in self.key_order + [x for x in self if not x in self.
                                      key_order]:
            if prop in ('mode', 'handle'):
                continue
            value = self[prop]
            data_node = xml_doc.createElement(prop)
            data_node.appendChild(xml_doc.createTextNode(str(value)))
            if type(value) == int:
                data_node.setAttribute("type", "int")
            elif type(value) == bool:
                data_node.setAttribute("type", "bool")
            xml_doc.documentElement.appendChild(data_node)
        xml = xml_doc.toprettyxml()
        with open(self.filename, 'w') as f:
            f.write(xml)
        
    def load(self):
        xml_doc = xml.dom.minidom.parse(self.filename)
        for node in xml_doc.firstChild.childNodes:
            if not node.nodeType == node.TEXT_NODE:
                key = str(node.nodeName)
                val = str(node.firstChild.data).strip()
                if node.getAttribute("type") == "int":
                    self[key] = int(val)
                elif node.getAttribute("type") == "bool":
                    self[key] = False if val == 'False' else True
                else:
                    self[key] = val
                if not key in self.key_order:
                    self.key_order.append(key)
    
    def parse_options(self):
        parser = optparse.OptionParser()
        parser.add_option("-d", dest="sgf_folder", 
                          help="directory containing sgf files to display", 
                          metavar="DIR")
        parser.add_option("-m", "--movedelay", dest="movedelay",
                          help="delay between move in ms", type="int", 
                          metavar="MS")
        parser.add_option("-s", "--startdelay", dest="startdelay", 
                          help="delay at start of new game in ms", type="int", 
                          metavar="MS")
        parser.add_option("-e", "--enddelay", dest="enddelay",
                          help="delay at end of a finished game in ms", type="int", 
                          metavar="MS")
        parser.add_option("-a", "--noannotations", action="store_true", 
                          help="disable annotations")
        parser.add_option("-k", "--nomarkup", action="store_true", 
                          help="disable markup")
        parser.add_option("--kgs", action="store_true", 
                          help="Use games from kgs")
        parser.add_option("--gokifu", action="store_true", 
                          help="Use games from gokifu.com")
        parser.add_option("--eidogo", action="store_true", 
                          help="Use games from eidogo.com")
        options, args = parser.parse_args()
        if options.kgs:
            self['source'] = 'kgs'
        elif options.gokifu:
            self['source'] = 'gokifu'
        elif options.eidogo:
            self['source'] = 'eidogo'
        self['move_delay'] = options.movedelay or self['move_delay']
        self['start_delay'] = options.startdelay or self['start_delay']
        self['end_delay'] = options.enddelay or self['end_delay']
        if options.noannotations:
            self['annotations'] = False
        if options.nomarkup:
            self['markup'] = False


class SSConfigWindow(gtk.Window):
    def __init__(self, conf):
        super(SSConfigWindow, self).__init__()
        self.conf = conf
        self.set_title("Go Games Screensaver Preferences")
        self.connect("destroy", gtk.main_quit)
        self.set_resizable(False)
        #if not conf.get(handle) == None:
        #    handle = conf[handle]
        #    self.set_transient_for()
        #    self.set_parent()
        #    self.set_destroy_with_parent(True)
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
        if self.conf["source"] == "kgs":
            self.kgs_check.set_active(True)
        if self.conf["source"] == "eidogo":
            self.eidogo_check.set_active(True)
        if self.conf["source"] == "gokifu":
            self.gokifu_check.set_active(True)
        if self.conf["source"] == "file":
            self.file_check.set_active(True)
        self.markup_check.set_active(self.conf["markup"])
        self.annotations_check.set_active(self.conf["annotations"])
        self.file_chooser.set_filename(self.conf["sgf_folder"])
        
    def on_cancel(self, widget):
        self.destroy()

    def on_apply(self, widget):
        self.conf["move_delay"] = int(self.move_delay_spinner.get_value() *
                                      1000)
        self.conf["start_delay"] = int(self.start_delay_spinner.get_value() *
                                       1000)
        self.conf["end_delay"] = int(self.end_delay_spinner.get_value() * 1000)
        self.conf["annotations"] = bool(self.annotations_check.get_active())
        self.conf["markup"] = bool(self.markup_check.get_active())
        self.conf["sgf_folder"] = self.file_chooser.get_filename()
        self.conf.save()
    
    def on_ok(self, widget):
        self.on_apply(widget)
        self.destroy()

class DelaySpinButton(gtk.SpinButton):
    def __init__(self):
        super(DelaySpinButton, self).__init__()
        self.configure(None, 2, 1)
        self.set_range(0, 3600)
        self.set_increments(.1, 5)
