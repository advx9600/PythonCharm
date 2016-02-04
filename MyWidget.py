__author__ = 'Administrator'
import  wx
import wx.lib.sized_controls as sc
import wx.aui
import time
import win32gui
import win32con
import  wx.lib.layoutf  as layoutf

# for python's err report
if (1>3):
    def _(msg):
        print ""


class TaskBarIcon(wx.TaskBarIcon):
    __registed_icon = 'img/registed_phone.png'
    __unregisted_icon = 'img/unregisted_phone.png'

    #### this is the VideoForm.py's MainWindow
    __mainWin=None
    def __init__(self,win):
        super(TaskBarIcon, self).__init__()
        self.set_icon(self.__unregisted_icon)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.__mainWin = win

    def create_menu_item(self,menu, label, func):
        item = wx.MenuItem(menu, -1, label)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.AppendItem(item)
        return item

    def CreatePopupMenu(self):
        menu = wx.Menu()
        self.create_menu_item(menu, 'Say Hello', self.on_hello)
        menu.AppendSeparator()
        self.create_menu_item(menu, _('Exit'), self.on_exit)
        return menu

    def setRegisted(self,isTrue):
        if isTrue:
            self.set_icon(self.__registed_icon)
        else:
            self.set_icon(self.__unregisted_icon)

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon,_("VideoForm.py"))

    def on_left_down(self, event):
        self.__mainWin.Iconize(False)
        self.__mainWin.Raise()
        self.__mainWin.Show(True)

    def on_hello(self, event):
        print 'Hello, world!'

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        self.__mainWin.OnCloseWindow()

class ColoredPanel(wx.Window):
    def __init__(self, parent, color):
        wx.Window.__init__(self, parent, -1, style = wx.SIMPLE_BORDER)
        self.SetBackgroundColour(color)
        if wx.Platform == '__WXGTK__':
            self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)


class MainNoteBookPanel(wx.Notebook):
    __callWin=None
    __soundPlayer=None
    __call=None

    hangUpBtn=None
    answerBtn=None
    videoPanel=None
    videoWinId=None
    def __init__(self, parent, id):
        wx.Notebook.__init__(self, parent, id, size=(51,151), style=
                             wx.BK_DEFAULT
                             # wx.BK_TOP  |
                             # wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                             # | wx.NB_MULTILINE
                             )
        # self.log = log
        win = self.makeColorPanel(wx.WHITE)
        self.AddPage(win, _("MainWindow"))
        st = wx.StaticText(win.win, -1,
                          "Main",
                          (10, 10))
        st.SetForegroundColour(wx.BLACK)

    def hangup(self,e):
        self.hangUpBtn.Enable(False)
        self.__call.hangup()

    def answer(self,e):
        self.answerBtn.Enable(False)
        self.__call.answer()

    def __setCallWin(self,win):
        win.SetBackgroundColour(wx.GREEN)
        box = wx.BoxSizer(wx.HORIZONTAL)

        self.videoPanel=videoPanel = wx.Panel(win)
        videoPanel.SetBackgroundColour(wx.BLACK)
        #
        box.Add(videoPanel,1,wx.EXPAND)
        #
        #
        #
        self.hangUpBtn=btn = wx.Button(win,-1,_("hang up"))
        self.Bind(wx.EVT_BUTTON, self.hangup, btn)
        box.Add(btn,0,wx.ALIGN_LEFT)
        #
        win.SetSizer(box)

    def call_on_state(self,call,code,state):
        self.__call =call
        if (code == 0 and not self.__callWin):
            # self.__callWin=win = self.makeColorPanel(wx.WHITE)
            self.__callWin =win= wx.Panel(self)
            self.__setCallWin(win)
            self.AddPage(win, _("Calling"))
            self.SetSelection(1)

        # if not self.__callWin:
        #     return
        ### http://www.51testing.com/html/90/360490-834635.html
        #### other code process
        elif code in (404,408,480,486,603) or (code==200 and state=="DISCONNCTD"):
            if (code == 404):
                self.SetPageText(1,_("not found user"))
            elif code == 408:
                self.SetPageText(1,_("Request Timeout"))
            elif code == 480:
                self.SetPageText(1,_("Temporily Unavailable"))
            elif code == 486:
                self.SetPageText(1,_("Busy here"))
            elif code == 603:
                self.SetPageText(1,_("Give up call"))
            elif code == 200:
                self.SetPageText(1,_("disconnected"))

            self.__soundPlayer.Stop()
            self.__callWin.Enable(False)
            time.sleep(3)
            self.DeletePage(1)
            self.__callWin=None
        elif code == 180:
            self.SetPageText(1,_("wait for answer"))
            self.__soundPlayer = wx.Sound("sound/ringback2.wav")
            self.__soundPlayer.Play(wx.SOUND_ASYNC | wx.SOUND_LOOP)
        elif code == 200 and state== "CONFIRMED":
            self.SetPageText(1,_("connected")+" #1")
            self.__soundPlayer.Stop()

    def on_media_sate(self,vid):
        if vid:
            self.videoWinId =vid
            win32gui.SetParent(vid,self.videoPanel.Handle)
            x,y = self.videoPanel.GetPosition()
            w,h = self.videoPanel.GetSize()
            win32gui.SetWindowPos(vid,win32con.HWND_TOP,x,y,w,h,win32con.SWP_NOACTIVATE)
            self.videoPanel.Bind(wx.EVT_SIZE,self.reSizeVidePanel,self.videoPanel)

    def reSizeVidePanel(self,e):
        if self.videoWinId:
            x,y = self.videoPanel.GetPosition()
            w,h = self.videoPanel.GetSize()
            win32gui.SetWindowPos(self.videoWinId,win32con.HWND_TOP,x,y,w,h,win32con.SWP_NOACTIVATE)

    def __setComingCallWin(self,win):
        win.SetBackgroundColour(wx.GREEN)
        box = wx.BoxSizer(wx.HORIZONTAL)

        self.videoPanel=videoPanel = wx.Panel(win)
        videoPanel.SetBackgroundColour(wx.BLACK)
        box.Add(videoPanel,1,wx.EXPAND)

        self.hangUpBtn=btn = wx.Button(win,-1,_("hang up"))
        self.Bind(wx.EVT_BUTTON, self.hangup, btn)
        box.Add(btn,0,wx.ALIGN_LEFT)

        self.answerBtn = btn= wx.Button(win,-1,_("answer"))
        self.Bind(wx.EVT_BUTTON, self.answer, btn)
        box.Add(btn,0,wx.ALIGN_LEFT)

        win.SetSizer(box)
        pass

    def  on_incoming_call(self,call):
        if  not self.__callWin:
            self.__callWin=win= wx.Panel(self)
            # self.__setComingCallWin(win)
            self.AddPage(win, _("Calling"))
            self.SetSelection(1)


        # if (code == )
        # st.SetBackgroundColour(wx.BLUE)

        # # Show how to put an image on one of the notebook tabs,
        # # first make the image list:
        # il = wx.ImageList(16, 16)
        # idx1 = il.Add(images.Smiles.GetBitmap())
        # self.AssignImageList(il)
        #
        # # now put an image on the first tab we just created:
        # self.SetPageImage(0, idx1)
        #
        #
        # win = self.makeColorPanel(wx.RED)
        # self.AddPage(win, "Red")
        # self.SetSelection(1)
        #
        # win = ScrolledWindow.MyCanvas(self)
        # self.AddPage(win, 'ScrolledWindow')
        #
        # win = self.makeColorPanel(wx.GREEN)
        # self.AddPage(win, "Green")
        #
        # win = GridSimple.SimpleGrid(self, log)
        # self.AddPage(win, "Grid")
        #
        # win = ListCtrl.TestListCtrlPanel(self, log)
        # self.AddPage(win, 'List')
        #
        # win = self.makeColorPanel(wx.CYAN)
        # self.AddPage(win, "Cyan")
        #
        # win = self.makeColorPanel(wx.NamedColour('Midnight Blue'))
        # self.AddPage(win, "Midnight Blue")
        #
        # win = self.makeColorPanel(wx.NamedColour('Indian Red'))
        # self.AddPage(win, "Indian Red")

    #     self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
    #     self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
    #
    #
    def makeColorPanel(self, color):
        p = wx.Panel(self, -1)
        win = ColoredPanel(p, color)
        p.win = win
        def OnCPSize(evt, win=win):
            win.SetPosition((0,0))
            win.SetSize(evt.GetSize())
        p.Bind(wx.EVT_SIZE, OnCPSize)
        return p

    #
    #     def OnCPSize(evt, win=win):
    #         win.SetPosition((0,0))
    #         win.SetSize(evt.GetSize())
    #         p.Bind(wx.EVT_SIZE, OnCPSize)
    #         return p


    # def OnPageChanged(self, event):
    #     old = event.GetOldSelection()
    #     new = event.GetSelection()
    #     sel = self.GetSelection()
    #     self.log.write('OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel))
    #     event.Skip()
    #
    # def OnPageChanging(self, event):
    #     old = event.GetOldSelection()
    #     new = event.GetSelection()
    #     sel = self.GetSelection()
    #     self.log.write('OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel))
    #     event.Skip()

class SipConfigDialog(sc.SizedDialog):
    userText=None
    pwdText = None
    domainText = None

    def __init__(self, parent, id,title):
        sc.SizedDialog.__init__(self, None, -1, title,
                        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        pane = self.GetContentsPane()
        pane.SetSizerType("form")

        # row 1
        wx.StaticText(pane, -1,  _("username"))
        self.userText=text = wx.TextCtrl(pane, -1, "")
        text.SetSizerProps(expand=True)

        # row 2
        wx.StaticText(pane, -1,  _("password"))
        self.pwdText=text = wx.TextCtrl(pane, -1, "", size=(200,-1))
        text.SetSizerProps(expand=True)

        # row 3
        wx.StaticText(pane, -1,  _("domain"))
        self.domainText=text = wx.TextCtrl(pane, -1, "")
        text.SetSizerProps(expand=True)

        # add dialog buttons
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))

        # a little trick to make sure that you can't resize the dialog to
        # less screen space than the controls need
        self.Fit()
        self.SetMinSize(self.GetSize())

    def setValue(self,domain,username,pwd):
        self.userText.SetValue(username)
        self.pwdText.SetValue(pwd)
        self.domainText.SetValue(domain)

class SipConfigDialogOld(wx.Dialog):
    userText=None
    pwdText = None
    domainText = None
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition,
            style=wx.DEFAULT_DIALOG_STYLE,
            ):

        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate(pre)

        # Now continue with the normal construction of the dialog
        # contents
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, -1, _("Sip Config"))
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, _("username")+":")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.userText=text = wx.TextCtrl(self, -1, "", size=(200,-1))
        box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, _("password")+":")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.pwdText=text = wx.TextCtrl(self, -1, "", size=(20,-1))
        box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, _("domain")+":")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALIGN_RIGHT | wx.ALL, 5)

        self.domainText=text = wx.TextCtrl(self, -1, "", size=(10,-1))
        box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL| wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()

        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL| wx.ALIGN_CENTER_HORIZONTAL| wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def setValue(self,domain,username,pwd):
        self.userText.SetValue(username)
        self.pwdText.SetValue(pwd)
        self.domainText.SetValue(domain)
