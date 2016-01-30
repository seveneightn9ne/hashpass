#!/usr/bin/env python
"""
A GUI Utility for generating deterministic passwords.
"""

import hashpasslib

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

    self.label_clipboard = Tkinter.Label(self,
        text="",
        font=self.font_mono)
    self.label_clipboard.grid(sticky=Tkinter.W)

    self.ask_for_master()

    self.pack()

  def ask_for_master(self, message=None):
    print "asked"
    if message == None:
        if hashpasslib.read_stored_master() == None:
            message = "Enter a master password.\nIt will be bcrypted and saved to disk."
            self.no_saved_master = True
        else:
            message = "Enter your master password."
            self.no_saved_master = False
    self.asked_for_master = True #Unset by pressing enter
    self.clear_textbox()
    self.label_clipboard.config(text=(message))

  def ask_for_website(self):
    self.clear_textbox()
    self.entry.config(show="")
    self.label_clipboard.config(text=("Enter the website name to generate a password."))

  def clear_textbox(self):
    self.entry_var.set("")

  def on_change_entry(self):
    print "onchange"
    if self.asked_for_master:
      return
    plain = self.entry_var.get()
    if len(plain) == 0:
      self.label_hash.config(text="")
      return
    hashed = hashpasslib.make_password(plain, old=False)
    self.label_hash.config(text=hashed)
    self.clipboard_thread.send_to_clipboard_at_some_point(hashed)
    self.label_clipboard.config(text=(
      "Copied to clipboard. "
      "Enter to clear."))

  def on_press_enter(self):
    print "enter"
    if self.asked_for_master:
      self.on_submit_master(self.entry_var.get())
    else:
      self.ask_for_website()

  def on_kb_quit(self):
    """When a keyboard shortcut to quit is pressed."""
    self.quit()

  def on_submit_master(self, master):
    print "submit master"
    self.asked_for_master = False
    if self.no_saved_master:
      hashpasslib.store_master(master)
      self.no_saved_master = False
      self.ask_for_master("Enter the password again.")
    else:
      if hashpasslib.is_correct_master(master):
        hashpasslib.use_master(master, use_bcrypt=True)
        self.ask_for_website()
      else:
        self.ask_for_master("That didn't match your saved master. ")


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
        hashpasslib.send_to_clipboard(s)
      time.sleep(0.2)


if __name__ == "__main__":
  root = Tkinter.Tk()
  HashPass(root)
  root.mainloop()
