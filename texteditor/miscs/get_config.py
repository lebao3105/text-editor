from tkinter import font, messagebox
from . import constants
import os
import configparser
import platform

if platform.system() == "Windows":
    file = os.environ["USERPROFILE"] + "\\.config\\texteditor_configs.ini"
    backup = os.environ["USERPROFILE"] + "\\.config\\texteditor_bck.ini"
    defconsole = "cmd"
else:
    file = os.environ["HOME"] + "/.config/texteditor_configs.ini"
    backup = os.environ["HOME"] + "/.config/texteditor_bck.ini"
    defconsole = "xterm"

cfg = configparser.ConfigParser()

# Default variables.
# We must use cfg.get() to get the current variable's value.
cfg["global"] = {
    "color": "light",
    "sub_color": "default",
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
cfg["filemgr"] = {"autosave": "yes", "autosave-time": "30"}  # in minutes

# File write/backup
with open(backup, "w") as f2:
    cfg.write(f2)
with open(backup, "r") as f:
    bck = f.read()

if not os.path.isfile(file):
    try:
        with open(file, "w") as f:
            cfg.write(f)
    except:
        raise Exception("Unable to write configuration file!")

cfg.read(file)

bg = cfg.get("global", "color")
fg = cfg.get("global", "sub_color")


# OK, so this class only able to change some configuration? Can we use more?
class GetConfig:
    """Changes Tkinter/TTK widget configuration from the configuration file."""

    def __init__(self, parent=None, action: str = None):
        """parent: Widget to use\n
        action:str=None: |\n
        --> config : Configure the widget\n
        --> reset : Reset the configuration file\n
        If you use config, you must include parent also."""
        super().__init__()
        if parent == None or "":
            if action == "reset":
                self.reset()

        if action != None or "":
            if action == "config":
                self.configure(parent)
            elif action == "reset":
                self.reset()

    @staticmethod
    def reset():
        if not bck:
            print(
                "Error: Unable to reset configuration file: Backed up default variables not found"
            )
            return False
        try:
            os.remove(file)
            with open(file, "w") as f:
                f.write(bck)
        except OSError as e:
            raise messagebox.showerror(
                "Error occured while writing contents to the file", str(e)
            )
        finally:
            print("Completed resetting texteditor configuration file.")
            return True

    @staticmethod
    def checkclass(widget):
        wind = ["Tk", "Frame", "TopLevel"]
        text = ["Label", "Text"]
        ttk_widgets = ["TCombobox"]

        # Combine 3 arrays together
        for it in text:
            wind.append(it)
        for it2 in ttk_widgets:
            wind.append(it2)

        class_name = widget.winfo_class()
        if class_name in wind or cfg.sections():
            return class_name
        else:
            return False

    @staticmethod
    def configure(widget):
        class_name = GetConfig.checkclass(widget)
        if class_name:
            fg2, colormode = GetConfig._checkcolor(GetConfig, widget)
            font_type, font_size = GetConfig._checkfont(GetConfig)
            if colormode == "dark":
                try:
                    widget.configure(fg=fg2, bg=constants.DARK_BG)
                except:
                    widget.configure(foreground=fg2, background=constants.DARK_BG)
            if font_type and font_size is not None:
                widget.configure(font=(font_type, int(font_size)))

    @staticmethod
    def change_config(section: str, option: str, value: str | int, event=None):
        cfg.set(section, option, str(value))
        try:
            with open(file, "w") as filed:
                cfg.write(filed)
        except:
            print("Unable to write new configuration!")
            print(
                "Detail: make section %s->option %s to use value %s"
                % (section, option, value)
            )
            return False
        finally:
            print("Changed texteditor configuration.")
            return True

    def _checkcolor(self, widget):
        if bg == "dark":
            if fg == "default":
                fg2 = constants.LIGHT_BG
            elif fg == "Green":
                fg2 = constants.GREEN_TEXT
            elif fg == "Red":
                fg2 = constants.RED_TEXT
            else:
                fg2 = constants.LIGHT_BG
            if GetConfig.checkclass(widget) == "Text":
                widget.configure(insertbackground=constants.LIGHT_BG)
            return fg2, "dark"
        else:
            fg2 = constants.LIGHT_BG
            if GetConfig.checkclass(widget) == "Text":
                widget.configure(insertbackground=constants.DARK_BG)
            return fg2, "light"

    def _checkfont(self):
        # Get values
        font_type = self.getvalue("global", "font")
        font_size = self.getvalue("global", "font_size")

        if not int(font_size):
            messagebox.showwarning(
                "Warning",
                "Wrong font size defined on the configuration file - the program will use font size 14.",
            )
            font_size = "14"
        elif int(font_size) <= 11:
            messagebox.showwarning(
                "Warning", "The defined font size is smaller (or equal) than 10."
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
                        message="Wrong font type in the configuration file."
                    )
                    isshown = True
                font_type = "Consolas"

        return font_type, font_size

    @staticmethod
    def getvalue(section: str, name: str):
        if not section in cfg.sections():
            raise Exception("Section %s not found" % section)
        elif not cfg[section][name]:
            raise Exception("%s->%s not found" % section, name)
        else:
            return cfg.get(section, name)
