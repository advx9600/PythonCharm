# -*- coding: gbk -*-
__author__ = 'Administrator'

import sys
import  wx
import pjsua as pj
import threading
import thread
import time
import win32gui
import gettext
import  MyWidget
import MyUtil
import  wx.lib.layoutf  as layoutf
import DB
import datetime

from DB import TbUser
from DB import TbConfig
#---------------------------------------------------------------------------

gettext.install('lang', './locale', unicode=False)
gettext.translation('lang', './locale', languages=['cn']).install(True)

# for python's err report
if (1>3):
    def _(msg):
        pass

lib = pj.Lib()

class MainWindow(wx.Frame):
    acc=None
    call=None

    tbUser=None
    userDao=None
    # tbConfig=None
    configDao=None

    callBtn=None
    callUserText=None

    notebookPanel=None
    taskBar=None

    lastErrorInfo=None

    _previousSize=None
    _previousPos=None

    def on_reg_state(self,evt):
        reg_status= evt.GetValue()

        if reg_status == 200:
            self.SetTitle(_("register OK"))
            self.taskBar.setRegisted(True)
        else:
            self.SetTitle(_("register failed")+":"+str(reg_status))
            self.taskBar.setRegisted(False)

    def on_incoming_call(self,evt):
        if (self.call):
                self.call.answer(486)
                return

        call = evt.GetValue()
        call.answer(180)  ### this must add before set_callback
        call.set_callback(MyUtil.MyCallCallback(self))

        self.call=call
        self.taskBar.on_incoming_call(True)
        self.notebookPanel.on_incoming_call(call)

    def on_state(self,evt):
        info = evt.GetValue()
        code = int(info.last_code)
        state = info.state_text
        self.real_on_state(code,state)

    def real_on_state(self,code,state):
        if not self.call:
            return
        ### http://www.51testing.com/html/90/360490-834635.html
        ### 404 not found,408 Request Timeout,480 temporary unavailable,486 Busy,487 500 Internal Server Err,timeout,603 decline
        if code in (404,408,480,486,487,500,603) or (code==200 and state=="DISCONNCTD"):
            # mainWindow.call.set_callback(None)
            self.call.attach_to_id(-1)
            self.call = None
        ### notebookPanel UI set
        self.notebookPanel.call_on_state(self.call,code,state)
        self.taskBar.on_incoming_call(False)

    def on_media_state(self,evt):
        info = evt.GetValue()
        if  info.media_state == pj.MediaState.ACTIVE and self.call.vid_win_id():
            self.notebookPanel.on_media_sate(self.call.vid_win_id())

    def showMessage(self,msg,title=""):
        wx.MessageBox(msg,title)

    def __setUi(self):
        self.Bind(wx.EVT_CLOSE, self.__OnCloseWindow)
        
        self.Bind( MyUtil.EVT_ON_INCOMING_CALL,self.on_incoming_call)
        self.Bind(MyUtil.EVT_ON_REG_STATE,self.on_reg_state)
        self.Bind(MyUtil.EVT_ON_STATE,self.on_state)
        self.Bind(MyUtil.EVT_ON_MEDIA_STATE,self.on_media_state)
          # option menu
        optionmenu= wx.Menu()

        sipConfigMenuItem = optionmenu.Append(0,_("&Sip Config"),"")
        self.Bind(wx.EVT_MENU, self.doSipConfigMenuItem, sipConfigMenuItem)

        menuBar = wx.MenuBar()
        menuBar.Append(optionmenu,(_("&Option")))
        self.SetMenuBar(menuBar)

        panel = wx.Panel(self,-1)
        panel.SetAutoLayout(True)

        #### topPanel layout
        topPanel = wx.Window(panel,-1,style=wx.NO_BORDER)
        topPanel.SetConstraints(layoutf.Layoutf('t=t10#1;l=l10#1;b=b10#1;r=r10#1;h!40',(panel,)))

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add( wx.StaticText(topPanel, -1, _("sip")+":"), 0, wx.ALIGN_CENTER)
        self.callUserText=text=wx.TextCtrl(topPanel, -1, self.configDao.GetLastCallNum(),style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER, self.onCallUserTextEnter, text)
        box.Add(text, 1, wx.ALIGN_CENTER)
        self.callBtn =btn=wx.Button(topPanel, -1, _('call'))
        self.Bind(wx.EVT_BUTTON, self.onCallBtnClick, btn)
        box.Add(btn, 0,wx.ALIGN_CENTER)

        topPanel.SetSizer(box)

        ### center panel layout
        centerPanel = wx.Window(panel,-1,style=wx.NO_BORDER)
        # centerPanel.SetBackgroundColour(wx.RED)
        centerPanel.SetConstraints(layoutf.Layoutf('t=t45#2;l=l10#1;b=b10#1;r=r10#1',(panel,topPanel)))
        self.notebookPanel=notebook=MyWidget.MainNoteBookPanel(centerPanel,-1,self)
        notebook.SetConstraints(layoutf.Layoutf('t=t0#1;l=l0#1;b=b0#1;r=r0#1',(centerPanel,)))

        ### debug
        # notebook.on_incoming_call(None)

        ### system tray
        self.taskBar=MyWidget.TaskBarIcon(self)

    def __init__(self, parent, title):
        ## dao init
        self.userDao = TbUser()
        self.configDao =TbConfig()

        wx.Frame.__init__(self, parent, title=title,size=(int(self.configDao.GetWinW()),int(self.configDao.GetWinH())),pos=(int(self.configDao.GetWinX()),int(self.configDao.GetWinY())))
        self.__setUi()

        ### lib init
        lib.init(log_cfg = pj.LogConfig(level=1, callback=self.log_cb))
        lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(0))
        lib.start()

        if (self.userDao.getCount() == 0):
            # self.userDao.addUser(TbUser(name="101", pwd="101", domain="192.168.0.175"))
            self.doSipConfigMenuItem(None)
        else:
            self.__reSetAccount()

        self.Show(True)
        self._previousSize = self.GetSize()
        self._previousPos = self.GetPosition()

    def onCallUserTextEnter(self,event):
        if (self.callUserText.GetValue()):
            self.onCallBtnClick(event)
        event.Skip()

    def onCallBtnClick(self,e):
        if not self.call:
            user = self.callUserText.GetValue().strip()
            uri="sip:"+user+"@"+self.tbUser.domain
            if self.tbUser.name == user:
                self.showMessage(_("can't call myself"))
                return

            try:
                self.call = self.acc.make_call(str(uri),cb=MyUtil.MyCallCallback(self))
                ### setup notebook's ui
                self.notebookPanel.call_on_state(self.call,0,None)
                self.configDao.SetLastCallNum(user)
                self.configDao.sessionCommit()
            except :
                self.show_err_msg()

    def reRegister(self):
        self.__reSetAccount()

    def __reSetAccount(self):
        if self.acc:
            self.acc.delete()
            self.acc =None

        self.tbUser= self.userDao.getFirstUser()
        account = pj.AccountConfig(str(self.tbUser.domain), str(self.tbUser.name), str(self.tbUser.pwd))
        # account.reg_timeout =30
        try:
            self.acc = lib.create_account(account)
        except:
            self.show_err_msg()

        acc_cb = MyUtil.MyAccountCallback(self.acc,self)
        self.acc.set_callback(acc_cb)
        acc_cb.wait()
        self.SetTitle(_("on registing")+"...")

    def doSipConfigMenuItem(self,e):
        dlg = MyWidget.SipConfigDialog(self, -1, _("sip config window"))
        if  self.tbUser:
            dlg.setValue(self.tbUser.domain, self.tbUser.name, self.tbUser.pwd)

        dlg.CenterOnScreen()

        # this does not return until the dialog is closed.
        val = dlg.ShowModal()

        if val == wx.ID_OK:
            if not self.tbUser:
                self.tbUser =TbUser()

            self.tbUser.domain=dlg.domainText.GetValue()
            self.tbUser.name=dlg.userText.GetValue()
            self.tbUser.pwd=dlg.pwdText.GetValue()

            self.userDao.addUser(self.tbUser)

            self.__reSetAccount()

        dlg.Destroy()
        # self.acc.info().media_state
        # win32gui.SetParent(self.call.vid_win_id(),self.Handle)

    def __OnCloseWindow(self,event):
        self.__saveWinData()

        self.Show(False)

    def OnCloseWindow(self):
        self.__saveWinData()

        if self.call:
            self.call.attach_to_id(-1)
            self.acc.delete()
        lib.destroy()
        self.Destroy()

    def __saveWinData(self):
        isNeedUpdate=None

        if (self._previousSize != self.GetSize()):
            w,h=self._previousSize = self.GetSize()
            self.configDao.SetWinW(w)
            self.configDao.SetWinH(h)
            isNeedUpdate = True

        if (self._previousPos != self.GetPosition()):
            x,y=self._previousPos = self.GetPosition();
            self.configDao.SetWinX(x)
            self.configDao.SetWinY(y)
            isNeedUpdate = True

        if (isNeedUpdate):
            self.configDao.sessionCommit()

        pass

    def log_cb(self,level, str, len):
        if (level==1):
            self.lastErrorInfo = str
        print str,

    def show_err_msg(self):
        dlg = wx.MessageDialog(self,MyUtil.ProcessErrMsg(self.lastErrorInfo) ,
                               _('Err Message'),
                               wx.OK | wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()


app = wx.App()
mainWindow = MainWindow(None, _("no account"))
app.MainLoop()