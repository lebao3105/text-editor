from tkinter import END
from tkinter.filedialog import *
from tkinter.messagebox import askyesno
from sys import platform
import os, sys
from . import constant

sys.path.append(os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__)
                    )
                )
            )
import tabs

# Use this for closing the application
is_saved = False
# Saved files
saved_files = [ ]

if platform == "win32":
    searchdir = os.environ["USERPROFILE"]+"\Documents"
    script_type = ("Windows Shell Script", "*.bat, *.cmd")
elif platform == "linux":
    searchdir = os.environ["HOME"]+"/Documents"
    script_type = ("UNIX Shell Script", "*.sh")

def find_text_editor(self):
    if hasattr(self, 'text_editor'):
        return
    else:
        raise Exception("Text editor not found!")

def open_file(self, event=None):
    file_name = askopenfilename(initialdir=searchdir,
                                title=self._("Select a file to open"), 
                                filetypes=(("All files", "*.*"),
                                script_type, ("Text files", "*.txt")))
    if file_name:
        find_text_editor(self)

        if not self.text_editor.compare("end-1c", "==", 1.0):
            tabs.add_tab(self)
        
        for x in constant.FILES_ARR:
            if file_name in x:
                if asktoopen(self):
                    pass
        
        openfilename(self, file_name)
                
def openfilename(tkwin, filename):
        with open(filename, "r") as f:
            print('Opening file: ', filename)
            tkwin.text_editor.insert(1.0, f.read())
            tkwin.title(tkwin._("Text editor") + " - " + filename)
            tkwin.notebook.tab("current", text=filename)
        
        constant.FILES_ARR.append(filename)
            
        #print(constants.FILES_ARR)

def save_file(self, event=None):
    find_text_editor(self)
    filefind = self.notebook.tab(self.notebook.select(), "text")
    #print(filefind)
    if self.text_editor.compare("end-1c", "==", 1.0):
        save_as(self)
    elif not (filefind in constant.FILES_ARR):
        save_as(self)
    else:
        try:
            with open(filefind, "w") as f:
                print('Saving file: ', filefind)
                f.write(self.text_editor.get(1.0, END))
        finally:
            saved_files.append(filefind)

def save_as(self, event=None):
    find_text_editor(self)
    file_name = asksaveasfilename(initialdir=searchdir, 
                                    title=self._("Save as"),
                                    filetypes=(("All files", "*.*"),
                                    script_type, ("Text files", "*.txt")))
    if file_name:
        try:
            with open(file_name, "w") as f:
                print('Saving new file: ', file_name)
                f.write(self.text_editor.get(1.0, END))
        finally:
            constant.FILES_ARR.append(file_name)
            saved_files.append(file_name)

def asktoopen(self):
    _ = self._
    ask = askyesno(_("Infomation"),
                _("This file is opened in another tab. By default we will load the contents to a new tab.\nDo it?"))
    if ask:
        tabs.add_tab(self)
        return True