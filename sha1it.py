#!/usr/bin/env python
"""
A GUI Utility for taking the SHA1 hash of a string.

Enter a string and press enter or press the button.
The string will be hashed and the result will be displayed
and copied to the clipboard.
"""

import hashlib
import Tkinter
from Tkinter import Tk

def hash(input):
  """Take the sha1 hash of a thing."""
  return hashlib.sha1(input).hexdigest()

def copy_to_clipboard(string):
   """Copy a string the system clipboard."""
   tk = Tk()
   tk.withdraw()
   tk.clipboard_clear()
   tk.clipboard_append(string)
   tk.destroy()

class Sha1it(Tkinter.Frame, object):
  def __init__(self, parent):
    super(Sha1it, self).__init__(parent)
    self.parent = parent

    self.parent.title("Sha1it")

    self.entry = Tkinter.Entry(self)
    self.entry.pack(side=Tkinter.LEFT)

    self.button_generate = Tkinter.Button(self,
      text="Sha1",
      command=self.click_generate)
    self.button_generate.pack()

    self.pack(fill=Tkinter.BOTH, expand=1)

  def click_generate(self):
    input = self.entry.get()
    hashed = hash(input)
    self.entry.delete(0, Tkinter.END)
    self.entry.insert(0, hashed)
    copy_to_clipboard(hashed)


if __name__ == "__main__":
  root = Tk()
  root.geometry("250x150")
  Sha1it(root)
  root.mainloop()
