#!/usr/bin/env python
"""
A GUI Utility for generating deterministic passwords.
"""

from hashpasslib import *

import hashlib
import Tkinter
import tkFont
import threading
import time


class HashPass(Tkinter.Frame, object):
  """Application main frame.
  (As in the primary frame, not like a supercomputer or anything.)
  """
  def __init__(self, parent):
    super(HashPass, self).__init__(parent)
    self.parent = parent
    self.parent.title("HashPass")

    self.clipboard_thread = DelayedClipboardThread()

    # Keyboard shortcuts for quit.
    for keys in ["<Control-q>", "<Control-c>", "<Control-d>", "<Control-w>"]:
      self.bind_all(keys, lambda *args: self.on_kb_quit())

    self.font_mono = tkFont.Font(family="Monospace", size=9)

    self.entry_var = Tkinter.StringVar()
    self.entry_var.trace("w", lambda *args: self.on_change_entry())

    self.entry = Tkinter.Entry(self,
        width=40,
        textvariable=self.entry_var,
        show="*",
        font=self.font_mono)
    self.entry.grid(sticky=Tkinter.W)
    self.entry.focus_set()
    self.entry.bind("<Return>", lambda *args: self.on_press_enter())

    self.label_hash = Tkinter.Label(self,
        text="",
        font=self.font_mono)
    self.label_hash.grid(sticky=Tkinter.W)

    self.need_new_master = read_stored_master() == None
    self.need_master = True

    label_clipboard_text = "Enter a master password.\n" + \
        "It will be bcrypted and saved to disk." if self.need_new_master \
        else "Enter your master password."

    self.label_clipboard = Tkinter.Label(self,
        text=label_clipboard_text,
        font=self.font_mono)
    self.label_clipboard.grid(sticky=Tkinter.W)

    self.pack()

  def on_change_entry(self):
    plain = self.entry_var.get()
    if len(plain) == 0 or self.need_master:
      return
    hashed = make_password(plain, old=True)
    self.label_hash.config(text=hashed)
    self.clipboard_thread.send_to_clipboard_at_some_point(hashed)
    self.label_clipboard.config(text=(
      "Copied to clipboard. "
      "Enter to clear."))

  def on_press_enter(self):
    if self.need_master:
      self.on_submit_master(self.entry_var.get())
    else:
      self.entry_var.set("")
      self.label_hash.config(text="")
      self.label_clipboard.config(
          text=("Enter the website name to generate a password."))

  def on_kb_quit(self):
    """When a keyboard shortcut to quit is pressed."""
    self.quit()

  def on_submit_master(self, master):
    if self.need_new_master:
      store_master(master)
      self.need_new_master = False
      self.label_clipboard.config(text=("Enter the password again."))
    elif self.need_master:
      if is_correct_master(master):
        use_master(master, use_bcrypt=False)
        self.label_clipboard.config(
            text=("Enter the website name to generate a password."))
        # Clear the password.
        self.entry_var.set("")
        # Disable password hiding.
        self.entry.config(show="")
        self.need_master = False
      else:
        self.label_clipboard.config(text=(
            "That didn't match your saved master. "))
        self.entry_var.set("")


class DelayedClipboardThread(object):
  def __init__(self):
    self._event = threading.Event()
    self._lock = threading.RLock()
    self._value = None

    self._thread = threading.Thread(target=self._run)
    self._thread.daemon = True
    self._thread.start()

  def send_to_clipboard_at_some_point(self, s):
    with self._lock:
      self._value = s
    self._event.set()

  def _run(self):
    while True:
      self._event.wait()
      with self._lock:
        s = self._value
        self._event.clear()
      if s != None:
        send_to_clipboard(s)
      time.sleep(0.2)


if __name__ == "__main__":
  root = Tkinter.Tk()
  HashPass(root)
  root.mainloop()
