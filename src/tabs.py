from tkinter import *
from tkinter import ttk
import miscs.init
import miscs.file_operations

# For example:
# We have 2 tabs: Untitled and Untitled 2. You close Untitled
# and create a new tab. The new tab's name is Untitled 2 - not 3.
# This is because tab_name = tabs number + 1, which can occur problem
# like that.
def checker(self):
    # get the current tab name
    find_tab = self.notebook.tab(self.notebook.select(), "text")
    # if the number in find_tab = tabs index, return True
    if str(self.notebook.index("end")) in find_tab:
        return True
    # if this is the first tab yet
    elif find_tab == self._("Untitled "):
        return True
    # what I mentioned before
    elif str(self.notebook.index("end") + 1) in find_tab:
        return False

def add_tab(self):
    # check if there are no tabs yet
    if self.notebook.index("end") == 0:
        # if there's no tab yet, create a new one
        firsttab = Frame(self.notebook)
        self.notebook.add(firsttab, text=self._("Untitled "))
        # place the textbox
        place_textbox(firsttab, self)
        self.notebook.select(firsttab)
    else:
        if checker(self):
            tab_name = self.notebook.index("end") + 1
        else:
            tab_name = self.notebook.index("end") + 2
        new_tab = Frame(self.notebook)
        self.notebook.add(new_tab, text=self._("Untitled ") + str(tab_name))
        place_textbox(new_tab, self)
        self.notebook.select(new_tab)

def place_textbox(self, root):
    # Text box
    self.text_editor = Text(self, wrap="word", undo=True, font=("Arial", 12))
    self.text_editor.bind("<Button-3><ButtonRelease-3>", lambda event:place_right_click_menu(self, event, root))
    self.text_editor.pack(expand=True, fill="both")
    # Scrollbar
    self.scroll = ttk.Scrollbar(self.text_editor, orient="vertical", command=self.text_editor.yview)
    self.scroll2 = ttk.Scrollbar(self.text_editor, orient="horizontal", command=self.text_editor.xview)
    self.scroll.pack(side="right", fill="y")
    self.scroll2.pack(side="bottom", fill="x")
    self.text_editor.configure(yscrollcommand=self.scroll.set, xscrollcommand=self.scroll2.set, undo=True, autoseparators=True)
    root.text_editor = self.text_editor
    miscs.init.initialize(self.text_editor, 2)

def tabs_close(self):
    # Automatically close the window if there's only one tab
    if self.notebook.index("end") == 1:
        print(self._("No other tabs left, asking for close the window..."))
        miscs.init.ask_quit(self)
    # If not, just close the selected tab and keep
    # the main window open
    else:
        self.notebook.forget(self.notebook.select())

def place_right_click_menu(self, event, root):
    try:
        m = Menu(self.text_editor, tearoff=0)
        m.add_command(label=root._("Copy"), accelerator="Ctrl+C", event=event.widget.event_generate("<Control-c>"))
        m.add_command(label=root._("Paste"), accelerator="Ctrl+V", event=event.widget.event_generate("<Control-v>"))
        m.add_command(label=root._("Cut"), accelerator="Ctrl+X", event=event.widget.event_generate("<Control-x>"))
        m.add_separator()
        m.add_command(label=root._("Save"), accelerator="Ctrl+S", event=event.widget.event_generate("<Control-s>"))
        m.add_command(label=root._("Save as"), accelerator="Ctrl+Shift+S", event=event.widget.event_generate("<Control-Shift-s>"))
        m.add_separator()
        m.add_command(label=root._("Undo"), accelerator="Ctrl+Z", event=event.widget.event_generate("<Control-z>"))
        m.add_command(label=root._("Redo"), accelerator="Ctrl+Y", event=event.widget.event_generate("<Control-y>"))
        m.tk_popup(event.x_root, event.y_root)
    finally:
        m.grab_release()

