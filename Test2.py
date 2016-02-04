# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import threading
import gettext
import wx

import wx
from wx.lib.filebrowsebutton import FileBrowseButton

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="wx.Sound",size=(500,100))
        p = wx.Panel(self)

        self.fbb = FileBrowseButton(p,labelText="Select WAV file:",fileMask="*.wav")
        btn = wx.Button(p, -1, "Play")
        self.Bind(wx.EVT_BUTTON, self.OnPlaySound, btn)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.fbb, 1, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(btn, 0, wx.ALIGN_CENTER_VERTICAL)
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add(sizer, 0, wx.EXPAND|wx.ALL, 15)
        p.SetSizer(border)


    def OnPlaySound(self, evt):
        filename = self.fbb.GetValue()
        self.sound = wx.Sound(filename)
        if self.sound.IsOk():
            self.sound.Play(wx.SOUND_SYNC)
        else:
            wx.MessageBox("Invalid sound file", "Error")


app = wx.PySimpleApp()
frm = MyFrame()
frm.Show()
app.MainLoop()