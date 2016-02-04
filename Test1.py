__author__ = 'Administrator'
import sys
import pjsua as pj
import threading


def log_cb(level, str, len):
    print str,

class MyAccountCallback(pj.AccountCallback):
    sem = None

    def __init__(self, account):
        pj.AccountCallback.__init__(self, account)

    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()

    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()


lib = pj.Lib()

class MyCallCallback(pj.CallCallback):

    def __init__(self, call=None):
        pj.CallCallback.__init__(self, call)

    # Notification when call state has changed
    def on_state(self):
        global current_call
        print "Call with", self.call.info().remote_uri,
        print "is", self.call.info().state_text,
        print "last code =", self.call.info().last_code,
        print "(" + self.call.info().last_reason + ")"

        if self.call.info().state == pj.CallState.DISCONNECTED:
            current_call = None
            print 'Current call is', current_call

    # Notification when call's media state has changed.
    def on_media_state(self):
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            # Connect the call to sound device
            call_slot = self.call.info().conf_slot
            pj.Lib.instance().conf_connect(call_slot, 0)
            pj.Lib.instance().conf_connect(0, call_slot)
            print "Media is now active"

        else:
            print "Media is inactive"

try:
    lib.init(log_cfg = pj.LogConfig(level=4, callback=log_cb))
    lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(0))
    lib.start()

    account = pj.AccountConfig("192.168.0.174", "101", "101");

    acc = lib.create_account(account)

    acc_cb = MyAccountCallback(acc)
    acc.set_callback(acc_cb)
    acc_cb.wait()

    print "\n"
    print "Registration complete, status=", acc.info().reg_status, \
          "(" + acc.info().reg_reason + ")"
    print "\nPress ENTER to quit"

    sys.stdin.readline()
    print "start call"
    acc.make_call("sip:102@192.168.0.174", cb=MyCallCallback())

    sys.stdin.readline()

    lib.destroy()
    lib = None

except pj.Error, e:
    print "Exception: " + str(e)
    lib.destroy()

