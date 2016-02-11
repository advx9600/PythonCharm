__author__ = 'Administrator'
import  wx
import pjsua as pj
import threading
import datetime

# for python's err report
if (1>3):
    def _(msg):
        pass

def ProcessErrMsg(msg):
    msgAdd=""
    if (msg):
        if "[status=420006]" in str(msg):
            msgAdd=_("please insert mic and reboot this application")+"\n"
        elif "[status=171039]" in str(msg):
            msgAdd=_("sip account config failed,please delete db_1.db and reboot application")+"\n"

    msgAdd += str(msg)
    return  msgAdd


myRegStateEvent = wx.NewEventType()
EVT_ON_REG_STATE = wx.PyEventBinder(myRegStateEvent, 1)
class OnRegStateEvent(wx.PyCommandEvent):
    """Event to signal that a count value is ready"""
    def __init__(self, etype, eid, value=None):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        return self._value

myInComingCallEvent =wx.NewEventType()
EVT_ON_INCOMING_CALL =  wx.PyEventBinder(myInComingCallEvent, 1)
class InComingCallEvent(wx.PyCommandEvent):
    """Event to signal that a count value is ready"""
    def __init__(self, etype, eid, value=None):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        return self._value

class MyAccountCallback(pj.AccountCallback):
        sem = None
        win = None

        def __init__(self, account,win):
            pj.AccountCallback.__init__(self, account)
            self.win =win

        def wait(self):
            # only one thread can be registed
            self.sem = threading.Semaphore(1)
            self.sem.acquire()

        def on_reg_state(self):
            if self.sem:
                if self.account.info().reg_status >= 200:
                    self.sem.release()
                    self.sem=None

            evt = OnRegStateEvent(myRegStateEvent,-1,self.account.info().reg_status)
            wx.PostEvent(self.win, evt)

        def on_incoming_call(self, call):
            evt = InComingCallEvent(myInComingCallEvent,-1,call)
            wx.PostEvent(self.win, evt)

myOnStateEvent =wx.NewEventType()
EVT_ON_STATE =  wx.PyEventBinder(myOnStateEvent, 1)
class OnStateCallEvent(wx.PyCommandEvent):
    """Event to signal that a count value is ready"""
    def __init__(self, etype, eid, value=None):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        return self._value

myOnMediaStateEvent =wx.NewEventType()
EVT_ON_MEDIA_STATE =  wx.PyEventBinder(myOnMediaStateEvent, 1)
class OnMediaStateCallEvent(wx.PyCommandEvent):
    """Event to signal that a count value is ready"""
    def __init__(self, etype, eid, value=None):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        return self._value

class MyCallCallback(pj.CallCallback):
    win=None
    isVideo=False
    def __init__(self, win,call=None):
        pj.CallCallback.__init__(self, call)
        self.win = win
    # Notification when call state has changed
    def on_state(self):
        # print datetime.datetime.now(),
        print "Call with", self.call.info().remote_uri,
        print "is", self.call.info().state_text,
        print "last code =", self.call.info().last_code,
        print "(" + self.call.info().last_reason + ")"

        # code = int(self.call.info().last_code)
        # state = self.call.info().state_text

        ### because this event is very slow,so do it directly
        # if (code == 200 and state=="DISCONNCTD" and self.isVideo):
        #     self.win.real_on_state(code,state)
        # else:
        evt = OnStateCallEvent(myOnStateEvent,-1,self.call.info())
        wx.PostEvent(self.win, evt)

    # Notification when call's media state has changed.
    def on_media_state(self):
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            # Connect the call to sound device
            call_slot = self.call.info().conf_slot
            pj.Lib.instance().conf_connect(call_slot, 0)
            pj.Lib.instance().conf_connect(0, call_slot)

        if (self.call.vid_win_id()):
            self.isVideo=True
        else:
            self.isVideo=False

        evt = OnMediaStateCallEvent(myOnMediaStateEvent,-1,self.call.info())
        wx.PostEvent(self.win, evt)