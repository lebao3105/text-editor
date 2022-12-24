import configparser
import darkdetect
import os
import platform
import sv_ttk
import texteditor
import threading
from tkinter import TclError, font, messagebox
from . import constants, logger


if platform.system() == "Windows":
    file = os.environ["USERPROFILE"] + "\\.config\\texteditor_configs.ini"
    backup = os.environ["USERPROFILE"] + "\\.config\\texteditor_bck.ini"
    defconsole = "cmd"
else:
    file = os.environ["HOME"] + "/.config/texteditor_configs.ini"
    backup = os.environ["HOME"] + "/.config/texteditor_bck.ini"
    defconsole = "xterm"

cfg = configparser.ConfigParser()
log = logger.Logger("texteditor.backend.get_config")

# Default variables.
# We must use cfg.get() to get the current variable's value.
cfg["global"] = {
    "color": "light",
    "sub_color": "default",
    "autocolor": "yes",
    "font": "default",
    "font_size": "12",
}

# An old configuration
cfg["popups"] = {
    # TODO/NOTE: They should be different
    "width": str(constants.DEFAULT_OTHERS_WIGHT),
    "height": str(constants.DEFAULT_OTHERS_WIGHT),
}

cfg["cmd"] = {"defconsole": defconsole, "isenabled": "yes"}

# New: Auto-save files
cfg["filemgr"] = {"autosave": "yes", "autosave-time": "120"}  # in seconds

# File write/backup
with open(backup, "w") as f2:
    cfg.write(f2)
with open(backup, "r") as f:
    bck = f.read()

if not os.path.isfile(file):
    with open(file, mode="w") as f:
        try:
            f.write(cfg)
        except:
            log.throwerr("Unable to write things into the configuration file")

cfg.read(file)

bg = cfg.get("global", "color")
fg = cfg.get("global", "sub_color")

autocolormode = False


class GetConfig:
    """Changes Tkinter/TTK widget configurations from the configuration file."""

    def __init__(self, parent=None, action: str = None, _=None):
        """parent: Widget to use\n
        action:str=None: |\n
        --> config : Configure the widget\n
        --> reset : Reset the configuration file\n
        If you use config, you must include parent also.\n
        _=None: Gettext translation"""

        if _ is not None:
            self._ = _
        else:
            self._ = texteditor._

        if parent is None or "":
            if action == "reset":
                self.reset()

        if action is not None or "":
            if action == "config":
                self.configure(parent)
            elif action == "reset":
                self.reset()

    @staticmethod
    def reset():
        if not bck:
            log.throwerr(
                "Error: Unable to reset configration file",
                "Backed up variables not found",
            )
            return False
        try:
            os.remove(file)
            with open(file, "w") as f:
                f.write(bck)
        except OSError as e:
            messagebox.showerror(
                GetConfig._("Error occured while writing contents to the file"),
                GetConfig._("Details: %s") % str(e),
            )
            log.throwerr("Error: Unable to reset configuration file")
            return
        finally:
            log.throwinf("Reset texteditor configuration file - completed.")
            return True

    @staticmethod
    def checkclass(widget):
        wind = ["Tk", "Frame", "TopLevel"]
        text = ["Label", "Text"]
        ttk_widgets = ["TCombobox", "Button"]

        # Combine 3 arrays together
        for it in text:
            wind.append(it)
        for it2 in ttk_widgets:
            wind.append(it2)

        class_name = widget.winfo_class()
        if class_name in (wind or cfg.sections()):
            return class_name
        else:
            return False

    @staticmethod
    def configure(widget):
        """Configures the selected widget.
        This function is used for texteditor with
        _checkfont, so please make your own function."""
        classname = GetConfig.checkclass(widget)
        colormger = AutoColor(widget)
        if classname is not False:
            if classname not in ["Tk", "Frame", "TopLevel", "Button"]:
                font_type, font_size = GetConfig._checkfont(GetConfig)
                if font_type and font_size is not None:
                    widget.configure(font=(font_type, int(font_size)))
            colormger.changecolor()

    @staticmethod
    def change_config(section: str, option: str, value: str | int, event=None):
        cfg.set(section, option, str(value))
        with open(file, "w") as filed:
            try:
                cfg.write(filed)
            except:
                log.throwerr(
                    "Unable to write new configuration! (make %s->%s use %s)" % section,
                    option,
                    value,
                )
                return False
            finally:
                log.throwinf("Changed texteditor configuration.")
                return True

    def _checkfont(self):
        # Get values
        font_type = self.getvalue("global", "font")
        font_size = self.getvalue("global", "font_size")

        if not int(font_size):
            messagebox.showwarning(
                self._("Warning"),
                self._(
                    "Wrong font size defined on the configuration file - the program will use font size 14."
                ),
            )
            font_size = "14"
        elif int(font_size) <= 11:
            messagebox.showwarning(
                self._("Warning"),
                self._("The defined font size is smaller (or equal) than 10."),
            )

        font_families = font.families()
        if font_type == "default":
            font_type = "Consolas"
        else:
            if font_type not in font_families:
                if (
                    not isshown
                ):  # To prevent the application from showing the message box after open a new tab
                    messagebox.showwarning(
                        message=self._("Wrong font type in the configuration file.")
                    )
                    isshown = True
                font_type = "Consolas"

        return font_type, font_size

    @staticmethod
    def getvalue(section: str, name: str):
        if not section in cfg.sections():
            raise log.throwerr("Configuration section %s not found" % section)
        elif not cfg[section][name]:
            raise log.throwerr("Configuration %s->%s not found" % section, name)
        else:
            return cfg.get(section, name)


class AutoColor:
    """The color manager for texteditor."""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.start = autocolormode = GetConfig.getvalue("global", "autocolor")
        self.autocolor = self.start

        self.bg = GetConfig.getvalue("global", "color")
        self.fg = GetConfig.getvalue("global", "sub_color")
        self.colors = {"light": str(constants.DARK_BG), "dark": str(constants.LIGHT_BG)}
        if self.bg == "default":
            self.bg = "light"
        if self.fg == "default":
            self.fg = "dark"

    def startasync(self):
        if self.start is True:
            # Automatically changes the theme if
            # the system theme is CHANGED
            self.t = threading.Thread(target=darkdetect.listener, args=(self.setcolor,))
            self.t.daemon = True
            self.t.start()
            self.setcolor(darkdetect.theme())
            return
        else:
            self.start = True

    def stopasync(self):
        if hasattr(self, "t"):
            del self.t

    def changecolor(self):
        if self.start is True:
            self.startasync()
            # return
        else:
            self.setcolor()

    def setcolor(self, color: str = None):
        fg = self.__checkcolor(str(darkdetect.theme()).lower())
        if color is not None:
            sv_ttk.set_theme(color.lower())
        else:
            if self.autocolor == "yes":
                sv_ttk.set_theme(str(darkdetect.theme()).lower())
            else:
                theme = self.bg
                fg = self.colors[self.fg]
                sv_ttk.set_theme(theme)

        # Set the foreground
        try:
            self.parent.configure(fg=fg)
        except TclError:
            self.parent.configure(foreground=fg)

    def __checkcolor(self, bg):
        if bg == "dark":
            if fg == "default":
                fg2 = constants.LIGHT_BG
            elif fg == "Green":
                fg2 = constants.GREEN_TEXT
            elif fg == "Red":
                fg2 = constants.RED_TEXT
            else:
                fg2 = constants.LIGHT_BG
        else:
            fg2 = constants.DARK_BG
        return fg2
