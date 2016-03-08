import distutils
import py2exe
import sqlalchemy
import glob

from distutils.core import setup

#setup(console=['VideoForm.py'])

setup(
    windows=[
        {
            "script" : "VideoForm.py",
            "icon_resources" : [(0,"logo.ico")]
        }
    ],
    # console = ["VideoForm.py"],
    data_files=[
                    ("img",glob.glob("img\\*.png")),
                    ("sound",glob.glob("sound\\*.wav")),
                    ("locale/cn/LC_MESSAGES",glob.glob("locale/cn/LC_MESSAGES/*.mo")),
                    ("locale/en/LC_MESSAGES",glob.glob("locale/en/LC_MESSAGES/*.mo")),
                ]
)