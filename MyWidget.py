__author__ = 'Administrator'
import  wx
import  wx.lib.newevent
import wx.lib.sized_controls as sc
import wx.aui
import time
import win32gui
import win32con
import thread
import datetime
import  wx.lib.layoutf  as layoutf

# for python's err report
if (1>3):
    def _(msg):
        print ""

class TaskBarIcon(wx.TaskBarIcon):
    _registed_icon = 'img/registed_phone.png'
    _unregisted_icon = 'img/unregisted_phone.png'

    #### this is the VideoForm.py's MainWindow
    _mainWin=None

    _isOnComingCallBlink=None

    _isRegisted=False
    _isRegisting =False
    _isRegistingThreadOn=False

    def __init__(self,win):
        super(TaskBarIcon, self).__init__()
        self.set_icon(self._unregisted_icon)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self._mainWin = win

    def create_menu_item(self,menu, label, func):
        item = wx.MenuItem(menu, -1, label)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.AppendItem(item)
        return item

    def CreatePopupMenu(self):
        menu = wx.Menu()
        if not self._isRegisted:
            self.create_menu_item(menu, _('Register'), self.on_register)
            menu.AppendSeparator()
        self.create_menu_item(menu, _('Exit'), self.on_exit)
        return menu

    def setRegisted(self,isTrue):
        self._isRegisting = False
        self._isRegisted=isTrue
        if isTrue:
            self.set_icon(self._registed_icon)
        else:
            self.set_icon(self._unregisted_icon)

    # def __codeCheckThread(self):
        #     time.sleep(5)
        #     ### notebookPanel UI set
        #     self.call.set_callback(None)
        #     self.on_state2()
        # #
        # def __codeCheck(self,code):
        #     if (code == 0):
        #         thread.start_new_thread(self.__codeCheckThread,())

    def __on_incoming_call_thread(self):
        while(self._isOnComingCallBlink):
            time.sleep(0.5)
            self.set_icon(self._unregisted_icon)
            time.sleep(0.5)
            self.set_icon(self._registed_icon)
        self.set_icon(self._registed_icon)

    def on_incoming_call(self,isOn):
        self._isOnComingCallBlink = isOn
        if isOn:
            thread.start_new_thread(self.__on_incoming_call_thread,())

    def set_icon(self, path,name=None):
        if not name:
            name = _("VideoForm.py")
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon,name)

    def on_left_down(self, event):
        self._isOnComingCallBlink = False
        self._mainWin.Iconize(False)
        self._mainWin.Raise()
        self._mainWin.Show(True)

    def __on_registing_thread(self):
        if  self._isRegistingThreadOn:
            return

        self._isRegistingThreadOn = True
        while self._isRegisting:
            for i in range(0,5):
                time.sleep(0.3)
                if self._isRegisting:
                    val = _("on registing")
                    self.set_icon("img/registing_"+str(i)+".png", _("on registing"))

        self._isRegistingThreadOn = False

    def on_register(self,event):
        # self.SetIcon("",_("on registing"))
        self._mainWin.reRegister()
        self._isRegisting = True
        thread.start_new_thread(self.__on_registing_thread,())

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        self._mainWin.OnCloseWindow()

class ColoredPanel(wx.Window):
    def __init__(self, parent, color):
        wx.Window.__init__(self, parent, -1, style = wx.SIMPLE_BORDER)
        self.SetBackgroundColour(color)
        if wx.Platform == '__WXGTK__':
            self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

class MainNoteBookPanel(wx.Notebook):
    _callWin=None
    _soundPlayer=None
    _call=None
    _videoWinId=None

    hangUpBtn=None
    answerBtn=None
    videoPanel=None

    ### mainWindow
    _mainWindow=None
    def __init__(self, parent, id,mainWin):
        wx.Notebook.__init__(self, parent, id, size=(51,151), style=
                             wx.BK_DEFAULT
                             # wx.BK_TOP  |
                             # wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                             # | wx.NB_MULTILINE
                             )
        self._mainWindow = mainWin
        # self.log = log
        win = self.makeColorPanel(wx.WHITE)
        self.AddPage(win, _("MainWindow"))
        st = wx.StaticText(win.win, -1,
                          "Main",
                          (10, 10))
        st.SetForegroundColour(wx.BLACK)

    def hangup(self,e):
        try:
            self._call.hangup()
        except:
            self._mainWindow.show_err_msg()
        self.hangUpBtn.Enable(False)
        self._mainWindow.real_on_state(603,"immediately")

    def answer(self,e):
        self.answerBtn.Enable(False)
        self._call.answer()

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
        self._call =call
        if (code == 0 and not self._callWin):
            # self._callWin=win = self.makeColorPanel(wx.WHITE)
            self._callWin =win= wx.Panel(self)
            self.__setCallWin(win)
            self.AddPage(win, _("Calling"))
            self.SetSelection(1)

        # if not self._callWin:
        #     return
        ### http://www.51testing.com/html/90/360490-834635.html
        #### other code process
        elif code in (404,408,480,486,487,500,603) or (code==200 and state=="DISCONNCTD"):
            text=""
            if (code == 404):
                text=_("not found user")
            elif code == 408:
                text=_("Request Timeout")
            elif code == 480:
                text=_("Temporily Unavailable")
            elif code == 486:
                text=_("Busy here")
            elif code == 487:
                text=_("Request terminated")
            elif code == 500:
                text=_("Internal Server Error")
            elif code == 603:
                text=_("Give up call")
            elif code == 200:
                text=_("disconnected")
            else:
                text=str(code)

            self.SetPageText(1,text)
            if self._soundPlayer:
                self._soundPlayer.Stop()
                self._soundPlayer = None
            self._callWin.Enable(False)
            if state == "immediately" or (code ==200 and state=="DISCONNCTD"):
                self.__delayCloseWin(0)
            else:
                thread.start_new_thread(self.__delayCloseWin,(3,))

        elif code == 180:
            self.SetPageText(1,_("wait for answer"))
            self._soundPlayer = wx.Sound("sound/ringback2.wav")
            self._soundPlayer.Play(wx.SOUND_ASYNC | wx.SOUND_LOOP)
        elif code == 200 and state== "CONFIRMED":
            self.SetPageText(1,_("connected")+" #1")
            if self._soundPlayer:
                self._soundPlayer.Stop()
                self._soundPlayer = None
    #### call by  thread
    def __delayCloseWin(self,sleep=0):
        if (sleep >0):
            time.sleep(sleep)
        self.DeletePage(1)
        self._callWin=None
        self._videoWinId = None

    def on_media_sate(self,vid):
        if vid:
            self._videoWinId =vid
            win32gui.SetParent(vid,self.videoPanel.Handle)
            x,y = self.videoPanel.GetPosition()
            w,h = self.videoPanel.GetSize()
            win32gui.SetWindowPos(vid,win32con.HWND_TOP,x,y,w,h,win32con.SWP_NOACTIVATE)
            self.videoPanel.Bind(wx.EVT_SIZE,self.reSizeVidePanel,self.videoPanel)

    def reSizeVidePanel(self,e):
        if self._videoWinId:
            x,y = self.videoPanel.GetPosition()
            w,h = self.videoPanel.GetSize()
            win32gui.SetWindowPos(self._videoWinId,win32con.HWND_TOP,x,y,w,h,win32con.SWP_NOACTIVATE)

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

    def on_incoming_call(self,call):
        self._call = call
        self._soundPlayer = wx.Sound("sound/oldphone-mono.wav")
        self._soundPlayer.Play(wx.SOUND_ASYNC | wx.SOUND_LOOP)

        self._callWin=win= wx.Panel(self)
        self.__setComingCallWin(win)
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
    stunText = None

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

        # row 4
        wx.StaticText(pane, -1,  _("stun server"))
        self.stunText=text = wx.TextCtrl(pane, -1, "")
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
