# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import threading
import gettext
import wx
import time
import thread

import wx
from wx.lib.filebrowsebutton import FileBrowseButton

import  wx.lib.newevent
import datetime

def TbConfig(name,val):
    # get="Get"+name.split("_")
    splits=name.split("_")
    firstUpper=""
    for split in splits:
        firstUpper += split.capitalize()

    getMethod="def Get"+firstUpper+"(self):"
    getMethodImg="  return session.query(TbConfig).filter_by(name='"+name+"').one().val"
    print getMethod
    print getMethodImg

    setMethod ="def Set"+firstUpper+"(self,val):"
    setMethodImg= "  session.query(TbConfig).filter_by(name='"+name+"').update({TbConfig.val:str(val)})"
    print setMethod
    print setMethodImg


for i in range(1,10):
    time.sleep(0.1)
    print datetime.datetime.now().second,datetime.datetime.now().microsecond/100