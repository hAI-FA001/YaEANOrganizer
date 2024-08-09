# MY MODIF

from pubsub import pub
import wx
from wx.lib.scrolledpanel import ScrolledPanel
from wx.lib.agw.floatspin import FloatSpin
import numpy as np

from pyxenoverse.gui.file_drop_target import FileDropTarget
from pyxenoverse.gui.ctrl.unknown_hex_ctrl import UnknownHexCtrl
from pyxenoverse.gui.ctrl.hex_ctrl import HexCtrl
from pyxenoverse.gui import add_entry
from yaean.helpers import convert_to_px

from pyxenoverse.esk import UNK1_I_00_NAME, UNK1_SECTION_NAMES, UNK1Section, UNK1_SECTION_SIZE, UNK1_SECTION_BYTE_ORDER


class Unk1MainPanel(wx.Panel):
    def __init__(self, parent, root, is_save_ean=True, is_main_panel=True):
        wx.Panel.__init__(self, parent)
        self.parent = parent.GetParent().GetParent()
        self.root = root
        self.filetype = 'ean' if is_save_ean else 'esk'
        self.type = 'main' if is_main_panel else 'side'

        self.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.name = wx.StaticText(self, -1, '(No file loaded)')
        self.font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.name.SetFont(self.font)

        self.open = wx.Button(self, wx.ID_OPEN, "Load")
        if is_main_panel:
            self.save = wx.Button(self, wx.ID_SAVE, "Save")
        self.scrolled_panel = ScrolledPanel(self)
        self.unk_ctrls = []

        spacing = convert_to_px(10)
        
        btns_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btns_sizer.Add(self.open)
        btns_sizer.AddSpacer(convert_to_px(spacing))
        if is_main_panel:
            btns_sizer.Add(self.save)


        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.name, 0, wx.CENTER)
        main_sizer.Add(btns_sizer)
        main_sizer.AddSpacer(convert_to_px(spacing))
        main_sizer.Add(self.scrolled_panel, 1, wx.EXPAND)
        self.SetSizer(main_sizer)


        self.Bind(wx.EVT_BUTTON, self.on_open, id=wx.ID_OPEN)
        self.Bind(wx.EVT_BUTTON, self.on_save, id=wx.ID_SAVE)

        if is_main_panel:
            self.SetDropTarget(FileDropTarget(self, "load_main_file"))
        else:
            self.SetDropTarget(FileDropTarget(self, "load_side_file"))
        
        self.scrolled_panel.Disable()


    def setup_unk(self, esk):
        self.scrolled_panel.DestroyChildren()
        
        self.I_00 = 0
        self.unk1_sections = [UNK1Section(*([0] * len(UNK1_SECTION_BYTE_ORDER))) for _ in range(esk.num_unknown_sections)]

        overall_byte_order = 'I' + UNK1_SECTION_BYTE_ORDER * esk.num_unknown_sections
        all_unk_vals = [esk.unk1_I_00] 
        for section in esk.unk1_sections: all_unk_vals.extend([*section])

        ctrl_sz = (convert_to_px(300, False), convert_to_px(25))
        gsizer = wx.FlexGridSizer(3, 10, 10)
        for idx, label in enumerate([UNK1_I_00_NAME] + UNK1_SECTION_NAMES * esk.num_unknown_sections):
            byte_order = overall_byte_order[idx]
            static_text = wx.StaticText(self.scrolled_panel, label=label)
            
            if 'bone' in label.lower():
                ctrl = wx.Choice(self.scrolled_panel, -1, choices=[b.name + f" ({idx})" for idx, b in enumerate(esk.bones)], size=ctrl_sz)
                ctrl.Select(int(all_unk_vals[idx]))

            elif 'flag' in label.lower():
                ctrl = HexCtrl(self.scrolled_panel, wx.ID_OK, size=ctrl_sz, style=wx.TE_PROCESS_ENTER, value="0x0",
                               max=0xFFFF if byte_order.lower() == 'h' else 0xFFFFFFFF)
                ctrl.SetValue(int(all_unk_vals[idx]))

            elif byte_order.lower() == 'f':
                ctrl = FloatSpin(self.scrolled_panel, -1, increment=0.01, value=0.0, digits=8, size=ctrl_sz)
                ctrl.SetValue(all_unk_vals[idx])

            else:
                ctrl = self.make_uint_ctrl(self.scrolled_panel, ctrl_sz, byte_order)
                ctrl.SetValue(str(all_unk_vals[idx]))
            
            self.unk_ctrls.append(ctrl)

            gsizer.AddSpacer(10)
            gsizer.Add(static_text, 1, wx.ALIGN_RIGHT)
            gsizer.Add(ctrl, 1, wx.ALIGN_CENTER)
            
            if (idx - 0) % 8 == 0:
                gsizer.AddSpacer(10)
                gsizer.AddSpacer(10)
                gsizer.AddSpacer(10)

        self.scrolled_panel.SetupScrolling()
        self.scrolled_panel.SetSizer(gsizer)


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
        
