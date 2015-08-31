#!/usr/bin/env python
"""
A GUI Utility for generating deterministic passwords.
"""

import hashpass

import hashlib
import Tkinter
import tkFont


class HashPass(Tkinter.Frame, object):
  """Application main frame.
  (As in the primary frame, not like a supercomputer or anything.)
  """
  def __init__(self, parent):
    super(HashPass, self).__init__(parent)
    self.parent = parent
    self.parent.title("HashPass")

    self.font_mono = tkFont.Font(family="Monospace", size=9)

    self.entry_var = Tkinter.StringVar()
    self.entry_var.trace("w", lambda *args: self.on_change_entry())

    self.entry = Tkinter.Entry(self,
        width=40,
        textvariable=self.entry_var,
        font=self.font_mono)
    self.entry.grid(sticky=Tkinter.W)
    self.entry.focus_set()
    self.entry.bind("<Return>", lambda *args: self.on_press_enter())

    self.label_hash = Tkinter.Label(self,
        text="ab3246947813fd6df239c589f9c8a4d3d5826496",
        font=self.font_mono)
    self.label_hash.grid(sticky=Tkinter.W)

    self.label_clipboard = Tkinter.Label(self,
        text="Enter text to get the sha1.",
        font=self.font_mono)
    self.label_clipboard.grid(sticky=Tkinter.W)

    self.pack()

  def on_change_entry(self):
    plain = self.entry_var.get()
    if len(plain) == 0:
      return
    hashed = hashpass.hash(plain)
    self.label_hash.config(text=hashed)
    copy_to_clipboard(hashed)
    self.label_clipboard.config(text=(
      "Copied to clipboard. "
      "Enter to clear."))


  def on_press_enter(self):
    self.entry_var.set("")


def hash_sha1(input):
  """Take the sha1 hash of a thing."""
  return hashlib.sha1(input).hexdigest()


def copy_to_clipboard(string):
   """Copy a string the system clipboard."""
   tk = Tkinter.Tk()
   tk.withdraw()
   tk.clipboard_clear()
   tk.clipboard_append(string)
   tk.destroy()


if __name__ == "__main__":
  print "Started."
  root = Tkinter.Tk()
  Sha1it(root)
  root.mainloop()
