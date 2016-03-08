# -*- coding: gbk -*-
__author__ = 'Administrator'

import  wx
import pjsua as pj
import gettext
import  MyWidget
import MyUtil
import  wx.lib.layoutf  as layoutf
from pjsua import UAConfig
from pjsua import MediaConfig

from DB import TbUser
from DB import TbConfig
#---------------------------------------------------------------------------

gettext.install('lang', './locale', unicode=False)
gettext.translation('lang', './locale', languages=['cn']).install(True)

# for python's err report
if (1>3):
    def _(msg):
        pass

lib =None

class MainWindow(wx.Frame):
    acc=None
    call=None

    tbUser=None
    userDao=None
    # tbConfig=None
    configDao=None

    voiceCallBtn=None
    videoCallBtn=None
    callUserText=None

    notebookPanel=None
    taskBar=None

    lastErrorInfo=""

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
        call = evt.GetValue()
        if (self.call):
                call.answer(486)
                return

        call.answer(180)
        call.set_callback(MyUtil.MyCallCallback(self,isIncomingCall=True))

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

        sipConfigMenuItem = optionmenu.Append(101,_("&Sip Config"),"")
        natTravelMenuItem = optionmenu.Append(102,_("&Nat Traversal"),"")

        self.Bind(wx.EVT_MENU, self.doSipConfigMenuItem, sipConfigMenuItem)
        self.Bind(wx.EVT_MENU, self.doNatTravelConfig, natTravelMenuItem)

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
        self.videoCallBtn =btn=wx.Button(topPanel, -1, _('call'))
        self.Bind(wx.EVT_BUTTON, self.onVideoCallBtnClick, btn)
        box.Add(btn, 0,wx.ALIGN_CENTER)
        self.voiceCallBtn = btn = wx.Button(topPanel, -1, _('no video call'))
        self.Bind(wx.EVT_BUTTON, self.onVoiceCallBtnClick, btn)
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

    def __startSipLib(self):
        isSuccess = True
        global lib
        if lib:
            self.__stopSipLib()

        lib =  pj.Lib()

        try:
        # if True:
            dao = self.configDao;
            mediaConfig=MediaConfig()
            mediaConfig.enable_ice = MyUtil.db_str2bool(dao.GetIsUseIce())
            # mediaConfig.enable_turn =MyUtil.db_str2bool(dao.GetIsUseTurn())
            # mediaConfig.turn_server =dao.GetTurnServer()
            uaConfig=UAConfig()
            if (MyUtil.db_str2bool(dao.GetIsUseStun())):
                uaConfig.stun_srv = [str(dao.GetStunServer())]

            lib.init(ua_cfg = uaConfig,log_cfg = pj.LogConfig(level=1, callback=self.log_cb), media_cfg=mediaConfig)
            lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(0))
            lib.start()
        except:
            isSuccess=False
            self.show_err_msg()

        if isSuccess:
            isSuccess=self.reRegister()


        return isSuccess

    def __stopSipLib(self):
        global lib
        if self.call:
            self.call.attach_to_id(-1)
            self.call=None
        if self.acc:
            self.acc.delete()
            self.acc =None
        if lib:
            lib.destroy()
            lib = None

    def __init__(self, parent, title):
        startDlg = MyWidget.StartUpProgressBar()

        ## dao init
        startDlg.update(5,_("initial database"))
        self.userDao = TbUser()
        self.configDao =TbConfig()

        startDlg.update(15,_("initial parent window"))
        wx.Frame.__init__(self, parent, title=title,size=(int(self.configDao.GetWinW()),int(self.configDao.GetWinH())),pos=(int(self.configDao.GetWinX()),int(self.configDao.GetWinY())))

        startDlg.update(35,_("initial UI"))
        self.__setUi()
        ### lib init this may delay several seconds
        startDlg.update(65,_("initial sip lib"))
        self.__startSipLib()

        if (self.userDao.getCount() == 0):
            startDlg.update(100)
            self.doSipConfigMenuItem(None)

        startDlg.update(100)
        startDlg.Destroy()
        self.Raise()
        self.Show(True)
        self._previousSize = self.GetSize()
        self._previousPos = self.GetPosition()

    def onCallUserTextEnter(self,event):
        if (self.callUserText.GetValue()):
            self.onVideoCallBtnClick(None)
        event.Skip()

    def onVideoCallBtnClick(self,e):
        self.__onCallBtnClick(1)
    def onVoiceCallBtnClick(self,e):
        self.__onCallBtnClick(0)
    def __onCallBtnClick(self,vidCnt=1):
        if not self.call and self.acc:
            user = self.callUserText.GetValue().strip()
            uri="sip:"+user+"@"+self.tbUser.domain
            if self.tbUser.name == user:
                self.showMessage(_("can't call myself"))
                return

            try:
                self.call = self.acc.make_call(str(uri),cb=MyUtil.MyCallCallback(self),vid_cnt=vidCnt)
                ### setup notebook's ui
                self.notebookPanel.call_on_state(self.call,0,None)
                self.configDao.SetLastCallNum(user)
                self.configDao.commitSession()
            except :
                self.show_err_msg()

    def doSipConfigMenuItem(self,e):
        dlg = MyWidget.SipConfigDialog(self, -1, _("sip config window"))
        if  self.tbUser:
            dlg.setValue(self.tbUser.domain, self.tbUser.name, self.tbUser.pwd)

        dlg.CenterOnScreen()

        if not self.IsShown():
            dlg.Raise()
        # this does not return until the dialog is closed.
        val = dlg.ShowModal()

        if val == wx.ID_OK:
            if not self.tbUser:
                self.tbUser =TbUser()

            self.tbUser.domain=dlg.domainText.GetValue()
            self.tbUser.name=dlg.userText.GetValue()
            self.tbUser.pwd=dlg.pwdText.GetValue()

            self.userDao.addUser(self.tbUser)

            if self.reRegister():
                self.userDao.commitSession()
            else:
                self.userDao.rollbackSession()

        dlg.Destroy()
        # self.acc.info().media_state
        # win32gui.SetParent(self.call.vid_win_id(),self.Handle)

    def doNatTravelConfig(self,e):
        dlg = MyWidget.NetTraversalConfigDialog(self, -1, _("nat traversal config"))
        dao = self.configDao
        dlg.setValue(dao.GetIsUseIce(),dao.GetIsUseStun(),dao.GetStunServer(),dao.GetIsUseTurn(),dao.GetTurnServer())

        # this does not return until the dialog is closed.
        dlg.CenterOnScreen()
        val = dlg.ShowModal()

        if val == wx.ID_OK:
            dao.SetIsUseIce(MyUtil.db_bool2str(dlg.useIce.GetValue()))
            dao.SetIsUseStun(MyUtil.db_bool2str(dlg.useStun.GetValue()))
            dao.SetIsUseTurn(MyUtil.db_bool2str(dlg.useTurn.GetValue()))
            dao.SetStunServer(dlg.stunServer.GetValue())
            dao.SetTurnServer(dlg.turnServer.GetValue())

            if self.__startSipLib():
                dao.commitSession()
            else:
                dao.rollbackSession()

        dlg.Destroy()

    def reRegister(self):
        return self.__reSetAccount()

    def __reSetAccount(self):
        isSucess=True

        if self.acc:
            self.acc.delete()
            self.acc =None

        if self.userDao.getCount() > 0:
            self.tbUser= self.userDao.getFirstUser()
            account = pj.AccountConfig(str(self.tbUser.domain), str(self.tbUser.name), str(self.tbUser.pwd))
            # account.reg_timeout =30
            try:
                self.acc = lib.create_account(account)
                acc_cb = MyUtil.MyAccountCallback(self.acc,self)
                self.acc.set_callback(acc_cb)
                acc_cb.wait()
                self.SetTitle(_("on registing")+"...")
                self.taskBar.startRegistingBlink()
            except:
                isSucess=False
                self.show_err_msg()
        # else:
        #     self.SetTitle(_("no account"))

        return isSucess

    def __OnCloseWindow(self,event):
        self.__saveWinData()

        self.Show(False)

    def OnCloseWindow(self):
        self.__saveWinData()
        self.__stopSipLib()
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
            self.configDao.commitSession()

    def log_cb(self,level, str2, len):
        if (level==1):
            self.lastErrorInfo += str(str2)
        print str2

    def show_err_msg(self):
        dlg = wx.MessageDialog(self,MyUtil.ProcessErrMsg(self.lastErrorInfo) ,
                               _('Err Message'),
                               wx.OK | wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        self.lastErrorInfo =""
        dlg.ShowModal()
        dlg.Destroy()


app = wx.App()
mainWindow = MainWindow(None, _("no account"))
app.MainLoop()