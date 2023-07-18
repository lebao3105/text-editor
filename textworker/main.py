import os
import sys
import wx

from libtextworker.general import logger

logger.UseGUIToolKit("wx")

ignore_not_exists: bool = False
create_new: bool = False


def _file_not_found(filename):
    if ignore_not_exists:
        return wx.ID_CANCEL
    if create_new == True:
        return wx.ID_YES
    return wx.MessageDialog(
        None,
        message=_("Cannot find file name %s - create it?") % filename,
        caption=_("File not found"),
        style=wx.YES_NO | wx.ICON_INFORMATION,
    ).ShowModal()


def start_app(files: list[str], directory: str | None = None):
    app = wx.App(0)

    from .mainwindow import MainFrame

    fm = MainFrame()

    if len(files) >= 1:
        nb = fm.notebook
        for i in range(0, len(files)):
            if i >= 1:
                nb.AddTab(tabname=files[i])

            if not os.path.exists(files[i]):
                if _file_not_found(files[i]) != wx.ID_YES:
                    nb.DeletePage(nb.GetSelection())
                    break

            try:
                # nb.fileops.OpenFile(files[i])
                open(files[i], "r")
            except Exception as e:
                logger.warning(e)
                nb.DeletePage(nb.GetSelection())
            else:
                nb.fileops.OpenFile(files[i])

    if directory != None:
        directory = os.path.realpath(os.path.curdir + "/" + directory)

        if os.path.exists(directory) and os.path.isdir(directory):
            fm.OpenDir(None, directory)
        else:
            logger.warning(e)

    if sys.platform == "win32":
        import ctypes

        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    else:
        is_admin = os.getuid() == 0

    if is_admin:
        wx.MessageBox(
            _(
                "You are running this program as root.\n"
                "You must be responsible for your changes."
            ),
            style=wx.OK | wx.ICON_WARNING,
            parent=fm.mainFrame,
        )

    app.SetTopWindow(fm.mainFrame)
    fm.Show()
    app.MainLoop()
