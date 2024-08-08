# MY MODIF

from pubsub import pub
import wx
from wx.lib.scrolledpanel import ScrolledPanel
import numpy as np

from pyxenoverse.gui.file_drop_target import FileDropTarget
from yaean.helpers import convert_to_px


class Unk2MainPanel(wx.Panel):
    def __init__(self, parent, root, is_save_ean=True, is_main_panel=True):
        wx.Panel.__init__(self, parent)
        self.parent = parent.GetParent().GetParent()
        self.root = root
        self.filetype = 'ean' if is_save_ean else 'esk'
        self.type = 'main' if is_main_panel else 'side'

        self.I_values = []

        self.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.name = wx.StaticText(self, -1, '(No file loaded)')
        self.font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.name.SetFont(self.font)

        self.open = wx.Button(self, wx.ID_OPEN, "Load")
        if is_main_panel:
            self.save = wx.Button(self, wx.ID_SAVE, "Save")
        self.scrolled_panel = ScrolledPanel(self)


        self.spacing = convert_to_px(10)
        
        btns_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btns_sizer.Add(self.open)
        btns_sizer.AddSpacer(convert_to_px(self.spacing))
        if is_main_panel:
            btns_sizer.Add(self.save)


        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.name, 0, wx.CENTER)
        main_sizer.Add(btns_sizer)
        main_sizer.AddSpacer(convert_to_px(self.spacing))
        main_sizer.Add(self.scrolled_panel, 1, wx.EXPAND)
        self.SetSizer(main_sizer)


        self.Bind(wx.EVT_BUTTON, self.on_open, id=wx.ID_OPEN)
        self.Bind(wx.EVT_BUTTON, self.on_save, id=wx.ID_SAVE)

        if is_main_panel:
            self.SetDropTarget(FileDropTarget(self, "load_main_file"))
        else:
            self.SetDropTarget(FileDropTarget(self, "load_side_file"))
        

        self.scrolled_panel.Disable()


    def make_uint_ctrl(self, parent, ctrl_sz, byte_order):
        def on_change(evt):
            txt = ctrl.GetValue()
            try:
                value = int(txt) if byte_order.lower() == 'i' else float(txt)
                value = min(value, 2**32)
                value = max(value, -2**32)
            except ValueError:
                pass

        ctrl = wx.TextCtrl(parent, wx.ID_OK, '0', size=ctrl_sz, style=wx.TE_PROCESS_ENTER)
        ctrl.Bind(wx.EVT_TEXT, on_change)
        
        return ctrl
    
    def on_open(self, _):
        pub.sendMessage(f'open_{self.type}_file')

    def on_save(self, _):
        pub.sendMessage(f'save_{self.filetype}')


    def setup_ctrls(self, bone_count):
        self.I_values = [0] * (2 * bone_count)
        sizer = self.populate_ctrls_in_sizer()
        self.setup_scroll_panel_with(sizer)

        
    def destroy_unk2(self):
        self.scrolled_panel.DestroyChildren()
    
    def populate_ctrls_in_sizer(self):
        self.I_ctrls = []
        ctrl_sz = (convert_to_px(500, False), convert_to_px(25))
        sizer = wx.BoxSizer(wx.VERTICAL)
        for idx in range(len(self.I_values)):
            number = f'{idx * 4:02}'
            label = f'I_{number:3}'
            
            static_text = wx.StaticText(self.scrolled_panel, label=label)
            ctrl = self.make_uint_ctrl(self.scrolled_panel, ctrl_sz, 'I')
            
            self.I_ctrls.append(ctrl)
            
            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            hsizer.Add(static_text, 0, wx.ALIGN_CENTER)
            hsizer.AddSpacer(self.spacing)
            hsizer.Add(ctrl, 0, wx.ALIGN_CENTER)

            sizer.Add(hsizer)
            if idx != len(self.I_values)-1:
                sizer.AddSpacer(self.spacing)
            
        return sizer

    def setup_scroll_panel_with(self, sizer):
        # add padding like this :moyai:
        pad_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pad_sizer.AddSpacer(self.spacing)
        pad_sizer.Add(sizer)

        self.scrolled_panel.SetupScrolling()
        self.scrolled_panel.SetSizer(pad_sizer)

        self.scrolled_panel.Enable()

    def update_unk2(self):
        self.destroy_unk2()
        
        sizer = self.populate_ctrls_in_sizer()
        self.setup_scroll_panel_with(sizer)

    def add_unk2(self, unk2_added_idxs):
        unk2_default_vals = [0, 65535]
        
        for where_to_add in unk2_added_idxs:
            self.I_values = self.I_values[:where_to_add] + unk2_default_vals + self.I_values[where_to_add:]

        self.update_unk2()
    
    def delete_unk2(self, unk2_deleted_idxs):
        for where_to_delete in unk2_deleted_idxs:
            self.I_values = self.I_values[:where_to_delete] + self.I_values[where_to_delete+1:]

        self.update_unk2()