__author__ = 'Administrator'

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
