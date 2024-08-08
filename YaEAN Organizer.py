#!/usr/local/bin/python3.6
import os
import sys
import traceback

from pubsub import pub
import wx
from wx.lib.dialogs import MultiMessageDialog

from pyxenoverse.ean import EAN
from pyxenoverse.esk import ESK, I_BYTE_ORDER, I_IDX_TO_NAME, THESE_POINT_TO_BONES
from pyxenoverse.gui import create_backup
from yaean.panels.anim_main import AnimMainPanel
from yaean.panels.anim_side import AnimSidePanel
from yaean.panels.bone_main import BoneMainPanel
from yaean.panels.bone_side import BoneSidePanel
from yaean.panels.edit_unk1_main import Unk1MainPanel
from yaean.panels.edit_unk2_main import Unk2MainPanel
from yaean.helpers import build_anim_list, build_bone_tree, build_unk1_list, build_unk2_list, convert_to_px

import yaean.darkmode as darkmode


VERSION = '0.4.1'


class MainWindow(wx.Frame):
    def __init__(self, parent, title, dirname, filename):
        sys.excepthook = self.exception_hook
        self.copied_animations = None
        self.copied_bones = None
        self.copied_bone_info = None
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)

        # A "-1" in the size parameter instructs wxWidgets to use the default size.
        # In this case, we select 200px width and the default height.
        wx.Frame.__init__(self, parent, title=title, size=(convert_to_px(1200, False),convert_to_px(800)))
        self.statusbar = self.CreateStatusBar() # A Statusbar in the bottom of the window

        # Setting up the menu.
        filemenu= wx.Menu()
        menu_about= filemenu.Append(wx.ID_ABOUT)
        menu_exit = filemenu.Append(wx.ID_EXIT)

        # Creating the menubar.
        menu_bar = wx.MenuBar()
        menu_bar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menu_bar)  # Adding the MenuBar to the Frame content.

        # Publisher
        pub.subscribe(self.open_main_file, 'open_main_file')
        pub.subscribe(self.load_main_file, 'load_main_file')
        pub.subscribe(self.open_side_file, 'open_side_file')
        pub.subscribe(self.load_side_file, 'load_side_file')
        pub.subscribe(self.save_ean, 'save_ean')
        pub.subscribe(self.save_esk, 'save_esk')
        pub.subscribe(self.copy_bone_info, 'copy_bone_info')

        pub.subscribe(self.add_unk2, "add_unk2")  # MY MODIF
        pub.subscribe(self.delete_unk2, "delete_unk2")  # MY MODIF

        # Events
        self.Bind(wx.EVT_MENU, self.on_exit, menu_exit)
        self.Bind(wx.EVT_MENU, self.on_about, menu_about)
        
        # Tabs
        self.main_notebook = wx.Notebook(self)

        self.ean_main_notebook = wx.Notebook(self.main_notebook)
        self.ean_main_notebook.SetBackgroundColour(wx.Colour('grey'))
        self.esk_main_notebook = wx.Notebook(self.main_notebook)
        self.main_notebook.AddPage(self.ean_main_notebook, "EAN")
        self.main_notebook.AddPage(self.esk_main_notebook, "ESK")

        self.anim_main_panel = AnimMainPanel(self.ean_main_notebook, self)
        self.bone_main_panel = BoneMainPanel(self.ean_main_notebook, self, "EAN")
        self.unk1_panel_ean = Unk1MainPanel(self.ean_main_notebook, self)  # MY MODIF
        self.unk2_panel_ean = Unk2MainPanel(self.ean_main_notebook, self)  # MY MODIF
        self.ean_main_notebook.AddPage(self.anim_main_panel, "Animation List")
        self.ean_main_notebook.AddPage(self.bone_main_panel, "Bone List")
        self.ean_main_notebook.AddPage(self.unk1_panel_ean, "Bone Control")  # MY MODIF
        self.ean_main_notebook.AddPage(self.unk2_panel_ean, "Unk2 Section")  # MY MODIF


        self.esk_main_panel = BoneMainPanel(self.esk_main_notebook, self, "ESK")
        self.unk1_panel_esk = Unk1MainPanel(self.esk_main_notebook, self, is_save_ean=False)  # MY MODIF
        self.unk2_panel_esk = Unk2MainPanel(self.esk_main_notebook, self, is_save_ean=False)  # MY MODIF
        self.esk_main_notebook.AddPage(self.esk_main_panel, "Bone List")
        self.esk_main_notebook.AddPage(self.unk1_panel_esk, "Bone Control")  # MY MODIF
        self.esk_main_notebook.AddPage(self.unk2_panel_esk, "Unk2 Section")  # MY MODIF


        # Other view
        self.side_notebook = wx.Notebook(self)

        self.ean_side_notebook = wx.Notebook(self.side_notebook)
        self.ean_side_notebook.SetBackgroundColour(wx.Colour('grey'))
        self.esk_side_notebook = wx.Notebook(self.side_notebook)
        self.side_notebook.AddPage(self.ean_side_notebook, "EAN")
        self.side_notebook.AddPage(self.esk_side_notebook, "ESK")

        self.anim_side_panel = AnimSidePanel(self.ean_side_notebook, self)
        self.bone_side_panel = BoneSidePanel(self.ean_side_notebook, self, "EAN")
        self.unk1_panel_side_ean = Unk1MainPanel(self.ean_side_notebook, self, is_main_panel=False)  # MY MODIF
        self.unk2_panel_side_ean = Unk2MainPanel(self.ean_side_notebook, self, is_main_panel=False)  # MY MODIF
        self.ean_side_notebook.AddPage(self.anim_side_panel, "Animation List")
        self.ean_side_notebook.AddPage(self.bone_side_panel, "Bone List")
        self.ean_side_notebook.AddPage(self.unk1_panel_side_ean, "Bone Control")  # MY MODIF
        self.ean_side_notebook.AddPage(self.unk2_panel_side_ean, "Unk2 Section")  # MY MODIF

        self.esk_side_panel = BoneSidePanel(self.esk_side_notebook, self, "ESK")
        self.unk1_panel_side_esk = Unk1MainPanel(self.esk_side_notebook, self, is_save_ean=False, is_main_panel=False)  # MY MODIF
        self.unk2_panel_side_esk = Unk2MainPanel(self.esk_side_notebook, self, is_save_ean=False, is_main_panel=False)  # MY MODIF
        self.esk_side_notebook.AddPage(self.esk_side_panel, "Bone List")
        self.esk_side_notebook.AddPage(self.unk1_panel_side_esk, "Bone Control")  # MY MODIF
        self.esk_side_notebook.AddPage(self.unk2_panel_side_esk, "Unk2 Section")  # MY MODIF

        # MY MODIF
        self.toggle_dark_mode_button = wx.ToggleButton(self, label='Toggle Dark')
        self.toggle_dark_mode_button.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggle_dark)


        # Sizer
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.main_notebook, 1, wx.ALL|wx.EXPAND)
        hsizer.Add(self.side_notebook, 1, wx.ALL|wx.EXPAND)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.toggle_dark_mode_button, 0, wx.EXPAND)  # MY MODIF
        self.sizer.Add(hsizer, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.SetBackgroundColour("White")  # MY MODIF

        # Lists
        self.main = {
            'dirname': '',
            'ean': None,
            'esk': None,
            'notebook': self.main_notebook,
            'anim_panel': self.anim_main_panel,
            'ean_bone_panel': self.bone_main_panel,
            'esk_bone_panel': self.esk_main_panel,
            
            # MY MODIF
            'unk1_panel_ean': self.unk1_panel_ean,
            'unk1_panel_esk': self.unk1_panel_esk,
            'unk2_panel_ean': self.unk2_panel_ean,
            'unk2_panel_esk': self.unk2_panel_esk,

            'anim_list': self.anim_main_panel.anim_list,
            'ean_bone_list': self.bone_main_panel.bone_list,
            'esk_bone_list': self.esk_main_panel.bone_list,
            
            # MY MODIF
            'unk1_list_ean': self.unk1_panel_ean.I_ctrls,
            'unk1_list_esk': self.unk1_panel_esk.I_ctrls,
        }

        self.side = {
            'dirname': '',
            'ean': None,
            'esk': None,
            'notebook': self.side_notebook,
            'anim_panel': self.anim_side_panel,
            'ean_bone_panel': self.bone_side_panel,
            'esk_bone_panel': self.esk_side_panel,
            
            # MY MODIF
            'unk1_panel_ean': self.unk1_panel_side_ean,
            'unk1_panel_esk': self.unk1_panel_side_esk,
            'unk2_panel_ean': self.unk2_panel_side_ean,
            'unk2_panel_esk': self.unk2_panel_side_esk,
            
            'anim_list': self.anim_side_panel.anim_list,
            'ean_bone_list': self.bone_side_panel.bone_list,
            'esk_bone_list': self.esk_side_panel.bone_list,
            
            # MY MODIF
            'unk1_list_ean': self.unk1_panel_side_ean.I_ctrls,
            'unk1_list_esk': self.unk1_panel_side_esk.I_ctrls
        }

        self.sizer.Layout()
        self.Show()

        if filename:
            self.load_main_file(dirname, filename)

    def exception_hook(self, e, value, trace):
        with MultiMessageDialog(self, '', 'Error', ''.join(traceback.format_exception(e, value, trace)), wx.OK) as dlg:
            dlg.ShowModal()

    def on_about(self, _):
        # Create a message dialog box
        with wx.MessageDialog(self, " Yet another EAN Organizer v{} by Kyonko Yuuki".format(VERSION),
                              "About YaEAN Organizer", wx.OK) as dlg:
            dlg.ShowModal() # Shows it

    def on_exit(self, _):
        self.Close(True)  # Close the frame.

    def open_file(self, obj):
        with wx.FileDialog(self, "Choose a file", obj['dirname'], "", "*.ean;*.esk", wx.FD_OPEN) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.load_file(dlg.GetDirectory(), dlg.GetFilename(), obj)

    def load_file(self, dirname, filename, obj):
        obj['dirname'] = dirname
        path = os.path.join(obj['dirname'], filename)
        self.statusbar.SetStatusText("Loading...")
        new_ean = EAN()
        new_esk = ESK()
        if new_ean.load(path):
            obj['ean'] = new_ean
            build_anim_list(obj['anim_list'], obj['ean'])
            build_bone_tree(obj['ean_bone_list'], obj['ean'].skeleton)
            
            # MY MODIF
            do_build_unk1 = new_ean.skeleton.m_have_128_unknown_bytes
            if not do_build_unk1:
                obj['unk1_panel_ean'].scrolled_panel.Disable()
                with wx.MessageDialog(self,
                                      (f"Unk1 Offset ({new_ean.skeleton.unknown_offset_0}) is Zero"
                                      if not new_ean.skeleton.unknown_offset_0 else
                                      f"File can't hold Unk1 (File size is {new_ean.skeleton.fsize}, but Unk1 ends at {new_ean.skeleton.base_skeleton_address + new_ean.skeleton.unknown_offset_0 + 4*31})")
                                      + "\nDo you want to add Unk1?",
                                "Add Unk1", wx.YES | wx.NO) as dlg:
                    if dlg.ShowModal() == wx.ID_YES:
                        new_ean.skeleton.unk1_list = [0] * len(I_BYTE_ORDER)
                        do_build_unk1 = True
                        new_ean.skeleton.m_have_128_unknown_bytes = True
            if do_build_unk1:
                obj['unk1_panel_ean'].scrolled_panel.Enable()
                build_unk1_list(obj['unk1_list_ean'], obj['ean'].skeleton)

            # MY MODIF
            obj['unk2_panel_ean'].setup_ctrls(new_ean.skeleton.bone_count)
            obj['unk2_list_ean'] = obj['unk2_panel_ean'].I_ctrls
            build_unk2_list(obj['unk2_list_ean'], obj['ean'].skeleton.unk2_list)

            # MY MODIF
            obj['unk1_panel_ean'].name.SetLabel(filename)
            obj['unk1_panel_ean'].Layout()
            obj['unk2_panel_ean'].name.SetLabel(filename)
            obj['unk2_panel_ean'].Layout()
                
            obj['anim_panel'].name.SetLabel(filename)
            obj['anim_panel'].Layout()
            obj['ean_bone_panel'].name.SetLabel(filename)
            obj['ean_bone_panel'].skeletonIdCtrl.Enable()
            obj['ean_bone_panel'].skeletonIdCtrl.SetValue(str(obj['ean'].skeleton.skeletonId))
            obj['ean_bone_panel'].Layout()
            obj['notebook'].ChangeSelection(0)
            obj['notebook'].Layout()
            if obj['notebook'] == self.side['notebook']:
                self.copied_animations = None
        elif new_esk.load(path):
            obj['esk'] = new_esk
            build_bone_tree(obj['esk_bone_list'], obj['esk'])
            
            # MY MODIF
            do_build_unk1 = new_esk.m_have_128_unknown_bytes
            if not do_build_unk1:
                obj['unk1_panel_esk'].scrolled_panel.Disable()
                with wx.MessageDialog(self,
                                      (f"Unk1 Offset ({new_esk.unknown_offset_0}) is Zero"
                                      if not new_esk.unknown_offset_0 else
                                      f"File can't hold Unk1 (File size is {new_esk.fsize}, but Unk1 ends at {new_esk.base_skeleton_address + new_esk.unknown_offset_0 + 4*31})")
                                      + "\nDo you want to add Unk1?",
                                "Add Unk1", wx.YES | wx.NO) as dlg:
                    if dlg.ShowModal() == wx.ID_YES:
                        new_esk.unk1_list = [0] * len(I_BYTE_ORDER)
                        do_build_unk1 = True
                        new_esk.m_have_128_unknown_bytes = True
            if do_build_unk1:
                obj['unk1_panel_esk'].scrolled_panel.Enable()
                build_unk1_list(obj['unk1_list_esk'], obj['esk'])

            # MY MODIF
            obj['unk2_panel_esk'].setup_ctrls(new_esk.bone_count)
            obj['unk2_list_esk'] = obj['unk2_panel_esk'].I_ctrls
            build_unk2_list(obj['unk2_list_esk'], obj['esk'].unk2_list)

            # MY MODIF
            obj['unk1_panel_esk'].name.SetLabel(filename)
            obj['unk1_panel_esk'].Layout()
            obj['unk2_panel_esk'].name.SetLabel(filename)
            obj['unk2_panel_esk'].Layout()
            
            obj['esk_bone_panel'].name.SetLabel(filename)
            obj['esk_bone_panel'].skeletonIdCtrl.Enable()
            obj['esk_bone_panel'].skeletonIdCtrl.SetValue(str(obj['esk'].skeletonId))
            obj['esk_bone_panel'].Layout()
            obj['notebook'].ChangeSelection(1)
            obj['notebook'].Layout()
        else:
            with wx.MessageDialog(self, "{} is not a valid EAN/ESK".format(filename), "Warning") as dlg:
                dlg.ShowModal()
            return

        # TODO: Don't reset everything
        if obj['ean_bone_panel'] == self.side['ean_bone_panel']:
            self.side['ean_bone_panel'].deselect_all()
            self.side['esk_bone_panel'].deselect_all()
            self.main['ean_bone_panel'].copied_bones = None
            self.main['esk_bone_panel'].copied_bones = None
            self.copied_bone_info = None

        self.statusbar.SetStatusText("Loaded {}".format(path))

    def open_main_file(self):
        self.open_file(self.main)

    def load_main_file(self, dirname, filename):
        self.load_file(dirname, filename, self.main)

    def open_side_file(self):
        self.open_file(self.side)

    def load_side_file(self, dirname, filename):
        self.load_file(dirname, filename, self.side)

    def save_file(self, obj, filetype):
        if obj[filetype.lower()] is None:
            with wx.MessageDialog(self, " No {} Loaded".format(filetype), "Warning", wx.OK) as dlg:
                dlg.ShowModal()
            return

        
        # MY MODIF
        # update Unk values here
        esk_to_edit = obj['ean'].skeleton if filetype.lower() == 'ean' else obj['esk']
        if esk_to_edit.m_have_128_unknown_bytes:
            unk1_vals = [ctrl.GetSelection() if I_IDX_TO_NAME[idx] in THESE_POINT_TO_BONES else ctrl.GetValue()
                         for idx, ctrl in enumerate(obj[f'unk1_list_{filetype.lower()}'])]
            unk1_vals = [float(val) if I_BYTE_ORDER[idx].lower() == 'f' else int(val)
                         for idx, val in enumerate(unk1_vals)]
            esk_to_edit.unk1_list = unk1_vals
            
        esk_to_edit.unk2_list = [int(ctrl.GetValue()) for ctrl in obj[f'unk2_list_{filetype.lower()}']]    
        esk_to_edit.skeletonId = int(obj[f'{filetype.lower()}_bone_panel'].skeletonIdCtrl.GetValue())

        
        with wx.FileDialog(self, "Choose a file", obj['dirname'], "", "*." + filetype.lower(), wx.FD_SAVE) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetFilename()
                obj['dirname'] = dlg.GetDirectory()
                self.statusbar.SetStatusText("Saving...")
                create_backup(obj['dirname'], filename)
                path = os.path.join(obj['dirname'], filename)
                removed_nodes = obj[filetype.lower()].save(path)
                msg = ''
                if removed_nodes:
                    msg = "The following animation nodes were removed:\n{}".format(
                        '\n'.join([' * ' + node for node in sorted(removed_nodes)]))
                self.statusbar.SetStatusText("Saved {}".format(path))
                with MultiMessageDialog(
                        self, "Saved to {} successfully".format(path), filetype + " Saved", msg, wx.OK) as saved:
                    saved.ShowModal()

    def save_ean(self):
        self.save_file(self.main, "EAN")

    def save_esk(self):
        self.save_file(self.main, "ESK")

    def copy_bone_info(self, filename, bone):
        self.copied_bone_info = filename, bone

    # MY MODIF
    def on_toggle_dark(self, event):
        darkmode.darkMode(self, "White")
        # prev_label = self.toggle_dark_mode_button.GetLabel()
        # next_mode = 'White' if 'dark' in prev_label.lower() else 'Dark'
        # self.toggle_dark_mode_button.SetLabel(f"Toggle {next_mode}")
        pub.sendMessage('toggle_dark_mode', e="light" if self.GetBackgroundColour() == "White" else "dark")
    
    # MY MODIF
    def add_unk2(self, unk2_added_idxs, filetype):
        unk2_panel = f'unk2_panel_{filetype.lower()}'
        unk2_list = f'unk2_list_{filetype.lower()}'
        
        self.main[unk2_panel].add_unk2(unk2_added_idxs)
        self.main[unk2_list] = self.main[unk2_panel].I_ctrls
        unk2_vals = [ctrl.GetValue() for ctrl in self.main[unk2_list]]
        build_unk2_list(self.main[unk2_list], unk2_vals)
    
    # MY MODIF
    def delete_unk2(self, unk2_deleted_idxs, filetype):
        unk2_panel = f'unk2_panel_{filetype.lower()}'
        unk2_list = f'unk2_list_{filetype.lower()}'
        
        self.main[unk2_panel].delete_unk2(unk2_deleted_idxs)
        self.main[unk2_list] = self.main[unk2_panel].I_ctrls
        unk2_vals = [ctrl.GetValue() for ctrl in self.main[unk2_list]]
        build_unk2_list(self.main[unk2_list], unk2_vals)


if __name__ == '__main__':
    app = wx.App(False)
    dirname = filename = None
    if len(sys.argv) > 1:
        dirname, filename = os.path.split(sys.argv[1])
    frame = MainWindow(None, f"YaEAN Organizer v{VERSION}", dirname, filename)
    app.MainLoop()
