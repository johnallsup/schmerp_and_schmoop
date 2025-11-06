"""actions defined by ~/.schmerp.json

A very poor mans launcher thing.
I bind it to A-C-M-space and then define
shorthands in ~/.schmerp.json.
This is for things that aren't quite so common
that I want to bind an actual key combo to them,
but common enough that I want to be able to get them
slightly quicker than launching an terminal and using
that. The problem was that I would launch a throwaway
terminal to run something, not close it, and be left
with 100 open terminals that I had to go through to
find which ones I wanted to close.

If the shorthand is not found, we attempt to run as command,
so this also doubles as a quick command prompt.
We split ignoring quotes, so "o 'hello world'"
would split to ["o","'hello","world'"] -- if you want
full shell stuff, launch a terminal.

The first item is, after expansion, given to shutil.which()
to see if it is a command, and if so, then we execv that
command with the given arguments.

We append the result of the items to the result,
so that we could then append args to the entry. 
E.g. "x y z" would expand to
["run_something_with_no_args","y","z"]

Example ~/.schmerp.json
{
  "x": "run_something_with_no_args",
  "y": [ "run", "something", "with", "args" ]
}

what actually happens is in the DoSomething class,
which can be replaced so that e.g. we can run Python
code instead of just running an external program.

schmperp.json path given by SCHMERP defaulting to ~/.schmerp.json
label givenby SCHMERPLABEL defaulting to Schmerp
"""

import tkinter as tk
import tkinter.messagebox
import subprocess
import shutil
import os
import json
import re
import threading
import time
import textwrap
from glob import glob

class SchmerpMain:
  default_opts = {
      "bg": "#FFF",
      "fg": "#000",
      "ibg": "#FFF",
      "ifg": "#000",
      "font": "Optima",
      "fontsize": 30,
      "label": "Schmerp",
      "notes": None,
      "completion_enable": True,
      "grep_notes": False,
      "notes_height": 15
      }
  def __init__(self, delegate=None, opts = {}):
    self.opts = dict(self.__class__.default_opts)
    self.opts.update(opts)
    try:
      self.opts["fontsize"] = int(self.opts["fontsize"])
    except ValueError:
      print("Invalid fontsize",self.opts["fontsize"])
      raise
    self.delegate = delegate
    if delegate is not None:
      self.delegate.setParent(self)
 
  def input_callback(self,*xs):
    val = self.sv.get().strip()
    self.show_complete(val)
    self.grep_notes(val)

  def scroll_up(self,*xs):
    self.notes_tk.yview_scroll(-1, "units")

  def scroll_down(self,*xs):
    self.notes_tk.yview_scroll(1, "units")

  def scroll_up_10(self,*xs):
    self.notes_tk.yview_scroll(-10, "units")

  def scroll_down_10(self,*xs):
    self.notes_tk.yview_scroll(10, "units")

  def grep_notes(self,prefix):
    if not self.opts["grep_notes"]:
      return
    notes = self.notes
    lines = notes.split("\n")
    matching_lines = [ x for x in lines if x.startswith(prefix) ]
    wrapped_lines = [ "\n".join(textwrap.wrap(x,width=78)) for x in matching_lines ]
    result = "\n".join(wrapped_lines)
    notes_tk = self.notes_tk
    notes_tk.configure(state=tk.NORMAL)
    notes_tk.delete(1.0,tk.END)
    notes_tk.insert(tk.END,result)
    notes_tk.configure(state=tk.DISABLED)

  def show_complete(self,prefix):
    prefix = prefix.split(" ")[0]
    out = []
    completion_enable = self.opts["completion_enable"]
    if completion_enable:
      comps = self.delegate.complete(prefix)
      if prefix != "":
        if len(comps) == 0:
          out.append("no matches")
        else:
          ks = [ c[0] for c in comps ]
          out.append(" ".join(ks))
          for k,v in comps:
            out.append(f"{k}: {v}")
      else:
        ks = [ c[0] for c in comps ]
        out.append(" ".join(ks))
    txt = "\n".join(out)
    if completion_enable:
      comp = self.completions
      comp.configure(state=tk.NORMAL)
      comp.delete(1.0,tk.END)
      comp.insert(tk.END,txt)
      comp.configure(state=tk.DISABLED)

  def main(self):
    font = self.opts["font"]
    fontsize = self.opts["fontsize"]
    bg = self.opts["bg"]
    fg = self.opts["fg"]
    ifg = self.opts["ifg"]
    ibg = self.opts["ibg"]
    notes = self.opts["notes"]
    label_text = self.opts["label"]
    notes_height = self.opts["notes_height"]
    completion_enable = self.opts["completion_enable"]
    print(f"{completion_enable=}")

    root = tk.Tk()
    root.configure(background=bg)

    sv = tk.StringVar()
    sv.trace_add("write", self.input_callback)
    self.sv = sv
    label = tk.Label(root, text=f"{label_text}:", font=(font,fontsize), bg=bg, fg=fg)
    label.grid(row=0)
    textinput = tk.Entry(root,font=("Hack Nerd Font Mono",30),bg=ibg, fg=ifg, textvariable=sv)
    textinput.grid(row=0,column=1)
    textinput.focus()
    if completion_enable:
      completions = tk.Text(root, height=6, width=80)
      self.completions = completions
      completions.grid(row=1,columnspan=2)
      completions.configure(font = ("Hack Nerd Font Mono",12),bg=bg,fg=fg)
      completions.configure(state=tk.DISABLED)
    if notes is not None:
      notes_pars = re.split(r"\n{1,}",notes)
      notes_wrapped = [ "\n".join(textwrap.wrap(x,width=78)) for x in notes_pars ]
      nlines = len(notes_wrapped)
      nline_limit = notes_height
      if nlines > notes_height:
        nlines = notes_height
        notes_wrapped = "\n".join(notes_wrapped)
      else:
        notes_wrapped = notes
      notes_tk = tk.Text(root, height=nlines, width=80)
      self.notes = notes
      self.notes_tk = notes_tk
      notes_tk.grid(row=2,columnspan=2)
      notes_tk.configure(font = ("Hack Nerd Font Mono",12),bg=bg,fg=fg)
      notes_tk.insert(tk.END,notes_wrapped)
      notes_tk.configure(state=tk.DISABLED)

    root.bind('<Return>',self.return_handler)
    root.bind('<Escape>',self.escape_handler)
    root.bind('<Shift-BackSpace>',self.sbackspace_handler)
    root.bind('<Tab>',self.tab_handler)
    root.bind("<Up>", self.scroll_up)
    root.bind("<Down>", self.scroll_down)
    root.bind("<Shift-Up>", self.scroll_up_10)
    root.bind("<Shift-Down>", self.scroll_down_10)

    self.label = label
    self.textinput = textinput
    self.root = root

    if completion_enable:
      self.show_complete("")

    root.mainloop()

  def __call__(self,*xs,**kw):
    return self.main(*xs,**kw)

  def sbackspace_handler(self,e):
    self.textinput.delete(0,tk.END)

  def tab_handler(self,e):
    x = self.sv.get()
    completion_enable = self.opts["completion_enable"]
    if not completion_enable:
      return
    l = len(x)
    comps = [ c[0] for c in comps ]
    if len(comps) == 0:
      return
    suffixes = [ c[l:] for c in comps ]
    c0 = suffixes.pop(0)
    t = ""
    try:
      while len(c0) > 0:
        k = c0[0]
        for s in suffixes:
          if len(s) == 0 or k != s[0]:
            raise StopIteration()
        t += k
        c0 = c0[1:]
        suffixes = [ s[1:] for s in suffixes ]
    except StopIteration:
      pass
    y = x + t
    self.sv.set(y)
    self.delay_select_clear()
    return

  def delay_select_clear_task(self):
    time.sleep(0.001)
    self.textinput.select_clear()

  def delay_select_clear(self):
    thread = threading.Thread(target=self.delay_select_clear_task)
    thread.start()

  def escape_handler(self,e):
    print("Escape")
    exit()

  def return_handler(self,e):
    value = self.textinput.get()
    if self.delegate:
      try:
        if self.delegate(value):
          exit()
      except Exception as e:
        self.delegate.do_error(e)

  def run_something(self,wcmd,cmd):
    self.root.destroy()
    os.execv(wcmd,cmd)

class DoSomething:
  def __init__(self,cmds_fn=None,cmds_dir=None):
    self.parent = None
    self.schmerp = {
    }
    self.cmds_fn = cmds_fn
    if cmds_fn is not None:
      ifn = os.path.expanduser(cmds_fn)
      try:
        with open(ifn) as f:
          #self.schmerp = json.load(f)
          j = f.read()
          lines = j.splitlines()
          lines = [ re.sub(r"^\s*//.*$","",x) for x in lines ]
          lines = [ x.strip() for x in lines ]
          j = "\n".join(lines)
          self.schmerp = json.loads(j)
      except Exception as e:
        print("No ~/.schmerp.json",e)
        self.schmerp = {
        }
    if cmds_dir is not None:
      idir = os.path.expanduser(cmds_dir)
      if os.path.isdir(idir):
        jsons = glob(os.path.join(idir,"*.json"))
        for ifn in jsons:
          if not ( os.access(ifn,os.X_OK) and os.access(ifn,os.R_OK) ):
            continue
          try:
            with open(ifn) as f:
              self.schmerp.update(json.load(f))
          except Exception as e:
            print(f"Bad {ifn}",e)
            continue
          print("loaded from",ifn)

  def setParent(self,parent):
    self.parent = parent

  def complete(self,prefix):
    sch = self.schmerp
    ks = [ k for k in sch.keys() if k.startswith(prefix) ]
    out = []
    for k in ks:
      cmd = sch[k]
      if type(cmd) is list:
        cmd = " ".join(cmd)
      out.append((k,cmd))
    wcmd = shutil.which(prefix)
    if wcmd is not None:
      if prefix in ks:
        # put at end as shadowed
        out.append((prefix,f"## {wcmd}"))
      else:
        # put at start as not shadowed
        out.insert(0,(prefix,f"# {wcmd}"))
    return out

  def __call__(self,x):
    xs = re.split(r"\s+",x)
    x = xs[0]
    #print("call",x,self.cmds_fn,x not in self.schmerp,self.cmds_fn)
    if (x == ".e") and (x not in self.schmerp) and (self.cmds_fn is not None):
      cmds_fn = os.path.expanduser(self.cmds_fn)
      cmd = "konsole"
      args = [ "-e", "vi", cmds_fn ]
      xs = [ cmd, *args ]
    elif x in self.schmerp:
      #print("found")
      y = self.schmerp[x]
      xs.pop(0)
      if type(y) is str:
        xs.insert(0,y)
        if re.match(r"https?://",y):
          xs.insert(0,"o")
      elif type(y) is list:
        xs = y + xs
      elif type(y) is dict:
        if not "cmd" in y:
          self.do_error(ValueError(f"No cmd in dict for {x}"))
        cmd = y['cmd']
        if "env" in y:
          env = y['env']
          if not type(env) is dict:
            self.do_error(ValueError(f"Env for {x} not a dict"))
          for k,v in env.items():
            os.environ[k] = v
        if type(cmd) is str:
          xs.insert(0,cmd)
        elif type(cmd) is list:
          xs = cmd + xs
        else:
          self.do_error(ValueError("Must be string or list 2"))
      else:
        self.do_error(ValueError("Must be string or list"))
    cmd, *args = xs
    try:
      self.do(cmd,*args)
      return True
    except FileNotFoundError:
      self.do_error(f"File not found: {cmd}")
      return False
    except Exception as e:
      self.do_error(e)
      return False

  def do(self,cmd,*args):
    #print("do",cmd,args)
    cmd = os.path.expanduser(cmd)
    os.environ["PATH"] = os.path.expanduser("~/bin")+":"+os.environ["PATH"]
    wcmd = shutil.which(cmd)
    if wcmd is not None:
      if self.parent is not None:
        self.parent.run_something(wcmd,[cmd,*args])
        return True
      else:
        return os.execv(wcmd,[cmd,*args])
    else:
      raise FileNotFoundError(f"Cannot do {cmd}")

  def do_error(self,e,return_code=False):
    print("do_error",e)
    txt = repr(e)
    tk.messagebox.showinfo(message=txt,icon=tkinter.messagebox.ERROR)
    if return_code is not False:
      exit(return_code)

