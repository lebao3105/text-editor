import gettext
import locale
import os.path
import packaging.version
import pathlib
import sys
from tkinter.messagebox import showerror

import texteditor
from . import mainwindow
from .backend import __version__ as version

currdir = pathlib.Path(__file__).parent
__version__ = version

if packaging.version.parse(version).is_prerelease:
    texteditor.icon = currdir / "icons/texteditor.Devel.png"
else:
    texteditor.icon = currdir / "icons/texteditor.png"

try:
    from texteditor.defs import LOCALE_DIR
except ImportError:
    LOCALE_DIR = currdir / "po"
# LOCALE_DIR = "build/po/"

locale.setlocale(locale.LC_ALL, None)
gettext.bindtextdomain("me.lebao3105.texteditor", LOCALE_DIR)
gettext.textdomain("me.lebao3105.texteditor")
gettext.install("me.lebao3105.texteditor")
texteditor._ = gettext.gettext


def start_app(argv=None):
    if not argv:  # For __main__
        argv = sys.argv
    root = mainwindow.MainWindow()
    n = len(argv)
    if n - 1 > 0:
        if os.path.isfile(argv[1]):
            root.text_editor.fileops.openfile(argv[1])
        else:
            showerror(message=root._("File not found : %s") % str(argv[1]))
        for i in range(2, n):
            if os.path.isfile(argv[i]):
                root.add_tab()
                root.text_editor.fileops.openfile(root, argv[i])
            else:
                showerror(message=root._("File not found : %s") % str(argv[i]))
    else:
        pass

    root.mainloop()


if __name__ == "__main__":
    start_app(sys.argv)
