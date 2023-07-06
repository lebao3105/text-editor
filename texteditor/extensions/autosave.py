from tkinter import Toplevel, messagebox as msb, Misc
from .generic import global_settings, clrcall
from libtextworker.general import logger, CraftItems, GetCurrentDir
from pygubu.builder import Builder
from threading import Thread

enabled = global_settings.getkey("editor.autosave", "enable", False, True)
time = global_settings.getkey("editor.autosave", "time", False, True)

if not enabled in global_settings.yes_values:
    enabled = False

if not int(time):
    time = 30

TOGGLE: bool = bool(enabled)


class AutoSave:
    Editor: Misc
    CurrDelay: int = time

    def Start(self, time_: int = time):
        self.CurrDelay = time_
        if not enabled:
            return
        self.TaskId = self.Editor.after(int(time_) * 1000, lambda: self.SaveFunc())

    def Stop(self):
        self.Editor.after_cancel(self.TaskId)
        self.__delattr__("TaskId")

    def CheckToggle(self):
        if not TOGGLE and hasattr(self, "TaskId") == True:
            self.Stop()
        elif not hasattr(self, "TaskId"):
            self.Start()

    def Toggle(self, on: bool):
        if on:
            self.Start()
        else:
            self.Stop()

    def __init__(self):
        Thread(target=self.CheckToggle, daemon=True).start()


class AutoSaveConfig(Toplevel):
    """
    Autosave window.
    """
    isShown : bool = False

    timealiases = {
        _("30 seconds"): 30,
        _("1 minute"): 60,
        _("2 minutes"): 120,
        _("5 minutes"): 300,
        _("10 minutes"): 600,
        _("15 minutes"): 900,
        _("20 minutes"): 1200,
        _("30 minutes"): 1800,
    }

    def __init__(self, master: Misc | None = None):
        super().__init__(master)
        self.grab_release()
        self.wm_title("AutoSave config")
        self.wm_protocol("WM_DELETE_WINDOW", self.OnClose)
        self.resizable(False, False)

        self.builder = Builder(_)
        self.builder.add_from_file(
            CraftItems(GetCurrentDir(__file__), "../views", "autosave.ui")
        )

        self.dialog = self.builder.get_object("frame", self)
        self.combobox = self.builder.get_object("combobox1", self.dialog)
        self.checkbtn = self.builder.get_object("checkbutton1", self.dialog)
        self.combobox["values"] = [item for item in self.timealiases]
        self.combobox["state"] = "readonly"

        clrcall.configure(self.dialog, True)
        self.builder.connect_callbacks(self)

    def do_the_task(self):
        choice = self.builder.get_variable("selected_time").get()
        do_save = self.builder.get_variable("save").get()
        if choice:
            global_settings.set("editor.autosave", "time", self.timealiases[choice])
            if do_save:
                global_settings.update()

    """
    BUG: This func auto runs on editor init??? (unexpectedly)
    """
    
    def ShowWind(self):
        if not self.isShown:
            self.mainloop()
            self.isShown = True
        else:
            self.focus()

    def OnClose(self):
        self.isShown = False
        self.quit()