#!/usr/bin/env python

import os

from schmerp_core import SchmerpMain, DoSomething
from do_chrome_alias_handler import DoChromeAlias

schmerp_json_fn = os.getenv("CMDS","~/.schmerp.json")
schmerp_json_dir = os.getenv("CMDDIR","~/.schmerp.d")
schmerp_label_text = os.getenv("LABEL","Schmerp")
schmerp_notes_fn = os.getenv("SCHMERP_NOTES",None)
schmerp_notes = None
schmerp_bg = os.getenv("BG","#FFF")
schmerp_fg = os.getenv("FG","#000")
schmerp_ibg = os.getenv("IBG","#FFF")
schmerp_ifg = os.getenv("IFG","#000")
schmerp_font = os.getenv("FONT","Optima")
schmerp_fontsize = os.getenv("FONTSIZE","30")
schmerp_prefix = os.getenv("SCHMERP_PREFIX",None)
schmerp_completion_enable = os.getenv("COMPLETION","1")
schmerp_grep_notes = os.getenv("GREP_NOTES","1")
schmerp_notes_height = os.getenv("NOTES_HEIGHT",10)
try:
  with open(os.path.expanduser(schmerp_notes_fn)) as f:
    schmerp_notes = f.read()
except Exception:
  schmperp_notes = None
try:
  schmerp_fontsize = int(schmerp_fontsize)
  if schmerp_fontsize < 10 or schmerp_fontsize > 40:
    raise ValueError()
except ValueError:
  print("Invalid FONTSIZE",schmperp_fontsize)
  exit(1)
try:
  schmerp_notes_height = int(schmerp_notes_height)
except ValueError:
  print("Invalid NOTES_HEIGHT")
  exit(1)
if schmerp_completion_enable.lower() in ["n","no","0"]:
  schmerp_completion_enable = False
else:
  schmerp_completion_enable = True
if schmerp_grep_notes.lower() in ["y","yes","1"]:
  schmerp_grep_notes = True
else:
  schmerp_grep_notes = False
schmerp_opts = {
      "bg": schmerp_bg,
      "fg": schmerp_fg,
      "ibg": schmerp_ibg,
      "ifg": schmerp_ifg,
      "font": schmerp_font,
      "fontsize": schmerp_fontsize,
      "label": schmerp_label_text,
      "notes": schmerp_notes,
      "grep_notes": schmerp_grep_notes,
      "completion_enable": schmerp_completion_enable,
      "notes_height": schmerp_notes_height
    }

if __name__ == "__main__":
  main = SchmerpMain(delegate=DoChromeAlias(prefix=schmerp_prefix),opts=schmerp_opts)
  main()
  exit()
