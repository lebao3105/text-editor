"""This module adds tab to the tkinter.Notebook widget.
It also handles what's happening in the child widget of the tab (tkinter.Text)...
"""
import gettext
from hashlib import md5
from tkinter import Frame, Tk, Menu
from tkinter.ttk import Notebook
from texteditor.miscs import constants, file_operations, textwidget

_ = gettext.gettext

window_title = _("Text Editor") + " - "
newtab_name = _(constants.UNTITLED)


class TabsViewer(Notebook):
    """A configured Tkinter Notebook with a simple right-click menu."""

    def __init__(self, master: Frame | Tk, **kw):
        super().__init__(master, **kw)
        self.parent = master
        master.notebook = self

        dummy = Frame()
        self.add(dummy, text="+")

        # Tab name
        self.tabname = self.tab(self.select(), "text")

        # Now, make a right-click menu
        # TODO: Make some function which will add more items to the menu
        right_click_menu = Menu(self, tearoff=0)
        right_click_menu.add_command(
            label=_("New tab"), command=lambda: self.add_tab(self)
        )
        right_click_menu.add_command(
            label=_("Close the current opening tab"),
            accelerator="Ctrl+I",
            command=lambda: self.close_tab(),
        )
        self.bind(
            "<Button-3><ButtonRelease-3>",
            lambda event: right_click_menu.post(event.x_root, event.y_root),
        )
        self.bind("<<NotebookTabChanged>>", self.tab_changed)
        # Place the notebook
        self.pack(expand=True, fill="both")

    def add_tab(self, event=None, idx=None):

        # Add a new tab
        textframe = Frame(self)
        if idx is not None:
            self.insert(idx, textframe, text=newtab_name)
        else:
            self.add(textframe, text=newtab_name)

        # Add contents
        self.parent.text_editor = textwidget.TextWidget(
            textframe, useMenu=True, useUnRedo=True
        )
        self.parent.text_editor.addMenusepr()
        self.parent.text_editor.addMenucmd(
            label=_("Save"), acc="Ctrl+S", fn=lambda: file_operations.save_file(self)
        )
        self.parent.text_editor.addMenucmd(
            label=_("Save as"),
            acc="Ctrl+Shift+S",
            fn=lambda: file_operations.save_as(self),
        )
        self.parent.text_editor.pack(expand=True, fill="both")

        self.select(textframe)
        self.titletext = window_title + newtab_name
        self.parent.title(self.titletext)

    def close_tab(self):
        # TODO: Check for the file content (also for mainwindow close event)
        tabnum = self.index("end")
        if tabnum == 1:
            # Close the window if there are no other tabs
            print(_("No other tab(s) here, trying to close the window..."))
            self.parent.destroy()
        else:
            self.forget(self.select())

    def tab_changed(self, event=None):
        if self.select() == self.tabs()[-1]:
            self.add_tab(idx=(len(self.tabs())-1))
        tabname = event.widget.tab("current")["text"]
        self.parent.title(_("Text Editor") + " - " + tabname)
