# MY MODIF

from pubsub import pub
import wx
from wx.lib.scrolledpanel import ScrolledPanel
from wx.lib.agw.floatspin import FloatSpin
import numpy as np

from pyxenoverse.gui.file_drop_target import FileDropTarget
from yaean.helpers import convert_to_px

from pyxenoverse.esk import I_BYTE_ORDER, I_IDX_TO_NAME, THESE_POINT_TO_BONES


# class Unk1MainPanel(wx.Panel):
#     def __init__(self, parent, root, is_save_ean=True, is_main_panel=True):
#         wx.Panel.__init__(self, parent)
#         self.parent = parent.GetParent().GetParent()
#         self.root = root
#         self.filetype = 'ean' if is_save_ean else 'esk'
#         self.type = 'main' if is_main_panel else 'side'

#         self.SetBackgroundColour(wx.Colour(255, 255, 255))

#         self.open = wx.Button(self, wx.ID_OPEN, "Load")
#         self.save = wx.Button(self, wx.ID_SAVE, "Save")
#         self.scrolled_panel = ScrolledPanel(self)


#         self.I_values = [0] * (120 // 4 + 1)
#         self.I_ctrls = []
        
#         ctrl_sz = (convert_to_px(100, False), convert_to_px(25))
#         spacing = convert_to_px(10)
#         sizer = wx.BoxSizer(wx.VERTICAL)
#         for idx in range(len(self.I_values)):
#             number = f'{idx * 4:02}'
#             label = f'I_{number:3}'
            
#             static_text = wx.StaticText(self.scrolled_panel, label=label)
#             ctrl = self.make_uint_ctrl(self.scrolled_panel, ctrl_sz)
#             self.I_ctrls.append(ctrl)
            

#             hsizer = wx.BoxSizer(wx.HORIZONTAL)
#             hsizer.Add(static_text, 0, wx.ALIGN_CENTER)
#             hsizer.AddSpacer(spacing)
#             hsizer.Add(ctrl, 0, wx.ALIGN_CENTER)

#             sizer.Add(hsizer)
#             if idx != len(self.I_values)-1:
#                 sizer.AddSpacer(spacing)

#         # add padding like this :moya:
#         pad_sizer = wx.BoxSizer(wx.HORIZONTAL)
#         pad_sizer.AddSpacer(spacing)
#         pad_sizer.Add(sizer)

#         self.scrolled_panel.SetupScrolling()
#         self.scrolled_panel.SetSizer(pad_sizer)
        
#         btns_sizer = wx.BoxSizer(wx.HORIZONTAL)
#         btns_sizer.Add(self.open)
#         btns_sizer.AddSpacer(convert_to_px(spacing))
#         if is_main_panel:
#             btns_sizer.Add(self.save)


#         main_sizer = wx.BoxSizer(wx.VERTICAL)
#         main_sizer.Add(btns_sizer)
#         main_sizer.AddSpacer(convert_to_px(spacing))
#         main_sizer.Add(self.scrolled_panel, 1, wx.EXPAND)
#         self.SetSizer(main_sizer)


#         self.Bind(wx.EVT_BUTTON, self.on_open, id=wx.ID_OPEN)
#         self.Bind(wx.EVT_BUTTON, self.on_save, id=wx.ID_SAVE)


#     def make_uint_ctrl(self, parent, ctrl_sz):
#         def on_change(evt):
#             txt = ctrl.GetValue()
#             try:
#                 value = int(txt)
#                 value = min(value, 2**32)
#                 value = max(value, -2**32)
#             except ValueError:
#                 pass

#         ctrl = wx.TextCtrl(parent, wx.ID_OK, '0', size=ctrl_sz, style=wx.TE_PROCESS_ENTER)
#         ctrl.Bind(wx.EVT_TEXT, on_change)
        
#         return ctrl
    
#     def on_open(self, _):
#         pub.sendMessage(f'open_{self.type}_file')

#     def on_save(self, _):
#         pub.sendMessage(f'save_{self.filetype}')

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


        self.I_values = [0] * len(I_BYTE_ORDER)
        self.I_ctrls = []
        # self.I_list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT)
        # self.I_list_ctrl.InsertColumn(0, 'Unks', width=convert_to_px(100))
        
        ctrl_sz = (convert_to_px(500, False), convert_to_px(25))
        spacing = convert_to_px(10)
        sizer = wx.BoxSizer(wx.VERTICAL)
        for idx in range(len(self.I_values)):
            number = f'{I_IDX_TO_NAME[idx]:02}'
            label = f'{I_BYTE_ORDER[idx].upper()}_{number:3}'
            
            static_text = wx.StaticText(self.scrolled_panel, label=label)
            
            if I_IDX_TO_NAME[idx] in THESE_POINT_TO_BONES:
                ctrl = wx.Choice(self.scrolled_panel, -1, choices=['(No File Loaded)'], size=ctrl_sz)
                ctrl.Select(0)
                ctrl.Disable()
            elif I_BYTE_ORDER[idx].lower() == 'f':
                ctrl = FloatSpin(self.scrolled_panel, -1, increment=0.01, value=0.0, digits=8, size=ctrl_sz)
            else:
                ctrl = self.make_uint_ctrl(self.scrolled_panel, ctrl_sz, I_BYTE_ORDER[idx])
            
            self.I_ctrls.append(ctrl)
            # self.I_list_ctrl.InsertItem(idx, label)
            

            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            hsizer.Add(static_text, 0, wx.ALIGN_CENTER)
            hsizer.AddSpacer(spacing)
            hsizer.Add(ctrl, 0, wx.ALIGN_CENTER)

            sizer.Add(hsizer)
            if idx != len(self.I_values)-1:
                sizer.AddSpacer(spacing)

        # add padding like this :moya:
        pad_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pad_sizer.AddSpacer(spacing)
        pad_sizer.Add(sizer)

        self.scrolled_panel.SetupScrolling()
        self.scrolled_panel.SetSizer(pad_sizer)
        
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
