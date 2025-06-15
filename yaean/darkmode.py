# MY MODIF

import wx
from pyxenoverse.gui.ctrl.single_selection_box import SingleSelectionBox

def getWidgets(parent, all_items=[]):
    # if isinstance(parent, wx.StaticText):
    #     # print('Static Text', parent.GetLabel())
    #     pass
    # elif isinstance(parent, wx.TextCtrl):
    #     # print('TextCtrl', parent.GetValue())
    #     pass
    # elif isinstance(parent, wx.StatusBar):
    #     print("STATUS BAR", parent)
    #     return []
    # elif isinstance(parent, wx.TreeCtrl):
    #     print("TREE CTRL", parent)
    # elif isinstance(parent, wx.StaticBoxSizer):
    #     print('STATIC BOX', parent)
    #     return []
    # elif isinstance(parent, SingleSelectionBox):
    #     print('CHECK BOX', parent)
    #     return []

    cur_items = [parent]
    for item in parent.GetChildren():
        cur_items.append(item)
        
        if hasattr(item, 'GetChildren'):
            for child in item.GetChildren():
                cur_items.extend(getWidgets(child))
                # cur_items.append(child)
        
    return cur_items + all_items

def darkMode(mainWidget, normalColor):
    widgets = getWidgets(mainWidget)
    panel = widgets[0]

    dark_mode = normalColor == panel.GetBackgroundColour()
    
    for w in widgets:
        if dark_mode:
            w.SetBackgroundColour("Dark Grey")
            w.SetForegroundColour("White")
        else:
            w.SetBackgroundColour("White")
            w.SetForegroundColour("Black")
    
    mainWidget.Refresh()

    return dark_mode