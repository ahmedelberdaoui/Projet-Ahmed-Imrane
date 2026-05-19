#Ahmedelberdaoui
import customtkinter as ctk
import json, os, uuid, hashlib, time, random, string
import threading, subprocess, socket, struct, wave, tempfile, shutil, sys
import re as _re
from datetime import datetime as dt

try:    import cv2;                    CV2 = True
except: CV2 = False
try:    from PIL import Image, ImageTk; PIL = True
except: PIL = False
try:    import speech_recognition as sr; SR = True
except: SR = False
try:    import pyaudio;                  PA = True
except: PA = False

# ── Logo intégré en base64 (pas besoin de logo.png externe) ──────────────────
LOGO_B64 = "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"


# ── Python réel (fonctionne aussi dans un .exe PyInstaller) ──────────────────
def _get_python():
    """Retourne le chemin vers python.exe réel, même dans un .exe PyInstaller."""
    import shutil
    # Si on est dans un .exe PyInstaller, sys.executable = ChatCode.exe
    # On cherche python dans le PATH
    if getattr(sys, 'frozen', False):
        # App compilée — chercher python dans le PATH
        for name in ("python", "python3", "python.exe", "python3.exe"):
            p = shutil.which(name)
            if p:
                return p
        # Fallback: essayer depuis le dossier de l'exe
        import os
        base = os.path.dirname(sys.executable)
        for name in ("python.exe", "python3.exe", "python"):
            candidate = os.path.join(base, name)
            if os.path.exists(candidate):
                return candidate
        return "python"  # dernière chance
    else:
        return sys.executable  # mode développement normal

PYTHON_EXE = _get_python()


BD  = "#1e1e1e"
BP  = "#252526"
BH  = "#1a1a1a"
BT  = "#0d0d0d"

MAX_ATT  = 5
INACT    = 5 * 60 * 1000
CHOST, CPORT = "127.0.0.1", 55123


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH utils
# ═══════════════════════════════════════════════════════════════════════════════
def hp(p):  return hashlib.sha256(p.encode()).hexdigest()
def ve(e):  return bool(_re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", e))
def ps(pwd):
    s = sum([len(pwd)>=8, bool(_re.search(r"[A-Z]",pwd)),
             bool(_re.search(r"\d",pwd)), bool(_re.search(r"[^a-zA-Z0-9]",pwd))])
    return s, ["Très faible","Faible","Moyen","Fort","Très fort"][s]
def lu():
    if os.path.exists("users.json"):
        with open("users.json") as f: return json.load(f)
    return []
def su(u):
    with open("users.json","w") as f: json.dump(u, f, indent=2)
def ls():
    if os.path.exists("session.json"):
        with open("session.json") as f: return json.load(f)
    return {}
def ss(u):
    with open("session.json","w") as f: json.dump({"username":u}, f)
def cs():
    if os.path.exists("session.json"): os.remove("session.json")
def rl(un):
    users = lu()
    for u in users:
        if u["username"] == un:
            h = u.get("login_history", [])
            h.append(dt.now().strftime("%d/%m/%Y %H:%M"))
            u["login_history"] = h[-5:]
            break
    su(users)


# ═══════════════════════════════════════════════════════════════════════════════
# AMIS
# ═══════════════════════════════════════════════════════════════════════════════
def lf():
    if os.path.exists("friends.json"):
        with open("friends.json") as f: return json.load(f)
    return {}
def sf(d):
    with open("friends.json","w") as f: json.dump(d, f, indent=2)
def _ef(d, u):
    if u not in d: d[u] = {"friends":[], "requests_in":[], "requests_out":[]}
def gf(u):  return lf().get(u, {}).get("friends", [])
def gri(u): return lf().get(u, {}).get("requests_in", [])
def gro(u): return lf().get(u, {}).get("requests_out", [])
def sfr(src, dst):
    d = lf(); _ef(d,src); _ef(d,dst)
    if dst in d[src]["friends"]:      return "already_friends"
    if dst in d[src]["requests_out"]: return "already_sent"
    if dst in d[src]["requests_in"]:  return "already_received"
    d[src]["requests_out"].append(dst); d[dst]["requests_in"].append(src)
    sf(d); return "sent"
def afr(me, frm):
    d = lf(); _ef(d,me); _ef(d,frm)
    for lst,usr in [(d[me]["requests_in"],frm),(d[frm]["requests_out"],me)]:
        if usr in lst: lst.remove(usr)
    for a,b in [(me,frm),(frm,me)]:
        if b not in d[a]["friends"]: d[a]["friends"].append(b)
    sf(d)
def rfr(me, frm):
    d = lf(); _ef(d,me); _ef(d,frm)
    for lst,usr in [(d[me]["requests_in"],frm),(d[frm]["requests_out"],me)]:
        if usr in lst: lst.remove(usr)
    sf(d)
def rmf(me, other):
    d = lf()
    for a,b in [(me,other),(other,me)]:
        _ef(d,a)
        if b in d[a]["friends"]: d[a]["friends"].remove(b)
    sf(d)


# ═══════════════════════════════════════════════════════════════════════════════
# CHAT SERVER
# ═══════════════════════════════════════════════════════════════════════════════
class ChatServer:
    def __init__(self):
        self._cl=[]; self._lk=threading.Lock(); self._sk=None; self._run=False
    def start(self):
        try:
            self._sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sk.bind((CHOST,CPORT)); self._sk.listen(20); self._run=True
            threading.Thread(target=self._acc, daemon=True).start()
        except OSError: pass
    def _acc(self):
        while self._run:
            try:
                c,_ = self._sk.accept()
                with self._lk: self._cl.append(c)
                threading.Thread(target=self._cli, args=(c,), daemon=True).start()
            except: break
    def _cli(self, conn):
        try:
            while True:
                raw = self._rv(conn)
                if raw is None: break
                with self._lk:
                    dead = []
                    for c in self._cl:
                        try: self._sd(c, raw)
                        except: dead.append(c)
                    for d in dead: self._cl.remove(d)
        finally:
            with self._lk:
                if conn in self._cl: self._cl.remove(conn)
            conn.close()
    @staticmethod
    def _sd(s,data): s.sendall(struct.pack(">I",len(data))+data)
    @staticmethod
    def _rv(s):
        h = ChatServer._rn(s,4)
        if not h: return None
        return ChatServer._rn(s, struct.unpack(">I",h)[0])
    @staticmethod
    def _rn(s,n):
        d = b""
        while len(d)<n:
            c = s.recv(n-len(d))
            if not c: return None
            d += c
        return d

_srv = ChatServer()
_srv.start()


# ═══════════════════════════════════════════════════════════════════════════════
# COLORATION SYNTAXIQUE
# ═══════════════════════════════════════════════════════════════════════════════
LANGS = ["Auto-detect","Python","JavaScript","TypeScript","HTML","CSS","SCSS",
         "SQL","JSON","YAML","XML","Bash","C","C++","C#","Java","Go","Rust",
         "PHP","Ruby","Swift","Kotlin","R","MATLAB","Lua","Perl","Autre"]
EXT2L = {".py":"Python",".js":"JavaScript",".ts":"TypeScript",
         ".html":"HTML",".htm":"HTML",".css":"CSS",".scss":"SCSS",
         ".sql":"SQL",".json":"JSON",".yaml":"YAML",".yml":"YAML",
         ".xml":"XML",".sh":"Bash",".bash":"Bash",".c":"C",".h":"C",
         ".cpp":"C++",".cc":"C++",".cs":"C#",".java":"Java",".go":"Go",
         ".rs":"Rust",".php":"PHP",".rb":"Ruby",".swift":"Swift",
         ".kt":"Kotlin",".r":"R",".m":"MATLAB",".lua":"Lua",".pl":"Perl"}
SH = {"kw":"#569cd6","bi":"#4ec9b0","st":"#ce9178","cm":"#6a9955","nm":"#b5cea8",
      "dc":"#dcdcaa","fn":"#dcdcaa","cn":"#4ec9b0","tg":"#4ec9b0","at":"#9cdcfe",
      "sl":"#d7ba7d","pr":"#9cdcfe","oa":"#f08080","oc":"#d8a0df","ol":"#569cd6",
      "os":"#c586c0","ow":"#4ec9b0","br":"#ffd700","bs":"#da70d6","bc":"#179fff"}
_OPS = [("oa",r"\*\*|//|[+\-*/%]"),("oc",r"==|!=|<=|>="),
        ("ol",r"&&|\|\||\b(and|or|not)\b"),
        ("os",r"(?<![=!<>])=(?!=)|\+=|-=|\*=|/="),
        ("ow",r"=>|->|::"),("br",r"[()]"),("bs",r"[\[\]]"),("bc",r"[{}]")]
RULES = {}
RULES["Python"] = [
    ("cm",r"#[^\n]*"),
    ("st",r'"""[\s\S]*?"""|'+"'''"r'[\s\S]*?'+"'''"+r'|"(?:[^"\\]|\\.)*"|'r"'(?:[^'\\]|\\.)*'"),
    ("dc",r"@\w+"),("nm",r"\b(0x[0-9a-fA-F]+|\d+\.?\d*)\b"),
    ("kw",r"\b(False|None|True|and|as|assert|async|await|break|class|continue|def|del"
          r"|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal"
          r"|not|or|pass|raise|return|try|while|with|yield)\b"),
    ("bi",r"\b(abs|all|any|bool|bytes|dict|dir|enumerate|eval|exec|filter|float|format"
          r"|getattr|hasattr|hash|input|int|isinstance|iter|len|list|locals|map|max|min"
          r"|next|object|open|ord|pow|print|range|repr|reversed|round|set|setattr"
          r"|sorted|str|sum|super|tuple|type|vars|zip)\b"),
    ("fn",r"\bdef\s+(\w+)"),("cn",r"\bclass\s+(\w+)"),
] + _OPS
RULES["JavaScript"] = [
    ("cm",r"//[^\n]*|/\*[\s\S]*?\*/"),
    ("st",r'`[^`]*`|"(?:[^"\\]|\\.)*"|'r"'(?:[^'\\]|\\.)*'"),
    ("nm",r"\b(0x[0-9a-fA-F]+|\d+\.?\d*)\b"),
    ("kw",r"\b(async|await|break|case|catch|class|const|continue|default|delete|do|else"
          r"|export|extends|finally|for|from|function|if|import|in|instanceof|let|new|of"
          r"|return|static|super|switch|this|throw|try|typeof|var|void|while|yield"
          r"|null|undefined|true|false)\b"),
    ("bi",r"\b(console|Math|JSON|Object|Array|String|Number|Boolean|Date|Promise|Map|Set"
          r"|window|document|fetch|setTimeout|setInterval|clearTimeout|clearInterval)\b"),
    ("fn",r"\bfunction\s+(\w+)"),
] + _OPS
RULES["HTML"] = [("cm",r"<!--[\s\S]*?-->"),("st",r'"[^"]*"'),
    ("tg",r"</?[a-zA-Z][a-zA-Z0-9]*|/?>"),("at",r"\b[a-zA-Z][a-zA-Z0-9-]*(?=\s*=)"),
    ("nm",r"\b\d+\b"),] + _OPS
RULES["CSS"]  = [("cm",r"/\*[\s\S]*?\*/"),("st",r'"[^"]*"'),
    ("sl",r"[.#]?[a-zA-Z][a-zA-Z0-9_-]*(?=\s*\{)"),("pr",r"[a-zA-Z-]+(?=\s*:)"),
    ("nm",r"\b\d+\.?\d*(px|em|rem|%|vh|vw|pt|s|ms)?\b"),] + _OPS
RULES["SQL"]  = [("cm",r"--[^\n]*|/\*[\s\S]*?\*/"),("st",r"'[^']*'"),
    ("kw",r"\b(SELECT|FROM|WHERE|INSERT|INTO|UPDATE|SET|DELETE|CREATE|DROP|ALTER|TABLE"
          r"|JOIN|LEFT|RIGHT|INNER|ON|AS|AND|OR|NOT|IN|IS|NULL|LIKE|ORDER|BY|GROUP"
          r"|HAVING|LIMIT|DISTINCT|COUNT|SUM|AVG|MAX|MIN|UNION|CASE|WHEN|THEN|ELSE"
          r"|END|VALUES|PRIMARY|KEY)\b"),
    ("nm",r"\b\d+\.?\d*\b"),] + _OPS
RULES["JSON"] = [("st",r'"(?:[^"\\]|\\.)*"'),("nm",r"-?\b\d+\.?\d*([eE][+-]?\d+)?\b"),
    ("kw",r"\b(true|false|null)\b")]
RULES["Bash"] = [("cm",r"#[^\n]*"),("st",r'"(?:[^"\\]|\\.)*"'),
    ("kw",r"\b(if|then|else|elif|fi|for|while|do|done|case|esac|function|return|exit"
          r"|in|echo|export|local|source)\b"),
    ("bi",r"\b(cd|ls|pwd|mkdir|rm|cp|mv|cat|grep|sed|awk|find|chmod|curl|wget|git"
          r"|python|python3|pip|npm|node|bash|sh)\b"),
    ("nm",r"\b\d+\b"),] + _OPS
_CKW = (r"\b(break|case|catch|class|const|continue|default|do|else|enum|extern|false"
        r"|final|finally|for|if|inline|namespace|new|nullptr|operator|override|private"
        r"|protected|public|return|sizeof|static|struct|switch|this|throw|true|try"
        r"|typedef|using|virtual|void|volatile|while)\b")
_CBI = (r"\b(string|int|float|double|bool|char|long|short|byte|uint|fmt|os|System"
        r"|Console|ArrayList|HashMap|print|println|printf|sprintf)\b")
_CBASE = [("cm",r"//[^\n]*|/\*[\s\S]*?\*/"),("st",r'"(?:[^"\\]|\\.)*"'),
          ("nm",r"\b(0x[0-9a-fA-F]+|\d+\.?\d*)\b"),("kw",_CKW),("bi",_CBI)] + _OPS
for _l in ("C","C++","C#","Java","Go","Rust","PHP","Ruby","Swift","Kotlin",
           "TypeScript","R","MATLAB","Lua","Perl","SCSS","YAML","XML","Autre"):
    RULES[_l] = _CBASE[:]
RULES["Auto-detect"] = _CBASE[:]

def dlang(code):
    f = code.strip()[:300]
    if f.startswith("<?php"):   return "PHP"
    if f.startswith("<?xml") or "<!DOCTYPE" in f[:50] or f.startswith("<html"): return "HTML"
    if _re.search(r"^\s*(import\s+\w|from\s+\w+\s+import)", f, _re.M): return "Python"
    if _re.search(r"^\s*(const|let|var|function)", f, _re.M):           return "JavaScript"
    if _re.search(r"^\s*(SELECT|INSERT|UPDATE)\s", f, _re.M|_re.I):     return "SQL"
    if f.strip().startswith("{") or f.strip().startswith("["):           return "JSON"
    if _re.search(r"\bpackage\s+main\b|\bfunc\s+\w+", f):               return "Go"
    if _re.search(r"\bfn\s+\w+|\blet\s+mut\b", f):                      return "Rust"
    if _re.search(r"^#!/", f):                                           return "Bash"
    if _re.search(r"#include|std::", f):                                 return "C++"
    return "Autre"

class HL:
    def __init__(self, tb, lv):
        self.tb=tb; self.lv=lv; self._t=tb._textbox; self._j=None
        for n,c in SH.items(): self._t.tag_configure(n, foreground=c)
    def sched(self, _=None):
        if self._j: self._t.after_cancel(self._j)
        self._j = self._t.after(80, self.apply)
    def apply(self, *_):
        self._j = None; lang = self.lv.get()
        if lang == "Auto-detect": lang = dlang(self._t.get("1.0","end-1c"))
        rules = RULES.get(lang, RULES["Autre"]); code = self._t.get("1.0","end-1c")
        for tag in SH: self._t.tag_remove(tag,"1.0","end")
        fl = _re.MULTILINE | (_re.IGNORECASE if lang=="SQL" else 0)
        for tn,pat in rules:
            try:
                for m in _re.finditer(pat, code, fl):
                    s,e = (m.start(1),m.end(1)) if tn in ("fn","cn") and m.lastindex else (m.start(),m.end())
                    self._t.tag_add(tn, f"1.0+{s}c", f"1.0+{e}c")
            except: pass


# ═══════════════════════════════════════════════════════════════════════════════
# TERMINAL INTERACTIF — style VS Code
# Texte écrit directement dans le terminal, input protégé, pip en temps réel
# ═══════════════════════════════════════════════════════════════════════════════
class VSTerminal(ctk.CTkFrame):
    """Terminal interactif — vrai tk.Text natif. Ecriture directe comme VS Code."""
    PROMPT = "❯ "

    def __init__(self, master, **kw):
        super().__init__(master, fg_color=BT, **kw)
        self._hist       = []
        self._hi         = 0
        self._proc       = None
        self._running    = False
        self._timer_id   = None
        self._exec_start = 0.0
        self._build()

    def _build(self):
        import tkinter as tk
        import tkinter.font as tkfont

        # Header
        hdr = ctk.CTkFrame(self, fg_color="#252526", height=32)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tab = ctk.CTkFrame(hdr, fg_color="#1e1e1e", corner_radius=0)
        tab.pack(side="left", padx=(6,0), pady=4, ipadx=4)
        ctk.CTkLabel(tab, text="TERMINAL", font=("Consolas",11,"bold"),
                     text_color="#ccc").pack(side="left", padx=(10,6), pady=3)
        self._kill_btn = ctk.CTkButton(hdr, text="⏹", width=28, height=22,
            fg_color="transparent", hover_color="#3c3c3c",
            font=("Consolas",13), command=self._kill, state="disabled")
        self._kill_btn.pack(side="right", padx=2, pady=4)
        ctk.CTkButton(hdr, text="🗑", width=28, height=22, fg_color="transparent",
            hover_color="#3c3c3c", font=("Consolas",11),
            command=self._do_clear).pack(side="right", padx=2, pady=4)
        ctk.CTkButton(hdr, text="＋", width=28, height=22, fg_color="transparent",
            hover_color="#3c3c3c", font=("Consolas",13),
            command=self._new_terminal).pack(side="right", padx=2, pady=4)

        # Resize handle
        drag = ctk.CTkFrame(self, fg_color="#2a2a2a", height=5, cursor="sb_v_double_arrow")
        drag.pack(fill="x")
        _d = {"y":0,"h":220}
        def _dp(e): _d["y"]=e.y_root; _d["h"]=self.winfo_height()
        def _dm(e): self.configure(height=max(80,min(600,_d["h"]+(_d["y"]-e.y_root))))
        drag.bind("<ButtonPress-1>",_dp); drag.bind("<B1-Motion>",_dm)

        # Scrollbar + vrai tk.Text natif
        wrap = ctk.CTkFrame(self, fg_color=BT)
        wrap.pack(fill="both", expand=True)
        sb = tk.Scrollbar(wrap, bg="#252526", troughcolor="#1e1e1e",
                          activebackground="#3c3c3c", bd=0, width=12)
        sb.pack(side="right", fill="y")
        font_t = tkfont.Font(family="Consolas", size=12)
        font_b = tkfont.Font(family="Consolas", size=12, weight="bold")

        # ✅ vrai tk.Text — pas de CTkTextbox — curseur visible, frappe directe
        self._t = tk.Text(wrap, bg=BT, fg="#cccccc",
                          insertbackground="#ffffff",
                          font=font_t, wrap="char", bd=0, relief="flat",
                          undo=False, yscrollcommand=sb.set, padx=8, pady=4)
        self._t.pack(side="left", fill="both", expand=True)
        sb.config(command=self._t.yview)

        # Tags couleurs
        cols = {"default":"#cccccc","ok":"#4ec9b0","err":"#f44747","warn":"#ffaa44",
                "inf":"#569cd6","path":"#6a9955","pip":"#ce9178","dim":"#555555"}
        for n,c in cols.items():
            self._t.tag_configure(n, foreground=c, font=font_t)
        self._t.tag_configure("prompt", foreground="#569cd6", font=font_b)
        self._t.tag_configure("cmd",    foreground="#ffffff",  font=font_b)

        # Barre de statut
        sb2 = ctk.CTkFrame(self, fg_color="#007acc", height=22)
        sb2.pack(fill="x", side="bottom"); sb2.pack_propagate(False)
        self._sb_left = ctk.CTkLabel(sb2, text="ChatCode Terminal",
                                     font=("Consolas",10,"bold"), text_color="#fff")
        self._sb_left.pack(side="left", padx=10)
        self._sb_time = ctk.CTkLabel(sb2, text="", font=("Consolas",10), text_color="#fff")
        self._sb_time.pack(side="left", padx=6)
        ctk.CTkLabel(sb2, text=f"Python {sys.version.split()[0]}  UTF-8",
                     font=("Consolas",10), text_color="#fff").pack(side="right", padx=10)

        # Bindings
        self._t.bind("<Return>",          self._on_enter)
        self._t.bind("<BackSpace>",       self._on_backspace)
        self._t.bind("<Delete>",          self._on_delete)
        self._t.bind("<Up>",              self._hist_up)
        self._t.bind("<Down>",            self._hist_down)
        self._t.bind("<Control-c>",       self._on_ctrl_c)
        self._t.bind("<Control-l>",       lambda e: (self._do_clear(), "break")[1])
        self._t.bind("<Home>",            self._on_home)
        self._t.bind("<ButtonRelease-1>", self._clamp_cursor)
        self._t.bind("<Key>",             self._on_any_key)

        # Welcome
        self._write("ChatCode Terminal\n", "inf")
        self._write(f"Python {sys.version.split()[0]}  —  {os.getcwd()}\n", "path")
        self._write("Ctrl+C interrompre  ·  Ctrl+L effacer\n\n", "dim")
        self._new_prompt()
        self._t.focus_set()

    def _write(self, text, tag="default"):
        self._t.insert("end", text, tag)
        self._t.see("end")

    def _new_prompt(self):
        cwd = os.path.basename(os.getcwd()) or os.getcwd()
        self._write(f"\n{cwd} ", "path")
        self._write(self.PROMPT, "prompt")
        self._t.mark_set("input_start", "end-1c")
        self._t.mark_gravity("input_start", "left")
        self._t.see("end")

    def _do_clear(self):
        self._t.delete("1.0", "end")
        self._new_prompt()

    def _new_terminal(self):
        self._do_clear()
        self._write(f"Nouveau terminal — {os.getcwd()}\n", "inf")
        self._new_prompt()

    def _in_input(self):
        try: return self._t.compare("insert", ">=", "input_start")
        except: return False

    def _clamp_cursor(self, _=None):
        try:
            if not self._in_input():
                self._t.mark_set("insert", "end")
        except: pass

    def _on_home(self, event):
        self._t.mark_set("insert", "input_start")
        return "break"

    def _on_backspace(self, event):
        try:
            if self._t.compare("insert", "<=", "input_start"):
                return "break"
        except: pass

    def _on_delete(self, event):
        try:
            if self._t.compare("insert", "<", "input_start"):
                return "break"
        except: pass

    def _on_any_key(self, event):
        # Laisser passer Ctrl/Alt et touches spéciales
        if event.state & 0x4 or event.state & 0x8: return
        if event.keysym in ("Up","Down","Left","Right","Home","End","Return",
                             "BackSpace","Delete","Shift_L","Shift_R",
                             "Control_L","Control_R","Alt_L","Alt_R",
                             "Escape","Tab","Prior","Next"): return
        # Si hors zone input → ramener le curseur à la fin avant la frappe
        if not self._in_input():
            self._t.mark_set("insert", "end")

    def _on_ctrl_c(self, event):
        self._kill()
        self._write("^C\n", "err")
        self._new_prompt()
        return "break"

    def _hist_up(self, event):
        if not self._hist: return "break"
        self._hi = max(0, self._hi-1)
        self._replace_input(self._hist[self._hi])
        return "break"

    def _hist_down(self, event):
        if self._hi >= len(self._hist)-1:
            self._hi = len(self._hist); self._replace_input("")
        else:
            self._hi += 1; self._replace_input(self._hist[self._hi])
        return "break"

    def _replace_input(self, text):
        try:
            self._t.delete("input_start", "end")
            self._t.insert("end", text, "cmd")
            self._t.see("end")
        except: pass

    def _get_input(self):
        try: return self._t.get("input_start", "end-1c").strip()
        except: return ""

    def _on_enter(self, event):
        cmd = self._get_input()
        try: self._t.tag_add("cmd", "input_start", "end-1c")
        except: pass
        self._write("\n")
        if cmd:
            self._hist.append(cmd); self._hi = len(self._hist)
            self._run_cmd(cmd)
        else:
            self._new_prompt()
        return "break"

    def _run_cmd(self, cmd):
        if cmd in ("cls","clear"): self._do_clear(); return
        if cmd == "pwd": self._write(os.getcwd()+"\n","path"); self._new_prompt(); return
        if cmd.startswith("cd "):
            try:
                os.chdir(cmd[3:].strip())
                self._write(f"→ {os.getcwd()}\n","path")
            except Exception as ex:
                self._write(f"Erreur: {ex}\n","err")
            self._new_prompt(); return
        if cmd == "help":
            self._write(
                "  cls/clear           effacer\n"
                "  pwd                 répertoire courant\n"
                "  cd <dir>            changer de dossier\n"
                "  pip install <pkg>   installer un paquet\n"
                "  pip list            paquets installés\n"
                "  pip uninstall <pkg> désinstaller\n"
                "  python -c \"...\"    exécuter Python\n"
                "  Ctrl+C              interrompre\n"
                "  Ctrl+L              effacer l'écran\n","inf")
            self._new_prompt(); return

        is_pip = cmd.strip().startswith("pip")
        if is_pip:
            actual = [PYTHON_EXE, "-m"] + cmd.split()
            self._write(f"📦 {cmd}\n","pip")
        else:
            actual = cmd if os.name=="nt" else ["bash","-c",cmd]

        self._running=True; self._exec_start=time.time()
        self._kill_btn.configure(state="normal")
        self._sb_left.configure(text="▶ En cours…")
        self._start_timer()

        def _thread():
            try:
                self._proc = subprocess.Popen(
                    actual, shell=(not is_pip and os.name=="nt"),
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace",
                    bufsize=1, cwd=os.getcwd())
                for line in self._proc.stdout:
                    if not self._running: break
                    ls = line.rstrip("\n")
                    t = ("ok"   if _re.search(r"Successfully installed",ls,_re.I) else
                         "warn" if _re.search(r"already satisfied",ls,_re.I) else
                         "err"  if _re.search(r"error|failed",ls,_re.I) else
                         "pip"  if is_pip and _re.search(r"Downloading|Installing|Collecting|Preparing|Building",ls,_re.I) else
                         "err"  if _re.search(r"\berror\b|\bexception\b|\btraceback\b|\bfailed\b",ls,_re.I) else
                         "warn" if _re.search(r"\bwarning\b",ls,_re.I) else "default")
                    self.after(0, lambda l=ls,tg=t: self._write(l+"\n",tg))
                self._proc.wait(); rc=self._proc.returncode
            except FileNotFoundError:
                rc=127; self.after(0,lambda:self._write(f"Commande introuvable : '{cmd.split()[0]}'\n","err"))
            except Exception as ex:
                rc=1; self.after(0,lambda:self._write(f"Erreur: {ex}\n","err"))
            finally:
                elapsed=time.time()-self._exec_start
                def _done():
                    self._running=False; self._proc=None
                    self._stop_timer(); self._kill_btn.configure(state="disabled")
                    sym="✓" if rc==0 else "✗"
                    self._write(f"\n{sym} {elapsed:.2f}s  [exit {rc}]\n","ok" if rc==0 else "err")
                    self._sb_left.configure(text=f"{sym} {elapsed:.2f}s")
                    self._sb_time.configure(text="")
                    self._new_prompt()
                self.after(0,_done)
        threading.Thread(target=_thread, daemon=True).start()

    def _kill(self):
        if self._proc:
            try:
                self._proc.terminate()
                self.after(500, lambda: self._proc.kill() if self._proc else None)
            except: pass
        self._running=False

    def _start_timer(self):
        self._stop_timer(); self._tick()

    def _tick(self):
        if not self._running: return
        self._sb_time.configure(text=f"⏱ {time.time()-self._exec_start:.1f}s")
        self._timer_id=self.after(100,self._tick)

    def _stop_timer(self):
        if self._timer_id:
            try: self.after_cancel(self._timer_id)
            except: pass
            self._timer_id=None

    def print(self, text, tag="default"):
        self._write(text, tag)

    def clear(self):
        self._do_clear()


def make_editor(master):
    frame = ctk.CTkFrame(master, fg_color=BD)
    frame.pack(fill="both", expand=True)

    # ── Onglet ────────────────────────────────────────────────────────────────
    tab_bar = ctk.CTkFrame(frame, fg_color="#252526", height=35)
    tab_bar.pack(fill="x"); tab_bar.pack_propagate(False)
    tab_label = ctk.CTkLabel(tab_bar, text="  📄 untitled  ×",
                             font=("Consolas",12), text_color="#ccc",
                             fg_color="#1e1e1e", corner_radius=0)
    tab_label.pack(side="left", ipady=6, ipadx=6)

    # ── Toolbar ───────────────────────────────────────────────────────────────
    toolbar = ctk.CTkFrame(frame, fg_color="#2d2d2d", height=34)
    toolbar.pack(fill="x"); toolbar.pack_propagate(False)

    lv = ctk.StringVar(value="Python")
    lm = ctk.CTkOptionMenu(toolbar, values=LANGS, variable=lv, width=132, height=26,
                           fg_color="#3c3c3c", button_color="#3c3c3c",
                           button_hover_color="#505050", font=("Consolas",11),
                           command=lambda _: hl.apply())
    lm.pack(side="left", padx=6, pady=4)

    st = ctk.CTkLabel(toolbar, text="", font=("Consolas",11), text_color="#aaa")

    BC = dict(height=26, fg_color="#3c3c3c", hover_color="#505050",
              font=("Consolas",11), corner_radius=4)

    RUNNERS = {
        "Python":     ([PYTHON_EXE,"-c","__CODE__"], False, ".py"),
        "JavaScript": (["node","-e","__CODE__"],          False, ".js"),
        "TypeScript": (["ts-node","-e","__CODE__"],       False, ".ts"),
        "Bash":       (["bash","-c","__CODE__"],          False, ".sh"),
        "Ruby":       (["ruby","-e","__CODE__"],          False, ".rb"),
        "Perl":       (["perl","-e","__CODE__"],          False, ".pl"),
        "PHP":        (["php","-r","__CODE__"],           False, ".php"),
        "Lua":        (["lua","__FILE__"],                True,  ".lua"),
        "R":          (["Rscript","__FILE__"],            True,  ".r"),
        "Go":         (["go","run","__FILE__"],           True,  ".go"),
        "C":          (["gcc","__FILE__","-o","__EXE__"], True,  ".c"),
        "C++":        (["g++","__FILE__","-o","__EXE__"], True,  ".cpp"),
        "Rust":       (["rustc","__FILE__","-o","__EXE__"],True, ".rs"),
        "C#":         (["dotnet-script","__FILE__"],      True,  ".cs"),
        "Swift":      (["swift","__FILE__"],              True,  ".swift"),
        "Kotlin":     (["kotlinc-jvm","-script","__FILE__"],True,".kts"),
        "Java":       (["javac","__FILE__"],              True,  ".java"),
    }

    # Terminal ref (assigné plus bas)
    _term = {"ref": None}

    def run():
        code = ed.get("1.0","end-1c"); lang = lv.get()
        if lang == "Auto-detect": lang = dlang(code)
        if not _term["ref"]: return
        term = _term["ref"]
        st.configure(text=f"  ▶ {lang}…", text_color="#ffaa44")

        def _run_thread():
            entry = RUNNERS.get(lang)
            if not entry:
                frame.after(0, lambda: term.print(f"ℹ '{lang}' ne s'exécute pas ici.\n","inf"))
                frame.after(0, lambda: st.configure(text=f"ℹ {lang}", text_color="#888"))
                return
            tpl, uf, ext = entry
            td = tempfile.mkdtemp()
            try:
                tmp = os.path.join(td, f"code{ext}")
                exe = os.path.join(td, "out.exe" if os.name=="nt" else "out")
                with open(tmp,"w",encoding="utf-8") as f2: f2.write(code)
                def bld(t):
                    return [c.replace("__CODE__",code).replace("__FILE__",tmp)
                              .replace("__EXE__",exe) for c in t]

                frame.after(0, lambda: term._write(f"$ run {lang}\n","cmd"))
                t0 = time.time()

                if not uf:
                    cmd_list = bld(tpl)
                    proc = subprocess.Popen(cmd_list, stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT,
                                            text=True, encoding="utf-8", errors="replace")
                elif lang in ("C","C++","Rust"):
                    proc = subprocess.Popen(bld(tpl), stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT,
                                            text=True, encoding="utf-8", errors="replace")
                    co = proc.stdout.read(); proc.wait()
                    if proc.returncode != 0:
                        frame.after(0, lambda: term._write(f"Erreur compilation:\n{co}\n","err"))
                        frame.after(0, lambda: st.configure(text="  ✗ Erreur", text_color="#f44747"))
                        return
                    proc = subprocess.Popen([exe], stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT,
                                            text=True, encoding="utf-8", errors="replace")
                elif lang == "Java":
                    proc = subprocess.Popen(["javac", tmp], stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT,
                                            text=True, encoding="utf-8", errors="replace")
                    co = proc.stdout.read(); proc.wait()
                    if proc.returncode != 0:
                        frame.after(0, lambda: term._write(f"Erreur compilation:\n{co}\n","err"))
                        return
                    m2 = _re.search(r"public\s+class\s+(\w+)", code)
                    cn = m2.group(1) if m2 else "code"
                    proc = subprocess.Popen(["java","-cp",td,cn], stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT,
                                            text=True, encoding="utf-8", errors="replace")
                else:
                    proc = subprocess.Popen(bld(tpl), stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT,
                                            text=True, encoding="utf-8", errors="replace")

                for line in proc.stdout:
                    ls = line.rstrip("\n")
                    tag = ("err"  if _re.search(r"error|exception|traceback",ls,_re.I)
                           else "warn" if _re.search(r"warning",ls,_re.I) else "default")
                    frame.after(0, lambda l=ls, t=tag: term._write(l+"\n", t))
                proc.wait(); rc = proc.returncode
                elapsed = time.time() - t0
                ok = rc == 0
                def _fin():
                    symbol = "✓" if ok else "✗"
                    term._write(f"\n{symbol} {elapsed:.2f}s  [exit {rc}]\n",
                                "ok" if ok else "err")
                    st.configure(text=f"  {symbol} {elapsed:.2f}s",
                                 text_color="#44ee88" if ok else "#f44747")
                    term._new_prompt()
                frame.after(0, _fin)
            finally:
                shutil.rmtree(td, ignore_errors=True)

        threading.Thread(target=_run_thread, daemon=True).start()

    def clear_ed():
        ed.delete("1.0","end")
        if _term["ref"]: _term["ref"].clear()
        st.configure(text=""); _upln()
    def copy_ed():
        frame.clipboard_clear(); frame.clipboard_append(ed.get("1.0","end-1c"))
        st.configure(text="  ✓ Copié", text_color="#44ee88")
        frame.after(2000, lambda: st.configure(text=""))
    def save_ed():
        import tkinter.filedialog as fd
        em = {"Python":".py","JavaScript":".js","TypeScript":".ts","HTML":".html",
              "CSS":".css","SQL":".sql","JSON":".json","Bash":".sh",
              "C":".c","C++":".cpp","C#":".cs","Java":".java","Go":".go","Rust":".rs"}
        ext = em.get(lv.get(),".txt")
        path = fd.asksaveasfilename(defaultextension=ext,
                                    filetypes=[(lv.get(),f"*{ext}"),("Tous","*.*")])
        if path:
            with open(path,"w",encoding="utf-8") as f2: f2.write(ed.get("1.0","end-1c"))
            st.configure(text="  ✓ Sauvegardé", text_color="#44ee88")
            tab_label.configure(text=f"  📄 {os.path.basename(path)}  ×")
    def open_ed():
        import tkinter.filedialog as fd
        path = fd.askopenfilename(filetypes=[("Tous","*.*")])
        if path:
            with open(path,"r",encoding="utf-8",errors="replace") as f2: code=f2.read()
            ed.delete("1.0","end"); ed.insert("1.0",code)
            ext = os.path.splitext(path)[1].lower()
            lv.set(EXT2L.get(ext, dlang(code)))
            hl.apply(); _upln()
            tab_label.configure(text=f"  📄 {os.path.basename(path)}  ×")

    for txt, cmd2 in [("▶ Run",run),("📋 Copy",copy_ed),("💾 Save",save_ed),
                      ("📂 Open",open_ed),("🗑 Clear",clear_ed)]:
        ctk.CTkButton(toolbar, text=txt, width=74, command=cmd2, **BC).pack(
            side="left", padx=2, pady=4)
    st.pack(side="left", padx=8)

    # ── Éditeur + numéros de lignes ───────────────────────────────────────────
    ed_frame = ctk.CTkFrame(frame, fg_color="#1e1e1e")
    ed_frame.pack(fill="both", expand=True)

    ln = ctk.CTkTextbox(ed_frame, width=52, fg_color="#1e1e1e",
                        text_color="#3d3d3d", font=("Consolas",13),
                        state="disabled", corner_radius=0)
    ln.pack(side="left", fill="y")
    ctk.CTkFrame(ed_frame, width=1, fg_color="#333").pack(side="left", fill="y")
    ed = ctk.CTkTextbox(ed_frame, fg_color="#1e1e1e", text_color="#d4d4d4",
                        font=("Consolas",13), wrap="none", corner_radius=0, undo=True)
    ed.pack(side="left", fill="both", expand=True)
    ed.insert("1.0","# Écrivez votre code ici\n")
    hl = HL(ed, lv)

    def _upln(_=None):
        lines = ed.get("1.0","end-1c").split("\n")
        nums  = "\n".join(str(i+1) for i in range(len(lines)))
        ln.configure(state="normal"); ln.delete("1.0","end")
        ln.insert("1.0",nums); ln.configure(state="disabled")

    # Barre de statut éditeur
    esb = ctk.CTkFrame(frame, fg_color="#007acc", height=0)  # cachée, dans le terminal
    sb_lang = ctk.CTkLabel(esb, text="Python", font=("Consolas",10), text_color="#fff")
    sb_pos  = ctk.CTkLabel(esb, text="Ln 1, Col 1", font=("Consolas",10), text_color="#fff")

    def _ok(_=None): _upln(); hl.sched()
    def _upd_sb(_=None):
        sb_lang.configure(text=lv.get())
        try:
            idx = ed._textbox.index("insert"); r,c = idx.split(".")
            sb_pos.configure(text=f"Ln {r}, Col {int(c)+1}")
        except: pass
    ed._textbox.bind("<KeyRelease>", lambda e: (_ok(e), _upd_sb(e)))
    ed._textbox.bind("<ButtonRelease>", _upd_sb)
    lv.trace_add("write", lambda *_: _upd_sb())
    _upln(); hl.apply()

    # ── Terminal VS Code (en bas) ─────────────────────────────────────────────
    term_wrap = ctk.CTkFrame(frame, fg_color=BT)
    term_wrap.pack(fill="x", side="bottom")
    term_wrap.configure(height=220)
    term_wrap.pack_propagate(False)

    term = VSTerminal(term_wrap)
    term.pack(fill="both", expand=True)
    _term["ref"] = term

    frame.editor = ed
    return frame


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIO MESSAGE — style WhatsApp
# ═══════════════════════════════════════════════════════════════════════════════
class AudioMessage(ctk.CTkFrame):
    def __init__(self, master, audio_data: bytes, duration: float, is_me: bool, **kw):
        import tkinter as tk
        bg = "#005c4b" if is_me else "#1f2c34"
        super().__init__(master, fg_color=bg, corner_radius=12, **kw)
        self._data=audio_data; self._dur=max(duration,0.1)
        self._playing=False; self._play_t=None; self._prog=0.0; self._me=is_me
        self._bg = bg

        # Largeur fixe pour que le canvas soit visible dès le départ
        self.configure(width=260)

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(padx=10, pady=8, fill="x")

        # Bouton play
        self.pb = ctk.CTkButton(row, text="▶", width=38, height=38, corner_radius=19,
                                fg_color="#00a884", hover_color="#00c49a",
                                font=("Arial",16), command=self._toggle)
        self.pb.pack(side="left", padx=(0,6))

        # Colonne centrale
        mid = ctk.CTkFrame(row, fg_color="transparent")
        mid.pack(side="left", fill="x", expand=True)

        # ✅ tk.Canvas natif — CTkCanvas n'existe pas
        self._cvs = tk.Canvas(mid, height=34, bg=bg,
                              highlightthickness=0, bd=0)
        self._cvs.pack(fill="x", expand=True, pady=(2,0))

        # Timer + durée sur la même ligne
        bot = ctk.CTkFrame(mid, fg_color="transparent")
        bot.pack(fill="x")
        self._timer_lbl = ctk.CTkLabel(bot, text="0:00",
                                       font=("Consolas",10), text_color="#8696a0")
        self._timer_lbl.pack(side="left")
        ctk.CTkLabel(bot, text=f" / {self._fmt(self._dur)}",
                     font=("Consolas",10), text_color="#667781").pack(side="left")

        # Dessiner les barres après que le widget soit rendu
        self._cvs.bind("<Configure>", lambda e: self._draw_bars(self._prog))
        self._cvs.bind("<Button-1>",  self._seek)
        self.after(50, lambda: self._draw_bars(0))

    def _draw_bars(self, prog=0.0):
        c=self._cvs; c.delete("all")
        w=c.winfo_width(); h=c.winfo_height()
        if w < 4 or h < 4:
            self.after(30, lambda: self._draw_bars(prog)); return
        BAR_W, GAP = 3, 2
        n = max(1, w//(BAR_W+GAP))
        random.seed(id(self))   # barres stables par instance
        heights=[random.randint(4, max(5,h-4)) for _ in range(n)]
        for i,bh in enumerate(heights):
            x0=i*(BAR_W+GAP); x1=x0+BAR_W
            y0=(h-bh)//2; y1=y0+bh
            col="#00a884" if i/n<prog else ("#4a6a62" if self._me else "#3a4a44")
            c.create_rectangle(x0,y0,x1,y1,fill=col,outline="")

    def _fmt(self, sec): return f"{int(sec)//60:01d}:{int(sec)%60:02d}"

    def _seek(self, event):
        w=self._cvs.winfo_width()
        if w<1: return
        self._prog=max(0.0,min(1.0,event.x/w))
        self._draw_bars(self._prog)
        self._timer_lbl.configure(text=self._fmt(self._prog*self._dur))

    def _toggle(self):
        if self._playing: self._stop()
        else: self._play()

    def _play(self):
        if not PA:
            self._timer_lbl.configure(text="⚠ pip install pyaudio"); return
        self._playing=True
        self.pb.configure(text="⏸",fg_color="#e53935",hover_color="#c62828")
        threading.Thread(target=self._play_thread,daemon=True).start()
        self._anim()

    def _stop(self):
        self._playing=False
        self.pb.configure(text="▶",fg_color="#00a884",hover_color="#00c49a")
        if self._play_t:
            try: self.after_cancel(self._play_t)
            except: pass
            self._play_t=None

    def _play_thread(self):
        try:
            tmp=tempfile.NamedTemporaryFile(suffix=".wav",delete=False)
            tmp.write(self._data); tmp.close()
            wf=wave.open(tmp.name,"rb"); p=pyaudio.PyAudio()
            s=p.open(format=p.get_format_from_width(wf.getsampwidth()),
                     channels=wf.getnchannels(),rate=wf.getframerate(),output=True)
            start=time.time()
            while self._playing:
                chunk=wf.readframes(1024)
                if not chunk: break
                s.write(chunk)
                self._prog=min(1.0,(time.time()-start)/self._dur)
            s.stop_stream(); s.close(); p.terminate(); wf.close(); os.unlink(tmp.name)
        except Exception as ex: print(f"Audio: {ex}")
        finally:
            self.after(0, self._stop)
            self.after(0, lambda: self._draw_bars(0))
            self.after(0, lambda: self._timer_lbl.configure(text=self._fmt(0)))
            self._prog=0.0

    def _anim(self):
        if not self._playing: return
        self._draw_bars(self._prog)
        self._timer_lbl.configure(text=self._fmt(self._prog*self._dur))
        self._play_t=self.after(50,self._anim)


# ═══════════════════════════════════════════════════════════════════════════════
# ENREGISTREMENT AUDIO — style WhatsApp
# ═══════════════════════════════════════════════════════════════════════════════
class AudioRecorder(ctk.CTkFrame):
    def __init__(self, master, on_send, on_cancel, **kw):
        import tkinter as tk
        super().__init__(master, fg_color="#1f2c34", height=56, **kw)
        self.on_send=on_send; self.on_cancel=on_cancel
        self._frames=[]; self._recording=True
        self._start=time.time(); self._timer_id=None

        ctk.CTkButton(self, text="🗑", width=38, height=38, corner_radius=19,
                      fg_color="#6a1a1a", hover_color="#8a2a2a",
                      font=("Arial",16), command=self._cancel).pack(side="left",padx=8,pady=9)

        self._cvs=tk.Canvas(self,height=38,bg="#1f2c34",highlightthickness=0,bd=0)
        self._cvs.pack(side="left",fill="x",expand=True,pady=9)

        self._lbl=ctk.CTkLabel(self,text="0:00",font=("Consolas",12,"bold"),text_color="#e53935")
        self._lbl.pack(side="left",padx=6)

        self.sb=ctk.CTkButton(self,text="✓",width=38,height=38,corner_radius=19,
                              fg_color="#00a884",hover_color="#00c49a",
                              font=("Arial",18,"bold"),command=self._send)
        self.sb.pack(side="right",padx=8,pady=9)

        ctk.CTkLabel(self,text="🎙",font=("Arial",20),text_color="#e53935").pack(side="right",padx=4)

        self._anim_bars=[4]*20; self._anim_loop()
        self._update_timer()
        if PA: threading.Thread(target=self._record,daemon=True).start()

    def _record(self):
        CHUNK,RATE,CH=1024,44100,1
        p=pyaudio.PyAudio()
        s=p.open(format=pyaudio.paInt16,channels=CH,rate=RATE,
                 input=True,frames_per_buffer=CHUNK)
        while self._recording:
            try: self._frames.append(s.read(CHUNK,exception_on_overflow=False))
            except: break
        s.stop_stream(); s.close(); p.terminate()

    def _update_timer(self):
        if not self._recording: return
        elapsed=time.time()-self._start
        self._lbl.configure(text=f"{int(elapsed)//60}:{int(elapsed)%60:02d}")
        self._timer_id=self.after(500,self._update_timer)

    def _anim_loop(self):
        if not self._recording: return
        c=self._cvs; c.delete("all"); w=c.winfo_width(); h=c.winfo_height()
        if w>2:
            n=20
            for i in range(n):
                target=random.randint(3,max(4,h-4))
                self._anim_bars[i]=int(self._anim_bars[i]*0.6+target*0.4)
                bh=self._anim_bars[i]; x=int((i+0.5)*w/n); bw=max(2,w//(n*2))
                c.create_rectangle(x-bw//2,(h-bh)//2,x+bw//2,(h+bh)//2,fill="#e53935",outline="")
        self.after(60,self._anim_loop)

    def _stop_all(self):
        self._recording=False
        if self._timer_id:
            try: self.after_cancel(self._timer_id)
            except: pass

    def _send(self):
        self._stop_all(); dur=time.time()-self._start
        if not self._frames or dur<0.3: self._cancel(); return
        tmp=tempfile.NamedTemporaryFile(suffix=".wav",delete=False)
        wf=wave.open(tmp.name,"wb"); wf.setnchannels(1); wf.setsampwidth(2)
        wf.setframerate(44100); wf.writeframes(b"".join(self._frames)); wf.close()
        with open(tmp.name,"rb") as f: data=f.read()
        os.unlink(tmp.name); self.on_send(data,dur); self.destroy()

    def _cancel(self):
        self._stop_all(); self.on_cancel(); self.destroy()


# ═══════════════════════════════════════════════════════════════════════════════
# CHAT PANEL
# ═══════════════════════════════════════════════════════════════════════════════
class ChatPanel(ctk.CTkFrame):
    def __init__(self, master, username, **kw):
        super().__init__(master, fg_color=BP, **kw)
        self.un=username; self._sk=None; self._run=False

        hdr=ctk.CTkFrame(self,fg_color="#075e54",height=52)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr,text="💬",font=("Arial",20)).pack(side="left",padx=10,pady=10)
        col=ctk.CTkFrame(hdr,fg_color="transparent"); col.pack(side="left",pady=8)
        ctk.CTkLabel(col,text="Chat en direct",font=("Arial",13,"bold"),text_color="#fff").pack(anchor="w")
        self.stat=ctk.CTkLabel(col,text="● Connexion…",font=("Arial",10),text_color="#a8d8a8"); self.stat.pack(anchor="w")
        ctk.CTkButton(hdr,text="+ Ami",width=65,height=28,corner_radius=8,
                      fg_color="#128C7E",hover_color="#1aad9c",font=("Arial",11),
                      command=self._add_dlg).pack(side="right",padx=8,pady=12)

        self.msgs=ctk.CTkScrollableFrame(self,fg_color="#111b21",corner_radius=0)
        self.msgs.pack(fill="both",expand=True)

        self._inp_wrap=ctk.CTkFrame(self,fg_color="#1f2c34")
        self._inp_wrap.pack(fill="x")
        self._build_input()
        self._connect()

    def _build_input(self):
        for w in self._inp_wrap.winfo_children(): w.destroy()
        inp=ctk.CTkFrame(self._inp_wrap,fg_color="#1f2c34",height=56)
        inp.pack(fill="x"); inp.pack_propagate(False)
        self.ent=ctk.CTkEntry(inp,placeholder_text="Message…",font=("Arial",13),
                              corner_radius=20,fg_color="#2a3942",border_width=0,height=38)
        self.ent.pack(side="left",fill="x",expand=True,padx=8,pady=9)
        self.ent.bind("<Return>",lambda e:self._st())
        self.mic_btn=ctk.CTkButton(inp,text="🎤",width=38,height=38,corner_radius=19,
                                   fg_color="#3a3a3a",hover_color="#4a4a4a",font=("Arial",16),
                                   command=self._start_recording)
        self.mic_btn.pack(side="right",padx=(0,4))
        ctk.CTkButton(inp,text="➤",width=38,height=38,corner_radius=19,
                      fg_color="#00a884",hover_color="#00c49a",font=("Arial",14),
                      command=self._st).pack(side="right",padx=4)

    def _start_recording(self):
        if not PA: self._disp({"type":"system","text":"⚠ pip install pyaudio"}); return
        for w in self._inp_wrap.winfo_children(): w.destroy()
        AudioRecorder(self._inp_wrap,on_send=self._send_audio,on_cancel=self._build_input).pack(fill="x")

    def _send_audio(self,data,duration):
        self._sr({"type":"audio","user":self.un,"duration":duration,"data":list(data)})
        self._build_input()

    def _connect(self):
        def _try():
            for _ in range(15):
                try:
                    self._sk=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    self._sk.connect((CHOST,CPORT)); self._run=True
                    self.after(0,lambda:self.stat.configure(text="● En ligne",text_color="#00ff88"))
                    self._sr({"type":"system","text":f"{self.un} a rejoint","user":self.un})
                    threading.Thread(target=self._rl,daemon=True).start(); return
                except: time.sleep(0.3)
            self.after(0,lambda:self.stat.configure(text="● Hors ligne",text_color="#f44747"))
        threading.Thread(target=_try,daemon=True).start()

    def _sr(self,obj):
        try:
            if self._sk:
                d=json.dumps(obj).encode(); self._sk.sendall(struct.pack(">I",len(d))+d)
        except: pass

    def _rl(self):
        while self._run:
            try:
                h=self._rn(4)
                if not h: break
                d=self._rn(struct.unpack(">I",h)[0])
                if d: self.after(0,lambda m=json.loads(d.decode()):self._disp(m))
            except: break

    def _rn(self,n):
        d=b""
        while len(d)<n:
            c=self._sk.recv(n-len(d))
            if not c: return None
            d+=c
        return d

    def _disp(self,msg):
        mt=msg.get("type","text"); user=msg.get("user","?")
        ts=dt.now().strftime("%H:%M"); isme=(user==self.un)
        if mt=="system":
            ctk.CTkLabel(self.msgs,text=msg.get("text",""),font=("Arial",11),
                         text_color="#8696a0",fg_color="#1f2c34",corner_radius=8).pack(pady=4,padx=30)
            self._scr(); return
        row=ctk.CTkFrame(self.msgs,fg_color="transparent"); row.pack(fill="x",pady=2,padx=6)
        if mt=="text":
            bub=ctk.CTkFrame(row,fg_color="#005c4b" if isme else "#1f2c34",corner_radius=12)
            bub.pack(side="right" if isme else "left",anchor="e" if isme else "w",
                     padx=(40 if not isme else 4,4 if not isme else 40))
            if not isme:
                ctk.CTkLabel(bub,text=user,font=("Arial",11,"bold"),text_color="#00a884").pack(anchor="w",padx=10,pady=(6,0))
            ctk.CTkLabel(bub,text=msg.get("text",""),font=("Arial",13),text_color="#e9edef",
                         wraplength=200,justify="left").pack(padx=10,pady=(4,2),anchor="w")
            ctk.CTkLabel(bub,text=ts,font=("Arial",10),text_color="#667781").pack(anchor="e",padx=10,pady=(0,4))
        elif mt=="audio":
            dur=msg.get("duration",0); data=bytes(msg.get("data",[]))
            sf=ctk.CTkFrame(row,fg_color="transparent")
            sf.pack(side="right" if isme else "left",anchor="e" if isme else "w",
                    padx=(40 if not isme else 4,4 if not isme else 40))
            if not isme:
                ctk.CTkLabel(sf,text=user,font=("Arial",11,"bold"),text_color="#00a884").pack(anchor="w",padx=2)
            AudioMessage(sf,audio_data=data,duration=dur,is_me=isme).pack(fill="x",ipadx=4,ipady=2)
            ctk.CTkLabel(sf,text=ts,font=("Arial",10),text_color="#667781").pack(anchor="e",padx=6)
        self._scr()

    def _scr(self): self.after(50,lambda:self.msgs._parent_canvas.yview_moveto(1.0))
    def _st(self):
        t=self.ent.get().strip()
        if not t: return
        self.ent.delete(0,"end"); self._sr({"type":"text","user":self.un,"text":t})
    def inject(self,text): self.ent.delete(0,"end"); self.ent.insert(0,text); self._st()

    def _add_dlg(self):
        w=ctk.CTkToplevel(self); w.title("Ajouter un ami"); w.geometry("320x170"); w.grab_set()
        ctk.CTkLabel(w,text="Nom d'utilisateur :",font=("Arial",13)).pack(pady=(16,4))
        e=ctk.CTkEntry(w,width=240,font=("Arial",13)); e.pack(pady=4)
        lbl=ctk.CTkLabel(w,text="",font=("Arial",12)); lbl.pack()
        def _send():
            to2=e.get().strip()
            if not to2: return
            if not any(u["username"]==to2 for u in lu()):
                lbl.configure(text="Introuvable.",text_color="#f44747"); return
            result=sfr(self.un,to2)
            t,c={"sent":("✅ Envoyée !","#44ee88"),"already_friends":("Déjà ami.","#aaa"),
                 "already_sent":("Déjà envoyée.","#aaa"),"already_received":("Demande reçue.","#44aaee")}.get(result,("…","#aaa"))
            lbl.configure(text=t,text_color=c); w.after(2000,w.destroy)
        ctk.CTkButton(w,text="Envoyer",width=120,command=_send).pack(pady=8)
        e.bind("<Return>",lambda _:_send())

    def disconnect(self):
        self._run=False
        try:
            self._sr({"type":"system","text":f"{self.un} a quitté","user":self.un})
            self._sk.close()
        except: pass


# ═══════════════════════════════════════════════════════════════════════════════
# CAMÉRA
# ═══════════════════════════════════════════════════════════════════════════════
class CamPanel(ctk.CTkFrame):
    def __init__(self,master,on_photo=None,on_close=None,**kw):
        super().__init__(master,fg_color=BP,**kw)
        self.on_photo=on_photo; self.on_close=on_close; self._run=False; self._cap=None
        hdr=ctk.CTkFrame(self,fg_color=BH); hdr.pack(fill="x")
        ctk.CTkLabel(hdr,text="📷  Caméra",font=("Arial",13,"bold"),text_color="#e0e0e0").pack(side="left",padx=10,pady=8)
        ctk.CTkButton(hdr,text="✕",width=28,height=28,fg_color="#6a1a1a",hover_color="#8a2a2a",command=self.stop).pack(side="right",padx=8,pady=8)
        self.vl=ctk.CTkLabel(self,text="Démarrage…",text_color="#aaa"); self.vl.pack(fill="both",expand=True,padx=6,pady=6)
        self.sl=ctk.CTkLabel(self,text="",font=("Arial",11),text_color="#44ee88"); self.sl.pack()
        ctk.CTkButton(self,text="📸 Prendre une photo",fg_color="#1a6a3a",hover_color="#2a8a4a",command=self._take).pack(pady=(0,10))
        self._start()
    def _start(self):
        if not CV2 or not PIL: self.vl.configure(text="pip install opencv-python pillow"); return
        self._cap=cv2.VideoCapture(0)
        if not self._cap.isOpened(): self.vl.configure(text="Caméra introuvable."); return
        self._run=True; self._upd()
    def _upd(self):
        if not self._run or not self._cap: return
        ret,frame=self._cap.read()
        if ret:
            w=max(self.winfo_width()-12,180); h=int(w*480/640)
            img=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).resize((w,h))
            ci=ImageTk.PhotoImage(img); self.vl.configure(image=ci,text=""); self.vl._ir=ci
        self.after(30,self._upd)
    def _take(self):
        if not self._cap: return
        ret,frame=self._cap.read()
        if not ret: return
        os.makedirs("photos",exist_ok=True)
        p=os.path.join("photos",f"photo_{dt.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        cv2.imwrite(p,frame); self.sl.configure(text=f"✓ {os.path.basename(p)}")
        if self.on_photo: self.after(0,lambda:self.on_photo(p))
    def stop(self):
        self._run=False
        if self._cap: self._cap.release(); self._cap=None
        if self.on_close: self.on_close()
        self.destroy()

def mk_cam(master,pr,rp,on_photo=None):
    def tgl():
        if pr.get("cam"): pr["cam"].stop(); pr["cam"]=None; return
        def oc(): pr["cam"]=None
        c=CamPanel(rp,on_photo=on_photo,on_close=oc); c.pack(fill="both",expand=True,padx=4,pady=4); pr["cam"]=c
    return ctk.CTkButton(master,text="📷",width=35,height=35,fg_color="#3a3a3a",hover_color="#4a4a4a",command=tgl)


# ═══════════════════════════════════════════════════════════════════════════════
# VOCAL
# ═══════════════════════════════════════════════════════════════════════════════
class _VT:
    def __init__(self,on_t,on_s,on_e): self.on_t=on_t;self.on_s=on_s;self.on_e=on_e;self._run=False
    def start(self): self._run=True; threading.Thread(target=self._l,daemon=True).start()
    def stop(self): self._run=False
    def _l(self):
        r=sr.Recognizer(); r.energy_threshold=300; r.dynamic_energy_threshold=True; r.pause_threshold=0.8
        try: mic=sr.Microphone()
        except Exception as e: self.on_e(f"Micro: {e}"); self._run=False; return
        self.on_s("calibrating")
        with mic as src:
            r.adjust_for_ambient_noise(src,duration=0.8); self.on_s("ready")
            while self._run:
                try:
                    self.on_s("listening"); audio=r.listen(src,timeout=5,phrase_time_limit=20)
                    self.on_s("processing"); text=r.recognize_google(audio,language="fr-FR")
                    if text.strip(): self.on_t(text.strip())
                except sr.WaitTimeoutError: pass
                except sr.UnknownValueError: pass
                except sr.RequestError as e: self.on_e(f"Network: {e}"); break
                except: pass
        self._run=False; self.on_s("stopped")

class VoicePanel(ctk.CTkFrame):
    PL=["#1a3a2a","#1e4a34","#22583e","#26664a","#22583e","#1e4a34","#1a3a2a"]
    def __init__(self,master,on_t=None,on_close=None,**kw):
        super().__init__(master,fg_color=BP,**kw)
        self.on_t=on_t;self.on_close=on_close;self._rec=None;self._pj=None;self._pi=0
        hdr=ctk.CTkFrame(self,fg_color=BH);hdr.pack(fill="x")
        ctk.CTkLabel(hdr,text="🎙  Vocal",font=("Arial",13,"bold"),text_color="#e0e0e0").pack(side="left",padx=10,pady=8)
        ctk.CTkButton(hdr,text="✕",width=28,height=28,fg_color="#6a1a1a",hover_color="#8a2a2a",command=self.stop).pack(side="right",padx=8,pady=8)
        self.pf=ctk.CTkFrame(self,fg_color="#1a3a2a",corner_radius=60,width=120,height=120)
        self.pf.pack(pady=16);self.pf.pack_propagate(False)
        ctk.CTkLabel(self.pf,text="🎙",font=("Arial",44)).place(relx=0.5,rely=0.5,anchor="center")
        self.sl=ctk.CTkLabel(self,text="Démarrage…",font=("Arial",12),text_color="#aaa");self.sl.pack()
        ctk.CTkLabel(self,text="Phrases reconnues",font=("Arial",11,"bold"),text_color="#555").pack(anchor="w",padx=12)
        self.hist=ctk.CTkTextbox(self,fg_color="#1e1e1e",text_color="#ccc",font=("Arial",12),wrap="word",state="disabled",height=120)
        self.hist.pack(fill="x",padx=8,pady=(2,8))
        ctk.CTkButton(self,text="⏹ Arrêter",fg_color="#6a1a1a",hover_color="#8a2a2a",command=self.stop).pack(pady=(0,8))
        if SR:
            self._rec=_VT(on_t=lambda t:self.after(0,lambda:self._ot(t)),
                          on_s=lambda s:self.after(0,lambda:self._os(s)),
                          on_e=lambda e:self.after(0,lambda:self.sl.configure(text=f"⚠ {e}",text_color="#f44747")))
            self._rec.start()
        else: self.sl.configure(text="⚠ pip install SpeechRecognition pyaudio",text_color="#f44747")
    def _ot(self,t):
        self.hist.configure(state="normal"); self.hist.insert("end",f"• {t}\n")
        self.hist.configure(state="disabled"); self.hist.see("end")
        if self.on_t: self.on_t(t)
    def _os(self,s):
        m={"calibrating":("Calibration…","#aaa",False),"ready":("Prêt — parlez !","#44ee88",False),
           "listening":("🔴 Écoute…","#44aaee",True),"processing":("⏳ Traitement…","#ffaa44",False),"stopped":("Arrêté","#888",False)}
        msg,col,pulse=m.get(s,("…","#aaa",False)); self.sl.configure(text=msg,text_color=col)
        if pulse: self._sp()
        else: self._ep()
    def _sp(self):
        if self._pj: return
        self._an()
    def _ep(self):
        if self._pj: self.after_cancel(self._pj); self._pj=None
        try: self.pf.configure(fg_color="#1a3a2a")
        except: pass
    def _an(self):
        try: self.pf.configure(fg_color=self.PL[self._pi%len(self.PL)]); self._pi+=1; self._pj=self.after(120,self._an)
        except: self._pj=None
    def stop(self):
        self._ep()
        if self._rec: self._rec.stop(); self._rec=None
        if self.on_close: self.on_close()
        self.destroy()

def mk_voice(master,pr,rp,on_t=None):
    def tgl():
        if pr.get("voice"): pr["voice"].stop(); pr["voice"]=None; btn.configure(text="🎙",fg_color="#3a3a3a"); return
        if not SR: return
        def oc(): pr["voice"]=None; btn.configure(text="🎙",fg_color="#3a3a3a")
        vp=VoicePanel(rp,on_t=on_t,on_close=oc); vp.pack(fill="both",expand=True,padx=4,pady=4)
        pr["voice"]=vp; btn.configure(text="🔴",fg_color="#aa2222")
    btn=ctk.CTkButton(master,text="🎙",width=35,height=35,fg_color="#3a3a3a",hover_color="#4a4a4a",command=tgl)
    return btn

def mk_sash(container,rp):
    s=ctk.CTkFrame(container,width=5,cursor="sb_h_double_arrow",fg_color="#3a3a3a"); s.pack(side="right",fill="y")
    _d={"x":0,"w":300}
    def _p(e): _d["x"]=e.x_root; _d["w"]=rp.winfo_width()
    def _m(e): rp.configure(width=max(180,min(600,_d["w"]+(_d["x"]-e.x_root))))
    s.bind("<ButtonPress-1>",_p); s.bind("<B1-Motion>",_m)


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH WIDGETS
# ═══════════════════════════════════════════════════════════════════════════════
class PSBar(ctk.CTkFrame):
    C=["#ff4444","#ff8800","#ffcc00","#44bb44","#00cc88"]
    def __init__(self,master,**kw):
        super().__init__(master,fg_color="transparent",**kw); self.bars=[]
        row=ctk.CTkFrame(self,fg_color="transparent"); row.pack(fill="x")
        for _ in range(4):
            b=ctk.CTkFrame(row,width=48,height=6,corner_radius=3,fg_color="#444"); b.pack(side="left",padx=2); self.bars.append(b)
        self.lbl=ctk.CTkLabel(self,text="",font=("Arial",11),text_color="#aaa"); self.lbl.pack()
    def update(self,pwd):
        if not pwd:
            for b in self.bars: b.configure(fg_color="#444")
            self.lbl.configure(text=""); return
        s,label=ps(pwd); c=self.C[s]
        for i,b in enumerate(self.bars): b.configure(fg_color=c if i<s else "#444")
        self.lbl.configure(text=label,text_color=c)

class RegFrame(ctk.CTkFrame):
    def __init__(self,master,on_ok,**kw):
        super().__init__(master,**kw); self.on_ok=on_ok
        self.configure(fg_color=BP,width=370,height=660); self._ev=False
        ctk.CTkLabel(self,text="Créer un Compte",font=("Arial",20,"bold")).pack(pady=16)
        self.un=ctk.CTkEntry(self,placeholder_text="Nom d'utilisateur",width=240); self.un.pack(pady=6)
        er=ctk.CTkFrame(self,fg_color="transparent"); er.pack(pady=6)
        self.em=ctk.CTkEntry(er,placeholder_text="Adresse email",width=198,show="*"); self.em.pack(side="left",padx=(0,6))
        self.eyb=ctk.CTkButton(er,text="👁",width=34,height=34,fg_color="#3a3a3a",hover_color="#4a4a4a",command=self._te); self.eyb.pack(side="left")
        self.pw=ctk.CTkEntry(self,placeholder_text="Mot de passe",show="*",width=240); self.pw.pack(pady=6)
        self.pw.bind("<KeyRelease>",lambda e:self.sb.update(self.pw.get()))
        self.sb=PSBar(self); self.sb.pack(pady=2)
        self.cp=ctk.CTkEntry(self,placeholder_text="Confirmer le mot de passe",show="*",width=240); self.cp.pack(pady=6)
        self.rem=ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self,text="Se souvenir de moi",variable=self.rem).pack(pady=4)
        self.err=ctk.CTkLabel(self,text="",text_color="#f44747",font=("Arial",12),wraplength=280); self.err.pack(pady=4)
        ctk.CTkButton(self,text="Créer le compte",width=240,command=self._save).pack(pady=8)
        ctk.CTkButton(self,text="Déjà un compte ? Se connecter",fg_color="transparent",hover_color="#3a3a3a",font=("Arial",12),command=lambda:self.master.show_login()).pack(pady=4)
    def _te(self):
        self._ev=not self._ev; self.em.configure(show="" if self._ev else "*"); self.eyb.configure(text="🙈" if self._ev else "👁")
    def _save(self):
        u=self.un.get().strip(); em=self.em.get().strip().lower(); p=self.pw.get(); c=self.cp.get()
        if not u or not em or not p: self.err.configure(text="Tous les champs sont obligatoires."); return
        if not ve(em): self.err.configure(text="Email invalide."); return
        if len(p)<6: self.err.configure(text="Mot de passe trop court (6 min)."); return
        if p!=c: self.err.configure(text="Mots de passe différents."); return
        users=lu()
        if any(x["username"].lower()==u.lower() for x in users): self.err.configure(text="Nom d'utilisateur déjà pris."); return
        if any(x.get("email","").strip().lower()==em for x in users): self.err.configure(text="Email déjà utilisé."); return
        data={"id":str(uuid.uuid4())[:8],"username":u,"email":em,"password":hp(p),
              "avatar":"👤","login_history":[],"failed_attempts":0,"locked_until":0}
        users.append(data); su(users)
        if self.rem.get(): ss(u)
        self.on_ok(u,welcome=True)

class LoginFrame(ctk.CTkFrame):
    def __init__(self,master,on_ok,**kw):
        super().__init__(master,**kw); self.on_ok=on_ok
        self.configure(fg_color=BP,width=370,height=460)
        ctk.CTkLabel(self,text="Connexion",font=("Arial",20,"bold")).pack(pady=20)
        self.un=ctk.CTkEntry(self,placeholder_text="Nom d'utilisateur ou email",width=240); self.un.pack(pady=8)
        self.pw=ctk.CTkEntry(self,placeholder_text="Mot de passe",show="*",width=240); self.pw.pack(pady=8)
        self.rem=ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self,text="Se souvenir de moi",variable=self.rem).pack(pady=4)
        self.err=ctk.CTkLabel(self,text="",text_color="#f44747",font=("Arial",12)); self.err.pack(pady=4)
        ctk.CTkButton(self,text="Se connecter",width=240,command=self._login).pack(pady=8)
        ctk.CTkButton(self,text="Mot de passe oublié ?",fg_color="transparent",hover_color="#3a3a3a",font=("Arial",12),command=lambda:self.master.show_forgot()).pack(pady=2)
        ctk.CTkButton(self,text="Pas de compte ? S'inscrire",fg_color="transparent",hover_color="#3a3a3a",font=("Arial",12),command=lambda:self.master.show_register()).pack(pady=2)
    def _login(self):
        ident=self.un.get().strip().lower(); p=self.pw.get()
        if not ident or not p: self.err.configure(text="Tous les champs sont obligatoires."); return
        users=lu(); h=hp(p)
        ud=next((u for u in users if u["username"].lower()==ident or u.get("email","").strip().lower()==ident),None)
        if not ud: self.err.configure(text="Identifiants incorrects."); return
        if time.time()<ud.get("locked_until",0):
            self.err.configure(text=f"Compte bloqué. Attendre {int(ud['locked_until']-time.time())}s."); return
        if ud["password"]!=h:
            ud["failed_attempts"]=ud.get("failed_attempts",0)+1
            if ud["failed_attempts"]>=MAX_ATT:
                ud["locked_until"]=time.time()+60; ud["failed_attempts"]=0; su(users)
                self.err.configure(text="Trop de tentatives. Bloqué 60s.")
            else:
                su(users); self.err.configure(text=f"Mot de passe incorrect. {MAX_ATT-ud['failed_attempts']} tentative(s).")
            return
        ud["failed_attempts"]=0; ud["locked_until"]=0; su(users); rl(ud["username"])
        if self.rem.get(): ss(ud["username"])
        self.on_ok(ud["username"],welcome=True)

class ForgotFrame(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.configure(fg_color=BP, width=370, height=400)
        self._code   = None
        self._target = None
        self._sent   = False

        ctk.CTkLabel(self, text="Réinitialiser le mot de passe",
                     font=("Arial", 18, "bold")).pack(pady=20)

        # Email
        self.ee = ctk.CTkEntry(self, placeholder_text="Votre adresse email", width=240)
        self.ee.pack(pady=8)

        # Code
        ctk.CTkLabel(self, text="Code de réinitialisation",
                     font=("Arial", 11), text_color="#888").pack()
        self.ce = ctk.CTkEntry(self, placeholder_text="ex: 123456", width=240)
        self.ce.pack(pady=(2, 8))

        # Nouveau mot de passe
        ctk.CTkLabel(self, text="Nouveau mot de passe",
                     font=("Arial", 11), text_color="#888").pack()
        self.pe = ctk.CTkEntry(self, placeholder_text="6 caractères min.",
                               show="*", width=240)
        self.pe.pack(pady=(2, 8))

        self.info = ctk.CTkLabel(self, text="", text_color="#888",
                                 font=("Arial", 11), wraplength=300)
        self.info.pack(pady=4)

        self.btn = ctk.CTkButton(self, text="1. Envoyer le code",
                                 width=240, command=self._step1)
        self.btn.pack(pady=4)

        self.btn2 = ctk.CTkButton(self, text="2. Confirmer et changer",
                                  width=240, command=self._step2,
                                  fg_color="#1a5a3a", hover_color="#2a6a4a")
        self.btn2.pack(pady=4)

        ctk.CTkButton(self, text="← Retour à la connexion",
                      fg_color="transparent", hover_color="#3a3a3a",
                      font=("Arial", 12),
                      command=lambda: self.master.show_login()).pack(pady=6)

        # Focus sur email au démarrage
        self.after(100, lambda: self.ee.focus())

    def _step1(self):
        """Étape 1 : vérifier l'email et générer le code."""
        em = self.ee.get().strip().lower()
        if not em:
            self.info.configure(text="⚠ Entrez votre adresse email.",
                                text_color="#f44747")
            return
        users = lu()
        user  = next((u for u in users
                      if u.get("email", "").strip().lower() == em), None)
        if not user:
            self.info.configure(text="⚠ Aucun compte avec cet email.",
                                text_color="#f44747")
            return
        self._code   = "".join(random.choices(string.digits, k=6))
        self._target = user["username"]
        self._sent   = True
        self.info.configure(
            text=f"✓ Code généré : {self._code}\n"
                 f"Copiez-le dans le champ ci-dessus puis cliquez '2. Confirmer'.",
            text_color="#44bb44")
        self.btn.configure(fg_color="#1a3a5a", text="✓ Code envoyé")
        # Mettre le code directement dans le champ pour faciliter
        self.ce.delete(0, "end")
        self.ce.insert(0, self._code)
        self.ce.focus()

    def _step2(self):
        """Étape 2 : vérifier le code et changer le mot de passe."""
        if not self._sent:
            self.info.configure(text="⚠ Cliquez d'abord sur '1. Envoyer le code'.",
                                text_color="#f44747")
            return
        code = self.ce.get().strip()
        npwd = self.pe.get()
        if not code:
            self.info.configure(text="⚠ Le champ code est vide.",
                                text_color="#f44747")
            self.ce.focus(); return
        if code != self._code:
            self.info.configure(text="⚠ Code incorrect.",
                                text_color="#f44747")
            self.ce.focus(); return
        if len(npwd) < 6:
            self.info.configure(text="⚠ Mot de passe trop court (6 min).",
                                text_color="#f44747")
            self.pe.focus(); return
        users = lu()
        for u in users:
            if u["username"] == self._target:
                u["password"] = hp(npwd); break
        su(users)
        self.info.configure(text="✅ Mot de passe changé ! Redirection…",
                            text_color="#44bb44")
        self.btn.configure(state="disabled")
        self.btn2.configure(state="disabled")
        self.master.after(2000, self.master.show_login)


class ProfileFrame(ctk.CTkFrame):
    AVS=["👤","🧑","👩","🧔","👨‍💻","🧑‍🎨","🦊","🐼","🤖","🦁"]
    def __init__(self,master,username,on_close,**kw):
        super().__init__(master,**kw); self.un=username; self.on_close=on_close
        self.configure(fg_color=BP,width=400,height=640)
        users=lu(); self.user=next((u for u in users if u["username"]==username),{})

        ctk.CTkLabel(self,text="Mon Profil",font=("Arial",20,"bold")).pack(pady=16)

        # Avatar
        self.avl=ctk.CTkLabel(self,text=self.user.get("avatar","👤"),font=("Arial",48),text_color="#ffffff")
        self.avl.pack()
        ar=ctk.CTkFrame(self,fg_color="transparent"); ar.pack(pady=4)
        for av in self.AVS:
            ctk.CTkButton(ar,text=av,width=36,height=36,fg_color="#1a2a4a",
                          hover_color="#2a4a7a",font=("Arial",20),text_color="#ffffff",
                          border_width=1,border_color="#2d6bcc",corner_radius=8,
                          command=lambda a=av:self._sa(a)).pack(side="left",padx=2,pady=2)

        # Nom d'utilisateur affiché + éditable
        self.un_lbl=ctk.CTkLabel(self,text=f"@{username}",font=("Arial",14),
                                  text_color="#aaa"); self.un_lbl.pack(pady=(4,0))
        ctk.CTkLabel(self,text="Changer le nom d'utilisateur",font=("Arial",13,"bold"),
                     anchor="w").pack(fill="x",padx=30,pady=(10,2))
        self.nun=ctk.CTkEntry(self,placeholder_text="Nouveau nom d'utilisateur",width=260)
        self.nun.pack()

        # Email
        ctk.CTkLabel(self,text="Modifier l'email",font=("Arial",13,"bold"),
                     anchor="w").pack(fill="x",padx=30,pady=(10,2))
        self.ne=ctk.CTkEntry(self,placeholder_text="Nouvel email",width=260); self.ne.pack()

        # Mot de passe
        ctk.CTkLabel(self,text="Modifier le mot de passe",font=("Arial",13,"bold"),
                     anchor="w").pack(fill="x",padx=30,pady=(10,2))
        self.npw=ctk.CTkEntry(self,placeholder_text="Nouveau mot de passe",show="*",width=260)
        self.npw.pack(); self.npw.bind("<KeyRelease>",lambda e:self.sb.update(self.npw.get()))
        self.sb=PSBar(self); self.sb.pack(pady=2)

        self.msg=ctk.CTkLabel(self,text="",font=("Arial",12),text_color="#44bb44")
        self.msg.pack(pady=4)
        ctk.CTkButton(self,text="Sauvegarder",width=260,command=self._save).pack(pady=6)

        # Historique
        h=self.user.get("login_history",[])
        if h:
            ctk.CTkLabel(self,text="Dernières connexions",font=("Arial",13,"bold"),
                         anchor="w").pack(fill="x",padx=30,pady=(10,2))
            for e in reversed(h):
                ctk.CTkLabel(self,text=f"🕐 {e}",font=("Arial",11),text_color="#aaa").pack()

        ctk.CTkButton(self,text="✕ Fermer",fg_color="transparent",
                      hover_color="#3a3a3a",command=on_close).pack(pady=10)

    def _sa(self,av):
        self.avl.configure(text=av, text_color="#ffffff"); users=lu()
        for u in users:
            if u["username"]==self.un: u["avatar"]=av; break
        su(users); self.master.update_av(av)

    def _save(self):
        users=lu()
        new_un  = self.nun.get().strip()
        ne      = self.ne.get().strip().lower()
        npw     = self.npw.get()
        changed = False

        for u in users:
            if u["username"]==self.un:

                # ✅ Changer le nom d'utilisateur
                if new_un and new_un != self.un:
                    if any(x["username"].lower()==new_un.lower() for x in users):
                        self.msg.configure(text="Nom d'utilisateur déjà pris.",
                                           text_color="#f44747"); return
                    old_un = self.un
                    u["username"] = new_un
                    self.un = new_un
                    self.un_lbl.configure(text=f"@{new_un}")
                    # Mettre à jour la session si active
                    if os.path.exists("session.json"):
                        ss(new_un)
                    self.master.ul.configure(text=new_un)
                    self.master.cu = new_un
                    changed = True

                # Email
                if ne:
                    if not ve(ne):
                        self.msg.configure(text="Email invalide.",text_color="#f44747"); return
                    if any(x.get("email","").strip().lower()==ne and x["username"]!=self.un
                           for x in users):
                        self.msg.configure(text="Email déjà utilisé.",text_color="#f44747"); return
                    u["email"]=ne; changed=True

                # Mot de passe
                if npw:
                    if len(npw)<6:
                        self.msg.configure(text="Mot de passe trop court.",
                                           text_color="#f44747"); return
                    u["password"]=hp(npw); changed=True
                break

        if changed:
            su(users)
            self.nun.delete(0,"end"); self.ne.delete(0,"end")
            self.npw.delete(0,"end"); self.sb.update("")
            self.msg.configure(text="Sauvegardé ✓",text_color="#44bb44")
        else:
            self.msg.configure(text="Aucune modification.",text_color="#aaa")

class FriendsPage(ctk.CTkFrame):
    def __init__(self,master,username,on_close,**kw):
        super().__init__(master,**kw); self.un=username; self.on_close=on_close
        self.configure(fg_color=BP,width=480,height=580)
        hdr=ctk.CTkFrame(self,fg_color=BH,corner_radius=0); hdr.pack(fill="x")
        ctk.CTkLabel(hdr,text="👥  Mes Amis",font=("Arial",18,"bold"),text_color="#e0e0e0").pack(side="left",padx=16,pady=12)
        ctk.CTkButton(hdr,text="✕",width=30,height=30,fg_color="transparent",hover_color="#3a3a3a",command=on_close).pack(side="right",padx=10,pady=10)
        tr=ctk.CTkFrame(self,fg_color="#222"); tr.pack(fill="x",pady=(8,0)); self._tabs={}
        for lbl,key in [("👥 Amis","friends"),("🔔 Demandes","requests"),("🔍 Chercher","search")]:
            b=ctk.CTkButton(tr,text=lbl,width=130,fg_color="#333",hover_color="#444",command=lambda k=key:self._show(k))
            b.pack(side="left",padx=4,pady=6); self._tabs[key]=b
        self.cnt=ctk.CTkFrame(self,fg_color=BP); self.cnt.pack(fill="both",expand=True,padx=10,pady=10)
        self._show("friends")
    def _clear(self):
        for w in self.cnt.winfo_children(): w.destroy()
        for b in self._tabs.values(): b.configure(fg_color="#333")
    def _show(self,key):
        self._clear(); self._tabs[key].configure(fg_color="#1a5a3a")
        {"friends":self._f,"requests":self._r,"search":self._s}[key]()
    def _f(self):
        friends=gf(self.un); users=lu()
        if not friends:
            ctk.CTkLabel(self.cnt,text="Vous n'avez pas encore d'amis.",text_color="#666",font=("Arial",13)).pack(pady=40); return
        sc=ctk.CTkScrollableFrame(self.cnt,fg_color=BP); sc.pack(fill="both",expand=True)
        for f in friends:
            ud=next((u for u in users if u["username"]==f),{})
            row=ctk.CTkFrame(sc,fg_color="#333",corner_radius=10); row.pack(fill="x",pady=4,padx=4)
            ctk.CTkLabel(row,text=f"{ud.get('avatar','👤')}  {f}",font=("Arial",14),width=200,anchor="w").pack(side="left",padx=12,pady=10)
            ctk.CTkButton(row,text="Supprimer",width=90,fg_color="#6a1a1a",hover_color="#8a2a2a",command=lambda fr=f:(rmf(self.un,fr),self._show("friends"))).pack(side="right",padx=8,pady=8)
    def _r(self):
        rcv=gri(self.un); snt=gro(self.un); users=lu()
        sc=ctk.CTkScrollableFrame(self.cnt,fg_color=BP); sc.pack(fill="both",expand=True)
        if rcv:
            ctk.CTkLabel(sc,text="Demandes reçues",font=("Arial",13,"bold"),text_color="#44aaee").pack(anchor="w",pady=(8,4))
            for f in rcv:
                ud=next((u for u in users if u["username"]==f),{})
                row=ctk.CTkFrame(sc,fg_color="#1a2a3a",corner_radius=10); row.pack(fill="x",pady=3,padx=4)
                ctk.CTkLabel(row,text=f"{ud.get('avatar','👤')}  {f}",font=("Arial",13),anchor="w",width=160).pack(side="left",padx=10,pady=8)
                ctk.CTkButton(row,text="✓ Accepter",width=90,fg_color="#1a6a3a",hover_color="#2a8a4a",command=lambda fr=f:(afr(self.un,fr),self._show("requests"))).pack(side="right",padx=4,pady=6)
                ctk.CTkButton(row,text="✗ Refuser",width=80,fg_color="#6a1a1a",hover_color="#8a2a2a",command=lambda fr=f:(rfr(self.un,fr),self._show("requests"))).pack(side="right",padx=4,pady=6)
        if snt:
            ctk.CTkLabel(sc,text="Demandes envoyées",font=("Arial",13,"bold"),text_color="#aaa").pack(anchor="w",pady=(16,4))
            for f in snt:
                ud=next((u for u in users if u["username"]==f),{})
                row=ctk.CTkFrame(sc,fg_color="#2a2a2a",corner_radius=10); row.pack(fill="x",pady=3,padx=4)
                ctk.CTkLabel(row,text=f"{ud.get('avatar','👤')}  {f}  — En attente…",font=("Arial",13),text_color="#888",anchor="w").pack(side="left",padx=10,pady=10)
        if not rcv and not snt:
            ctk.CTkLabel(sc,text="Aucune demande en cours.",text_color="#666",font=("Arial",13)).pack(pady=40)
    def _s(self):
        sr2=ctk.CTkFrame(self.cnt,fg_color="transparent"); sr2.pack(fill="x",pady=(8,4))
        self._se=ctk.CTkEntry(sr2,placeholder_text="Nom d'utilisateur…",width=260,font=("Arial",13)); self._se.pack(side="left",padx=(0,8))
        ctk.CTkButton(sr2,text="🔍 Chercher",width=110,command=self._ds).pack(side="left")
        self._se.bind("<Return>",lambda e:self._ds())
        self._sr2=ctk.CTkFrame(self.cnt,fg_color="transparent"); self._sr2.pack(fill="both",expand=True)
    def _ds(self):
        q=self._se.get().strip().lower()
        for w in self._sr2.winfo_children(): w.destroy()
        if not q: return
        users=lu(); friends=gf(self.un); sent=gro(self.un)
        res=[u for u in users if q in u["username"].lower() and u["username"]!=self.un]
        if not res:
            ctk.CTkLabel(self._sr2,text="Aucun utilisateur trouvé.",text_color="#666",font=("Arial",13)).pack(pady=20); return
        for u in res[:10]:
            uname=u["username"]; av=u.get("avatar","👤")
            row=ctk.CTkFrame(self._sr2,fg_color="#333",corner_radius=10); row.pack(fill="x",pady=4,padx=4)
            ctk.CTkLabel(row,text=f"{av}  {uname}",font=("Arial",14),anchor="w",width=200).pack(side="left",padx=12,pady=10)
            if uname in friends: ctk.CTkLabel(row,text="✓ Ami",text_color="#44ee88",font=("Arial",12)).pack(side="right",padx=12)
            elif uname in sent: ctk.CTkLabel(row,text="⏳ Envoyée",text_color="#aaa",font=("Arial",12)).pack(side="right",padx=12)
            else: ctk.CTkButton(row,text="➕ Ajouter",width=90,fg_color="#1a5a8a",hover_color="#2a6a9a",command=lambda un=uname,r=row:self._sndr(un,r)).pack(side="right",padx=8,pady=8)
    def _sndr(self,to,row):
        result=sfr(self.un,to)
        t,c={"sent":("⏳ Envoyée","#aaa"),"already_friends":("✓ Ami","#44ee88"),"already_sent":("⏳ Envoyée","#aaa"),"already_received":("✓ Reçue","#44aaee")}.get(result,("…","#aaa"))
        for w in row.winfo_children():
            if isinstance(w,ctk.CTkButton): w.destroy()
        ctk.CTkLabel(row,text=t,text_color=c,font=("Arial",12)).pack(side="right",padx=12)

class WelcomeBanner(ctk.CTkFrame):
    def __init__(self,master,username,**kw):
        super().__init__(master,**kw); self.configure(fg_color="#1a3a2a",corner_radius=10)
        users=lu(); user=next((u for u in users if u["username"]==username),{})
        hour=dt.now().hour; greet="Bonjour" if hour<12 else ("Bon après-midi" if hour<18 else "Bonsoir")
        ctk.CTkLabel(self,text=f"{user.get('avatar','👤')}  {greet}, {username} !",
                     font=("Arial",15,"bold"),text_color="#44ee88").pack(padx=20,pady=10)
        master.after(4000,self.destroy)


# ═══════════════════════════════════════════════════════════════════════════════
# APP PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════════════
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ChatCode"); self.geometry("1200x720"); self.configure(fg_color=BD)
        # ── Icône de la fenêtre et du .exe ───────────────────────────────────
        try:
            import os as _os
            _ico = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "logo.ico")
            if not _os.path.exists(_ico):
                # Chercher dans le dossier de l'exe (PyInstaller)
                _ico = _os.path.join(_os.path.dirname(sys.executable), "logo.ico")
            if _os.path.exists(_ico):
                self.iconbitmap(_ico)
        except Exception:
            pass
        self.cu=None; self.ov=None; self._ia=None
        self.grid_columnconfigure(0,weight=1); self.grid_rowconfigure(1,weight=1)
        hdr=ctk.CTkFrame(self,height=52,corner_radius=0,fg_color=BH)
        hdr.grid(row=0,column=0,sticky="ew"); hdr.grid_propagate(False)

        # ── Logo ChatCode intégré en base64 — pas besoin de logo.png externe ──
        try:
            from PIL import Image as _PILImage
            import io as _io, base64 as _b64
            _img = _PILImage.open(_io.BytesIO(_b64.b64decode(LOGO_B64))).resize((44,44), _PILImage.LANCZOS)
            self._logo_img = ctk.CTkImage(light_image=_img, dark_image=_img, size=(44,44))
            ctk.CTkLabel(hdr, image=self._logo_img, text="").pack(side="left", padx=(8,4), pady=4)
        except Exception:
            ctk.CTkLabel(hdr, text="</> ChatCode", font=("Consolas",16,"bold"),
                         text_color="#4a8aff").pack(side="left", padx=(12,4), pady=6)

        self.lb=ctk.CTkButton(hdr,text="Login",width=100,command=self.toggle_login); self.lb.pack(side="left",padx=8,pady=12)
        self.avl=ctk.CTkLabel(hdr,text="",font=("Arial",20),cursor="hand2",
                              text_color="#ffffff",fg_color="transparent"); self.avl.pack(side="left",padx=(8,2))
        self.avl.bind("<Button-1>",lambda e:self.show_profile())
        self.ul=ctk.CTkLabel(hdr,text="",font=("Arial",13),cursor="hand2",
                             text_color="#ffffff",fg_color="transparent"); self.ul.pack(side="left")
        self.ul.bind("<Button-1>",lambda e:self.show_profile())
        self.fb=ctk.CTkButton(hdr,text="👥 Amis",width=90,fg_color="#1a3a5a",hover_color="#2a4a6a",command=self.show_friends)
        self.fb.pack(side="left",padx=(12,0),pady=12); self.fb.pack_forget()
        ctk.CTkButton(hdr,text="✕",width=35,fg_color="#c42b1c",command=self.destroy).pack(side="right",padx=16)
        body=ctk.CTkFrame(self,fg_color=BD); body.grid(row=1,column=0,sticky="nsew")
        self.rp=ctk.CTkFrame(body,width=300,fg_color=BP); self.rp.pack(side="right",fill="y"); self.rp.pack_propagate(False)
        self._pr={"cam":None,"voice":None}; self._chat=None
        mk_cam(hdr,self._pr,self.rp,on_photo=self._on_photo).pack(side="right",padx=4)
        mk_voice(hdr,self._pr,self.rp,on_t=self._on_voice).pack(side="right",padx=4)
        mk_sash(body,self.rp)
        self.main=ctk.CTkFrame(body,fg_color=BD); self.main.pack(side="left",fill="both",expand=True)
        make_editor(self.main)
        self.bind_all("<Motion>",self._ri); self.bind_all("<KeyPress>",self._ri)
        sess=ls()
        if sess.get("username"):
            users=lu()
            if any(u["username"]==sess["username"] for u in users):
                self.unlock(sess["username"],welcome=False); return
        if lu(): self.show_login()
        else: self.show_register()

    def _ri(self,_=None):
        if not self.cu: return
        if self._ia: self.after_cancel(self._ia)
        self._ia=self.after(INACT,lambda:self.logout() if self.cu else None)

    def _co(self):
        if self.ov: self.ov.destroy(); self.ov=None

    def show_register(self):
        self._co(); self.ov=RegFrame(master=self,on_ok=self.unlock,corner_radius=15,border_width=2)
        self.ov.place(relx=0.5,rely=0.5,anchor="center")
    def show_login(self):
        self._co(); self.ov=LoginFrame(master=self,on_ok=self.unlock,corner_radius=15,border_width=2)
        self.ov.place(relx=0.5,rely=0.5,anchor="center")
    def show_forgot(self):
        self._co(); self.ov=ForgotFrame(master=self,corner_radius=15,border_width=2)
        self.ov.place(relx=0.5,rely=0.5,anchor="center")
    def show_profile(self):
        if not self.cu: return
        self._co(); self.ov=ProfileFrame(master=self,username=self.cu,on_close=self._co,corner_radius=15,border_width=2)
        self.ov.place(relx=0.5,rely=0.5,anchor="center")
    def show_friends(self):
        if not self.cu: return
        self._co(); self.ov=FriendsPage(master=self,username=self.cu,on_close=self._co,corner_radius=15,border_width=2)
        self.ov.place(relx=0.5,rely=0.5,anchor="center")
    def toggle_login(self):
        if self.ov: self._co()
        elif not self.cu: self.show_login()

    def unlock(self,username,welcome=True):
        self.cu=username; self._co()
        users=lu(); user=next((u for u in users if u["username"]==username),{})
        self.avl.configure(text=user.get("avatar","👤"))
        self.ul.configure(text=username)
        self.lb.configure(text="Déconnexion",command=self.logout)
        self.fb.pack(side="left",padx=(12,0),pady=12)
        if self._chat is None:
            self._chat=ChatPanel(self.rp,username=username); self._chat.pack(fill="both",expand=True)
        if welcome:
            b=WelcomeBanner(self.main,username); b.place(relx=0.5,rely=0.05,anchor="n")
        self._ri()

    def update_av(self,av): self.avl.configure(text=av)

    def logout(self):
        self.cu=None
        if self._ia: self.after_cancel(self._ia); self._ia=None
        cs(); self.avl.configure(text=""); self.ul.configure(text="")
        self.lb.configure(text="Login",command=self.toggle_login); self.fb.pack_forget()
        if self._chat: self._chat.disconnect(); self._chat.destroy(); self._chat=None
        self.show_login()

    def _on_photo(self,p):
        b=ctk.CTkLabel(self.main,text=f"📷 {p}",fg_color="#1a3a2a",corner_radius=8,font=("Arial",12),text_color="#44ee88")
        b.place(relx=0.5,rely=0.96,anchor="s"); self.after(3500,b.destroy)

    def _on_voice(self,text):
        if self._chat:
            try: self._chat.inject(text)
            except: pass


if __name__ == "__main__":
    App().mainloop()
