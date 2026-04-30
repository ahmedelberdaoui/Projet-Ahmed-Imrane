import customtkinter as ctk
import json
import os
import uuid
import hashlib
import re
import time
import random
import string
import threading
import datetime
from datetime import datetime as dt

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG_DARK   = "#1e1e1e"
BG_PANEL  = "#2b2b2b"
BG_HEADER = "#1a1a1a"

MAX_LOGIN_ATTEMPTS = 5
INACTIVITY_TIMEOUT = 5 * 60 * 1000


# ─────────────────────────────────────────────
# UTILITAIRES
# ─────────────────────────────────────────────

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email))

def password_strength(pwd: str) -> tuple:
    score = 0
    if len(pwd) >= 8:                    score += 1
    if re.search(r"[A-Z]", pwd):         score += 1
    if re.search(r"\d", pwd):            score += 1
    if re.search(r"[^a-zA-Z0-9]", pwd): score += 1
    labels = ["Très faible", "Faible", "Moyen", "Fort", "Très fort"]
    return score, labels[score]

def load_users() -> list:
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return []

def save_users(users: list):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

def load_session() -> dict:
    if os.path.exists("session.json"):
        with open("session.json", "r") as f:
            return json.load(f)
    return {}

def save_session(username: str):
    with open("session.json", "w") as f:
        json.dump({"username": username}, f)

def clear_session():
    if os.path.exists("session.json"):
        os.remove("session.json")

def record_login(username: str):
    users = load_users()
    for u in users:
        if u["username"] == username:
            history = u.get("login_history", [])
            history.append(dt.now().strftime("%d/%m/%Y %H:%M"))
            if len(history) > 5:
                history = history[-5:]
            u["login_history"] = history
            break
    save_users(users)


# ─────────────────────────────────────────────
# CAMÉRA — flux intégré dans le panneau droit
# ─────────────────────────────────────────────

class CameraPanel(ctk.CTkFrame):
    """Flux vidéo en direct affiché dans le panneau droit."""

    def __init__(self, master, on_photo=None, on_close=None, **kwargs):
        super().__init__(master, fg_color=BG_PANEL, **kwargs)
        self.on_photo  = on_photo
        self.on_close  = on_close
        self._running  = False
        self._cap      = None

        # ── Titre ──
        title_row = ctk.CTkFrame(self, fg_color=BG_HEADER)
        title_row.pack(fill="x")
        ctk.CTkLabel(title_row, text="📷  Caméra",
                     font=("Arial", 13, "bold"), text_color="#e0e0e0").pack(side="left", padx=10, pady=8)
        ctk.CTkButton(title_row, text="✕", width=28, height=28,
                      fg_color="#6a1a1a", hover_color="#8a2a2a",
                      command=self.stop).pack(side="right", padx=8, pady=8)

        # ── Affichage vidéo ──
        self.video_label = ctk.CTkLabel(self, text="Démarrage…", font=("Arial", 12),
                                        text_color="#aaa")
        self.video_label.pack(fill="both", expand=True, padx=6, pady=6)

        # ── Statut + bouton photo ──
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 11),
                                         text_color="#44ee88")
        self.status_label.pack(pady=(0, 4))

        ctk.CTkButton(self, text="📸 Prendre une photo",
                      fg_color="#1a6a3a", hover_color="#2a8a4a",
                      command=self.take_photo).pack(pady=(0, 10))

        self.start()

    def start(self):
        if not CV2_AVAILABLE or not PIL_AVAILABLE:
            self.video_label.configure(
                text="Modules manquants.\npip install opencv-python pillow")
            return
        self._cap = cv2.VideoCapture(0)
        if not self._cap.isOpened():
            self.video_label.configure(text="Caméra introuvable.")
            return
        self._running = True
        self._update()

    def _update(self):
        if not self._running or self._cap is None:
            return
        ret, frame = self._cap.read()
        if ret:
            # Adapte la taille à la largeur du panneau
            w = max(self.winfo_width() - 12, 180)
            h = int(w * 480 / 640)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img       = Image.fromarray(frame_rgb).resize((w, h))
            ctk_img   = ImageTk.PhotoImage(img)
            self.video_label.configure(image=ctk_img, text="")
            self.video_label._image_ref = ctk_img
        self.after(30, self._update)

    def take_photo(self):
        if self._cap is None:
            return
        ret, frame = self._cap.read()
        if not ret:
            self.status_label.configure(text="Échec.", text_color="#ff4444")
            return
        os.makedirs("photos", exist_ok=True)
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        path      = os.path.join("photos", f"photo_{timestamp}.jpg")
        cv2.imwrite(path, frame)
        self.status_label.configure(text=f"✓ {os.path.basename(path)}", text_color="#44ee88")
        if self.on_photo:
            self.after(0, lambda: self.on_photo(path))

    def stop(self):
        self._running = False
        if self._cap:
            self._cap.release()
            self._cap = None
        if self.on_close:
            self.on_close()
        self.destroy()


def make_camera_button(master, panel_ref: dict, right_panel, on_photo=None) -> ctk.CTkButton:
    """Bouton 📷 — ouvre/ferme le flux caméra dans le panneau droit."""

    def toggle():
        if panel_ref.get("cam") is not None:
            # déjà ouvert → fermer
            panel_ref["cam"].stop()
            panel_ref["cam"] = None
            return

        def on_close():
            panel_ref["cam"] = None

        cam = CameraPanel(right_panel, on_photo=on_photo, on_close=on_close)
        cam.pack(fill="both", expand=True, padx=4, pady=4)
        panel_ref["cam"] = cam

    return ctk.CTkButton(
        master, text="📷", width=35, height=35,
        fg_color="#3a3a3a", hover_color="#4a4a4a",
        command=toggle
    )


# ─────────────────────────────────────────────
# VOCAL — panneau dans la colonne droite
# ─────────────────────────────────────────────

class VoicePanel(ctk.CTkFrame):
    """Panneau vocal intégré dans le panneau droit (comme CameraPanel)."""

    PULSE_COLORS = ["#1a3a2a", "#1e4a34", "#22583e", "#26664a",
                    "#22583e", "#1e4a34", "#1a3a2a"]

    def __init__(self, master, on_transcript=None, on_close=None, **kwargs):
        super().__init__(master, fg_color=BG_PANEL, **kwargs)
        self.on_transcript = on_transcript
        self.on_close      = on_close
        self._recorder     = None
        self._pulse_idx    = 0
        self._pulse_job    = None
        self._history      = []   # phrases reconnues

        # ── Titre ──────────────────────────────────────────────────────
        title_row = ctk.CTkFrame(self, fg_color=BG_HEADER)
        title_row.pack(fill="x")
        ctk.CTkLabel(title_row, text="🎙  Vocal",
                     font=("Arial", 13, "bold"), text_color="#e0e0e0").pack(side="left", padx=10, pady=8)
        ctk.CTkButton(title_row, text="✕", width=28, height=28,
                      fg_color="#6a1a1a", hover_color="#8a2a2a",
                      command=self.stop).pack(side="right", padx=8, pady=8)

        # ── Zone animée (cercle pulsant) ────────────────────────────────
        self.pulse_frame = ctk.CTkFrame(self, fg_color="#1a3a2a", corner_radius=60,
                                        width=120, height=120)
        self.pulse_frame.pack(pady=18)
        self.pulse_frame.pack_propagate(False)
        self.mic_icon = ctk.CTkLabel(self.pulse_frame, text="🎙",
                                     font=("Arial", 44))
        self.mic_icon.place(relx=0.5, rely=0.5, anchor="center")

        # ── Statut ──────────────────────────────────────────────────────
        self.status_label = ctk.CTkLabel(self, text="Démarrage…",
                                         font=("Arial", 12), text_color="#aaa")
        self.status_label.pack(pady=(0, 8))

        # ── Historique des phrases ──────────────────────────────────────
        ctk.CTkLabel(self, text="Phrases reconnues", font=("Arial", 11, "bold"),
                     text_color="#666").pack(anchor="w", padx=12)
        self.history_box = ctk.CTkTextbox(self, fg_color="#1e1e1e", text_color="#cccccc",
                                          font=("Arial", 12), wrap="word",
                                          state="disabled", corner_radius=8, height=160)
        self.history_box.pack(fill="x", padx=8, pady=(2, 10))

        # ── Bouton micro ────────────────────────────────────────────────
        self.mic_btn = ctk.CTkButton(self, text="⏹ Arrêter l'écoute",
                                     fg_color="#6a1a1a", hover_color="#8a2a2a",
                                     command=self.stop)
        self.mic_btn.pack(pady=(0, 12))

        self._start()

    # ── Démarrage ──────────────────────────────────────────────────────

    def _start(self):
        if not SR_AVAILABLE:
            self._set_status("⚠ pip install SpeechRecognition pyaudio", "#ff4444")
            self.mic_icon.configure(text="⚠")
            return

        self._recorder = _VoiceRecorder(
            on_transcript=self._on_text,
            on_status=self._on_status,
            on_error=self._on_error
        )
        self._recorder.start()

    def _on_text(self, text: str):
        self.after(0, lambda: self._insert_phrase(text))
        if self.on_transcript:
            self.after(0, lambda: self.on_transcript(text))

    def _insert_phrase(self, text: str):
        self._history.append(text)
        self.history_box.configure(state="normal")
        self.history_box.insert("end", f"• {text}\n")
        self.history_box.configure(state="disabled")
        self.history_box.see("end")

    def _on_status(self, state: str):
        messages = {
            "calibrating": ("Calibration du micro…",  "#aaaaaa", False),
            "ready":       ("Prêt — parlez !",         "#44ee88", False),
            "listening":   ("🔴  Écoute…",             "#44aaee", True),
            "processing":  ("⏳  Traitement…",         "#ffaa44", False),
            "stopped":     ("Arrêté",                  "#888888", False),
        }
        msg, color, pulse = messages.get(state, ("…", "#aaa", False))
        self.after(0, lambda: self._set_status(msg, color))
        if pulse:
            self.after(0, self._start_pulse)
        else:
            self.after(0, self._stop_pulse)

    def _on_error(self, msg: str):
        self.after(0, lambda: self._set_status(f"⚠ {msg}", "#ff4444"))
        self.after(0, self._stop_pulse)

    def _set_status(self, msg: str, color: str):
        self.status_label.configure(text=msg, text_color=color)

    # ── Animation pulsante ──────────────────────────────────────────────

    def _start_pulse(self):
        if self._pulse_job:
            return
        self._animate_pulse()

    def _stop_pulse(self):
        if self._pulse_job:
            self.after_cancel(self._pulse_job)
            self._pulse_job = None
        try:
            self.pulse_frame.configure(fg_color="#1a3a2a")
        except Exception:
            pass

    def _animate_pulse(self):
        try:
            color = self.PULSE_COLORS[self._pulse_idx % len(self.PULSE_COLORS)]
            self.pulse_frame.configure(fg_color=color)
            self._pulse_idx += 1
            self._pulse_job  = self.after(120, self._animate_pulse)
        except Exception:
            self._pulse_job = None

    # ── Arrêt ───────────────────────────────────────────────────────────

    def stop(self):
        self._stop_pulse()
        if self._recorder:
            self._recorder.stop()
            self._recorder = None
        if self.on_close:
            self.on_close()
        self.destroy()


class _VoiceRecorder:
    """Thread d'écoute continue (interne à VoicePanel)."""

    def __init__(self, on_transcript, on_status, on_error):
        self.on_transcript = on_transcript
        self.on_status     = on_status
        self.on_error      = on_error
        self._running      = False

    def start(self):
        self._running = True
        threading.Thread(target=self._listen, daemon=True).start()

    def stop(self):
        self._running = False

    def _listen(self):
        recognizer = sr.Recognizer()
        recognizer.energy_threshold         = 300
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold          = 0.8

        try:
            mic = sr.Microphone()
        except Exception as e:
            self.on_error(f"Micro introuvable : {e}")
            self._running = False
            return

        self.on_status("calibrating")
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            self.on_status("ready")
            while self._running:
                try:
                    self.on_status("listening")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=20)
                    self.on_status("processing")
                    text  = recognizer.recognize_google(audio, language="fr-FR")
                    if text.strip():
                        self.on_transcript(text.strip())
                except sr.WaitTimeoutError:
                    pass
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    self.on_error(f"Erreur réseau : {e}")
                    break
                except Exception:
                    pass

        self._running = False
        self.on_status("stopped")


def make_voice_button(master, panel_ref: dict, right_panel, on_transcript=None) -> ctk.CTkButton:
    """Bouton 🎙 — ouvre/ferme le panneau vocal dans le panneau droit."""

    def toggle():
        if panel_ref.get("voice") is not None:
            panel_ref["voice"].stop()
            panel_ref["voice"] = None
            btn.configure(text="🎙", fg_color="#3a3a3a")
            return

        if not SR_AVAILABLE:
            _show_popup(master, "Module manquant.\npip install SpeechRecognition pyaudio")
            return

        def on_close():
            panel_ref["voice"] = None
            btn.configure(text="🎙", fg_color="#3a3a3a")

        vp = VoicePanel(right_panel, on_transcript=on_transcript, on_close=on_close)
        vp.pack(fill="both", expand=True, padx=4, pady=4)
        panel_ref["voice"] = vp
        btn.configure(text="🔴", fg_color="#aa2222")

    btn = ctk.CTkButton(
        master, text="🎙", width=35, height=35,
        fg_color="#3a3a3a", hover_color="#4a4a4a",
        command=toggle
    )
    return btn

# ─────────────────────────────────────────────
# DRAG (sash redimensionnable)
# ─────────────────────────────────────────────

def create_draggable_sash(container, right_panel):
    sash = ctk.CTkFrame(container, width=6, cursor="sb_h_double_arrow", fg_color="#3a3a3a")
    sash.pack(side="right", fill="y")
    _drag = {"x": 0, "width": 200}

    def on_press(e):
        _drag["x"]     = e.x_root
        _drag["width"] = right_panel.winfo_width()

    def on_drag(e):
        delta     = _drag["x"] - e.x_root
        new_width = max(100, min(500, _drag["width"] + delta))
        right_panel.configure(width=new_width)

    sash.bind("<ButtonPress-1>", on_press)
    sash.bind("<B1-Motion>",     on_drag)
    return sash


# ─────────────────────────────────────────────
# SYNTAX HIGHLIGHTING
# ─────────────────────────────────────────────

import re as _re

LANGUAGES = [
    "Auto-detect",
    "Python","JavaScript","TypeScript","HTML","CSS","SCSS",
    "SQL","JSON","YAML","XML","Bash","C","C++","C#",
    "Java","Go","Rust","PHP","Ruby","Swift","Kotlin",
    "R","MATLAB","Lua","Perl","Autre"
]
EXT_TO_LANG = {
    ".py":"Python",".js":"JavaScript",".ts":"TypeScript",
    ".html":"HTML",".htm":"HTML",".css":"CSS",".scss":"SCSS",
    ".sql":"SQL",".json":"JSON",".yaml":"YAML",".yml":"YAML",
    ".xml":"XML",".sh":"Bash",".bash":"Bash",
    ".c":"C",".h":"C",".cpp":"C++",".cc":"C++",".cs":"C#",
    ".java":"Java",".go":"Go",".rs":"Rust",".php":"PHP",
    ".rb":"Ruby",".swift":"Swift",".kt":"Kotlin",
    ".r":"R",".m":"MATLAB",".lua":"Lua",".pl":"Perl",
}

# Couleurs inspirées VS Code Dark+
SH = {
    "keyword":   "#569cd6",
    "builtin":   "#4ec9b0",
    "string":    "#ce9178",
    "comment":   "#6a9955",
    "number":    "#b5cea8",
    "decorator": "#dcdcaa",
    "function":  "#dcdcaa",
    "classname": "#4ec9b0",
    "tag":       "#4ec9b0",
    "attr":      "#9cdcfe",
    "selector":  "#d7ba7d",
    "property":  "#9cdcfe",
    "operator":  "#d4d4d4",
    # nouveaux
    "op_arith":  "#f08080",   # + - * / % **        rouge clair
    "op_comp":   "#d8a0df",   # == != < > <= >=      violet
    "op_logic":  "#569cd6",   # && || ! & | ^ ~      bleu
    "op_assign": "#c586c0",   # = += -= *= /= etc.   magenta
    "op_arrow":  "#4ec9b0",   # -> => :: .           cyan
    "bracket_r": "#ffd700",   # ( )                  or
    "bracket_s": "#da70d6",   # [ ]                  orchidée
    "bracket_c": "#179fff",   # { }                  bleu vif
}

SYNTAX_RULES = {
    "Python": [
        ("comment",   r"#[^\n]*"),
        ("string",    r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'),
        ("decorator", r"@\w+"),
        ("number",    r"\b(0x[0-9a-fA-F]+|\d+\.?\d*([eE][+-]?\d+)?)\b"),
        ("keyword",   r"\b(False|None|True|and|as|assert|async|await|break|class|continue"
                      r"|def|del|elif|else|except|finally|for|from|global|if|import|in|is"
                      r"|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b"),
        ("builtin",   r"\b(abs|all|any|bin|bool|bytes|callable|chr|dict|dir|divmod|enumerate"
                      r"|eval|exec|filter|float|format|frozenset|getattr|globals|hasattr|hash"
                      r"|help|hex|id|input|int|isinstance|issubclass|iter|len|list|locals|map"
                      r"|max|min|next|object|oct|open|ord|pow|print|property|range|repr"
                      r"|reversed|round|set|setattr|slice|sorted|staticmethod|str|sum|super"
                      r"|tuple|type|vars|zip)\b"),
        ("function",  r"\bdef\s+(\w+)"),
        ("classname", r"\bclass\s+(\w+)"),
    ],
    "JavaScript": [
        ("comment",   r"//[^\n]*|/\*[\s\S]*?\*/"),
        ("string",    r'(`[^`]*`|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'),
        ("number",    r"\b(0x[0-9a-fA-F]+|\d+\.?\d*)\b"),
        ("keyword",   r"\b(async|await|break|case|catch|class|const|continue|debugger|default"
                      r"|delete|do|else|export|extends|finally|for|from|function|if|import|in"
                      r"|instanceof|let|new|of|return|static|super|switch|this|throw|try"
                      r"|typeof|var|void|while|with|yield|null|undefined|true|false)\b"),
        ("builtin",   r"\b(console|Math|JSON|Object|Array|String|Number|Boolean|Date|RegExp"
                      r"|Error|Promise|Map|Set|Symbol|window|document|fetch|setTimeout"
                      r"|setInterval|clearTimeout|clearInterval)\b"),
        ("function",  r"\bfunction\s+(\w+)"),
    ],
    "HTML": [
        ("comment",   r"<!--[\s\S]*?-->"),
        ("string",    r'"[^"]*"|\'[^\']*\''),
        ("tag",       r"</?[a-zA-Z][a-zA-Z0-9]*|/?>"),
        ("attr",      r"\b[a-zA-Z][a-zA-Z0-9-]*(?=\s*=)"),
        ("number",    r"\b\d+\b"),
    ],
    "CSS": [
        ("comment",   r"/\*[\s\S]*?\*/"),
        ("string",    r'"[^"]*"|\'[^\']*\''),
        ("selector",  r"[.#]?[a-zA-Z][a-zA-Z0-9_-]*(?=\s*\{)"),
        ("property",  r"[a-zA-Z-]+(?=\s*:)"),
        ("number",    r"\b\d+\.?\d*(px|em|rem|%|vh|vw|pt|s|ms)?\b"),
        ("keyword",   r"\b(important|inherit|initial|unset|auto|none|block|inline|flex|grid"
                      r"|absolute|relative|fixed|sticky|bold|normal)\b"),
    ],
    "JSON": [
        ("string",    r'"(?:[^"\\]|\\.)*"'),
        ("number",    r"-?\b\d+\.?\d*([eE][+-]?\d+)?\b"),
        ("keyword",   r"\b(true|false|null)\b"),
    ],
    "SQL": [
        ("comment",   r"--[^\n]*|/\*[\s\S]*?\*/"),
        ("string",    r"'[^']*'"),
        ("keyword",   r"\b(SELECT|FROM|WHERE|INSERT|INTO|UPDATE|SET|DELETE|CREATE|DROP|ALTER"
                      r"|TABLE|INDEX|VIEW|JOIN|LEFT|RIGHT|INNER|OUTER|FULL|ON|AS|AND|OR|NOT"
                      r"|IN|IS|NULL|LIKE|ORDER|BY|GROUP|HAVING|LIMIT|OFFSET|DISTINCT|COUNT"
                      r"|SUM|AVG|MAX|MIN|UNION|ALL|EXISTS|CASE|WHEN|THEN|ELSE|END|PRIMARY"
                      r"|KEY|FOREIGN|REFERENCES|UNIQUE|DEFAULT|VALUES|RETURNING)\b"),
        ("number",    r"\b\d+\.?\d*\b"),
    ],
    "Bash": [
        ("comment",   r"#[^\n]*"),
        ("string",    r'"(?:[^"\\]|\\.)*"|\'[^\']*\''),
        ("keyword",   r"\b(if|then|else|elif|fi|for|while|do|done|case|esac|function"
                      r"|return|exit|in|echo|export|local|readonly|shift|source|trap|unset)\b"),
        ("builtin",   r"\b(cd|ls|pwd|mkdir|rm|cp|mv|cat|grep|sed|awk|find|chmod|chown"
                      r"|curl|wget|git|python|python3|pip|npm|node|bash|sh)\b"),
        ("number",    r"\b\d+\b"),
    ],
}

# ── Règles génériques partagées ──────────────────────────────────────────
_CLIKE_KW = (r"\b(auto|break|case|catch|class|const|continue|default|delete|do|else"
             r"|enum|explicit|extern|false|final|finally|for|friend|goto|if|inline"
             r"|namespace|new|nullptr|operator|override|private|protected|public"
             r"|return|sizeof|static|struct|switch|template|this|throw|true|try"
             r"|typedef|typename|union|using|virtual|void|volatile|while)\b")
_CLIKE_RULES = [
    ("comment",  r"//[^\n]*|/\*[\s\S]*?\*/"),
    ("string",   r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\''),
    ("number",   r"\b(0x[0-9a-fA-F]+|\d+\.?\d*([eE][+-]?\d+)?)\b"),
    ("keyword",  _CLIKE_KW),
]

# Langages supplémentaires (C-like)
for _lang in ("C", "C++", "C#", "Java", "Go", "Swift", "Kotlin", "PHP"):
    SYNTAX_RULES[_lang] = _CLIKE_RULES + [
        ("builtin", r"\b(print|println|printf|sprintf|fprintf|malloc|free|sizeof"
                    r"|string|int|float|double|bool|char|long|short|byte|uint|int32"
                    r"|int64|uint32|uint64|fmt|os|io|http|json|math|rand|time"
                    r"|System|Console|String|Integer|List|Map|Set|ArrayList|HashMap"
                    r"|echo|var_dump|isset|array_key_exists|count|strlen|substr"
                    r"|print|println|log|fmt\.Println|fmt\.Printf)\b"),
    ]

SYNTAX_RULES["TypeScript"] = SYNTAX_RULES["JavaScript"] + [
    ("keyword", r"\b(type|interface|enum|namespace|declare|abstract|readonly"
                r"|as|satisfies|infer|keyof|typeof|never|unknown|any)\b"),
]

SYNTAX_RULES["SCSS"] = SYNTAX_RULES["CSS"] + [
    ("keyword", r"@(mixin|include|extend|import|use|forward|each|for|if|else|while|function|return)\b"),
    ("builtin", r"\$[a-zA-Z_][a-zA-Z0-9_-]*"),
]

SYNTAX_RULES["YAML"] = [
    ("comment",  r"#[^\n]*"),
    ("string",   r'"[^"]*"|\'[^\']*\''),
    ("keyword",  r"^[\s]*[a-zA-Z_][a-zA-Z0-9_]*(?=\s*:)"),
    ("number",   r"\b(true|false|null|\d+\.?\d*)\b"),
]

SYNTAX_RULES["XML"] = [
    ("comment",  r"<!--[\s\S]*?-->"),
    ("string",   r'"[^"]*"|\'[^\']*\''),
    ("tag",      r"</?[a-zA-Z][a-zA-Z0-9:_-]*|/?>"),
    ("attr",     r"\b[a-zA-Z][a-zA-Z0-9:_-]*(?=\s*=)"),
]

SYNTAX_RULES["Rust"] = [
    ("comment",  r"//[^\n]*|/\*[\s\S]*?\*/"),
    ("string",   r'"(?:[^"\\]|\\.)*"|r#"[\s\S]*?"#'),
    ("number",   r"\b(0x[0-9a-fA-F_]+|0b[01_]+|\d[\d_]*\.?[\d_]*)\b"),
    ("keyword",  r"\b(as|async|await|break|const|continue|crate|dyn|else|enum|extern"
                 r"|false|fn|for|if|impl|in|let|loop|match|mod|move|mut|pub|ref|return"
                 r"|self|Self|static|struct|super|trait|true|type|unsafe|use|where|while)\b"),
    ("builtin",  r"\b(Option|Result|Some|None|Ok|Err|Vec|String|Box|Rc|Arc|Cell|RefCell"
                 r"|println!|print!|panic!|assert!|vec!|format!|todo!|unimplemented!)"),
]

SYNTAX_RULES["Ruby"] = [
    ("comment",  r"#[^\n]*"),
    ("string",   r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\''),
    ("number",   r"\b\d+\.?\d*\b"),
    ("keyword",  r"\b(BEGIN|END|alias|and|begin|break|case|class|def|defined|do|else"
                 r"|elsif|end|ensure|false|for|if|in|module|next|nil|not|or|redo|rescue"
                 r"|retry|return|self|super|then|true|undef|unless|until|when|while|yield)\b"),
    ("builtin",  r"\b(puts|print|p|pp|require|require_relative|attr_accessor|attr_reader"
                 r"|attr_writer|include|extend|raise|lambda|proc|Array|Hash|String|Integer"
                 r"|Float|Symbol|Range|Regexp|File|IO|Dir|Enumerable|Comparable)\b"),
]

SYNTAX_RULES["R"] = [
    ("comment",  r"#[^\n]*"),
    ("string",   r'"[^"]*"|\'[^\']*\''),
    ("number",   r"\b\d+\.?\d*(e[+-]?\d+)?[Li]?\b"),
    ("keyword",  r"\b(if|else|for|while|repeat|break|next|return|function|in|TRUE|FALSE|NULL"
                 r"|NA|NA_integer_|NA_real_|NA_complex_|NA_character_|Inf|NaN)\b"),
    ("builtin",  r"\b(c|list|data\.frame|matrix|array|vector|factor|seq|rep|length|nrow"
                 r"|ncol|dim|sum|mean|median|sd|var|print|cat|paste|paste0|sprintf|library"
                 r"|require|install\.packages|read\.csv|write\.csv|ggplot|lm|glm)\b"),
]

SYNTAX_RULES["Lua"] = [
    ("comment",  r"--[^\n]*|--\[\[[\s\S]*?\]\]"),
    ("string",   r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|\[\[[\s\S]*?\]\]'),
    ("number",   r"\b(0x[0-9a-fA-F]+|\d+\.?\d*)\b"),
    ("keyword",  r"\b(and|break|do|else|elseif|end|false|for|function|goto|if|in|local"
                 r"|nil|not|or|repeat|return|then|true|until|while)\b"),
    ("builtin",  r"\b(print|type|tostring|tonumber|pairs|ipairs|next|select|unpack"
                 r"|rawget|rawset|rawequal|rawlen|pcall|xpcall|error|assert|require"
                 r"|load|loadfile|dofile|collectgarbage|math|string|table|io|os|coroutine)\b"),
]

SYNTAX_RULES["Perl"] = [
    ("comment",  r"#[^\n]*"),
    ("string",   r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\''),
    ("number",   r"\b\d+\.?\d*\b"),
    ("keyword",  r"\b(if|elsif|else|unless|while|until|for|foreach|do|last|next|redo"
                 r"|return|sub|use|require|package|my|local|our|BEGIN|END|die|warn"
                 r"|print|say|chomp|chop|push|pop|shift|unshift|splice)\b"),
]

SYNTAX_RULES["MATLAB"] = [
    ("comment",  r"%[^\n]*"),
    ("string",   r"'[^'\n]*'"),
    ("number",   r"\b\d+\.?\d*([eE][+-]?\d+)?[ij]?\b"),
    ("keyword",  r"\b(break|case|catch|classdef|continue|else|elseif|end|for|function"
                 r"|global|if|otherwise|parfor|persistent|return|spmd|switch|try|while"
                 r"|true|false|NaN|Inf|pi|eps|nargin|nargout)\b"),
    ("builtin",  r"\b(disp|fprintf|sprintf|size|length|numel|zeros|ones|eye|rand|randn"
                 r"|linspace|plot|subplot|title|xlabel|ylabel|legend|grid|hold|figure"
                 r"|sum|prod|max|min|mean|std|sort|find|mod|abs|sqrt|exp|log|sin|cos|tan)\b"),
]

# ── Règles opérateurs/brackets (ajoutées à chaque langage) ──────────────
_OP_RULES = [
    ("op_assign", r"(?<![=!<>])=(?!=)|\+=|-=|\*=|/=|%=|\*\*=|//=|&=|\|=|\^=|<<=|>>="),
    ("op_comp",   r"==|!=|<=|>=|<(?!<)|>(?!>)"),
    ("op_logic",  r"&&|\|\||!(?!=)|\b(and|or|not|is|in)\b"),
    ("op_arith",  r"\*\*|//|[+\-*/%]"),
    ("op_arrow",  r"=>|->|::|\.\.\.|\.\."),
    ("bracket_r", r"[()]"),
    ("bracket_s", r"[\[\]]"),
    ("bracket_c", r"[{}]"),
]

# ── Fallback générique pour tout langage inconnu ─────────────────────────
_GENERIC_RULES = [
    ("comment",  r"(//|#)[^\n]*|/\*[\s\S]*?\*/|<!--[\s\S]*?-->"),
    ("string",   r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|`[^`]*`)'),
    ("number",   r"\b(0x[0-9a-fA-F]+|\d+\.?\d*([eE][+-]?\d+)?)\b"),
    ("keyword",  r"\b(if|else|for|while|do|return|function|class|import|export|from"
                 r"|const|let|var|def|end|begin|then|true|false|null|nil|none|new"
                 r"|this|self|static|public|private|protected|try|catch|finally"
                 r"|throw|raise|in|not|and|or|is|as|with|pass|break|continue)\b"),
] + _OP_RULES
SYNTAX_RULES["Autre"] = _GENERIC_RULES
SYNTAX_RULES["Auto-detect"] = _GENERIC_RULES


# Ajouter opérateurs/brackets à toutes les règles existantes
for _k in list(SYNTAX_RULES.keys()):
    if _k not in ("Autre", "Auto-detect"):
        SYNTAX_RULES[_k] = SYNTAX_RULES[_k] + _OP_RULES


def detect_lang_from_content(code: str) -> str:
    """Devine le langage à partir du contenu."""
    first = code.strip()[:200]
    if first.startswith("<?php"):          return "PHP"
    if first.startswith("<?xml"):          return "XML"
    if first.startswith("<!DOCTYPE") or first.startswith("<html"): return "HTML"
    if _re.search(r"^\s*import\s+\w|^\s*from\s+\w+\s+import", first, _re.M): return "Python"
    if _re.search(r"^\s*(const|let|var|function|=>|async\s+function)", first, _re.M): return "JavaScript"
    if _re.search(r"^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE)\s", first, _re.M|_re.I): return "SQL"
    if _re.search(r"^\s*[{\[]", first):  return "JSON"
    if _re.search(r"^---\s*$", first, _re.M): return "YAML"
    if _re.search(r"\bpackage\s+main\b|\bfunc\s+\w+", first): return "Go"
    if _re.search(r"\bfn\s+\w+|\blet\s+mut\b", first):        return "Rust"
    if _re.search(r"^#!/.*bash|^#!/.*sh", first):                    return "Bash"
    if _re.search(r"\bpublic\s+class\b|\bimport\s+java\.\b", first): return "Java"
    if _re.search(r"#include\s*<|\bstd::\w+|\bint\s+main\s*\(", first): return "C++"
    return "Autre"


class SyntaxHighlighter:
    """Coloration syntaxique temps réel pour CTkTextbox."""

    def __init__(self, textbox, lang_var):
        self.textbox  = textbox
        self.lang_var = lang_var
        self._text    = textbox._textbox   # widget Text tkinter sous-jacent
        self._job     = None
        self._setup_tags()

    def _setup_tags(self):
        for name, color in SH.items():
            self._text.tag_configure(name, foreground=color)

    def schedule(self, event=None):
        """Déclenche le highlighting avec un délai (évite le lag à chaque frappe)."""
        if self._job:
            self._text.after_cancel(self._job)
        self._job = self._text.after(80, self.apply)

    def apply(self, *_):
        self._job = None
        lang  = self.lang_var.get()

        # Auto-detect: guess from content
        if lang == "Auto-detect":
            code = self._text.get("1.0", "end-1c")
            lang = detect_lang_from_content(code)

        rules = SYNTAX_RULES.get(lang, SYNTAX_RULES["Autre"])
        code  = self._text.get("1.0", "end-1c")

        for tag in SH:
            self._text.tag_remove(tag, "1.0", "end")

        flags = _re.MULTILINE | (_re.IGNORECASE if lang == "SQL" else 0)
        for tag_name, pattern in rules:
            try:
                for m in _re.finditer(pattern, code, flags):
                    if tag_name in ("function", "classname") and m.lastindex:
                        s, e = m.start(1), m.end(1)
                    else:
                        s, e = m.start(), m.end()
                    self._text.tag_add(tag_name, f"1.0+{s}c", f"1.0+{e}c")
            except _re.error:
                pass


# ─────────────────────────────────────────────
# ÉDITEUR DE CODE (centre)
# ─────────────────────────────────────────────

def make_code_editor(master):
    """Éditeur de code avec syntaxe colorée, numéros de lignes et output."""
    frame = ctk.CTkFrame(master, fg_color=BG_DARK)
    frame.pack(fill="both", expand=True)

    # ── Toolbar ──────────────────────────────────────────────────────────
    toolbar = ctk.CTkFrame(frame, fg_color=BG_HEADER, height=38)
    toolbar.pack(fill="x")
    toolbar.pack_propagate(False)

    ctk.CTkLabel(toolbar, text="</> Code", font=("Arial", 13, "bold"),
                 text_color="#44aaee").pack(side="left", padx=12, pady=8)

    lang_var  = ctk.StringVar(value="Python")
    lang_menu = ctk.CTkOptionMenu(
        toolbar, values=LANGUAGES, variable=lang_var,
        width=116, height=28, fg_color="#2a2a2a",
        button_color="#3a3a3a", button_hover_color="#4a4a4a",
        command=lambda _: highlighter.apply()
    )
    lang_menu.pack(side="left", padx=8, pady=5)

    btn_cfg = dict(width=70, height=26, fg_color="#2a2a2a",
                   hover_color="#3a3a3a", font=("Arial", 11))

    def run_code():
        import subprocess, sys, tempfile, shutil

        code = editor.get("1.0", "end-1c")
        lang = lang_var.get()
        if lang == "Auto-detect":
            lang = detect_lang_from_content(code)

        status_label.configure(text=f"▶ {lang}…", text_color="#ffaa44")

        RUNNERS = {
            "Python":     ([sys.executable, "-c", "__CODE__"], False, ".py"),
            "JavaScript": (["node",       "-e", "__CODE__"],   False, ".js"),
            "TypeScript": (["ts-node",    "-e", "__CODE__"],   False, ".ts"),
            "Bash":       (["bash",       "-c", "__CODE__"],   False, ".sh"),
            "Ruby":       (["ruby",       "-e", "__CODE__"],   False, ".rb"),
            "Perl":       (["perl",       "-e", "__CODE__"],   False, ".pl"),
            "PHP":        (["php",        "-r", "__CODE__"],   False, ".php"),
            "Lua":        (["lua",        "__FILE__"],         True,  ".lua"),
            "R":          (["Rscript",    "__FILE__"],         True,  ".r"),
            "Go":         (["go",  "run", "__FILE__"],         True,  ".go"),
            "C":          (["gcc",  "__FILE__", "-o", "__EXE__"], True, ".c"),
            "C++":        (["g++",  "__FILE__", "-o", "__EXE__"], True, ".cpp"),
            "Rust":       (["rustc","__FILE__", "-o", "__EXE__"], True, ".rs"),
            "C#":         (["dotnet-script", "__FILE__"],      True,  ".cs"),
            "Swift":      (["swift",      "__FILE__"],         True,  ".swift"),
            "Kotlin":     (["kotlinc-jvm", "-script", "__FILE__"], True, ".kts"),
            "Java":       (["javac",      "__FILE__"],         True,  ".java"),
        }

        def _exec(cmd_list):
            try:
                r = subprocess.run(cmd_list, capture_output=True, text=True, timeout=15)
                return (r.stdout + r.stderr).strip() or "(aucune sortie)", r.returncode == 0
            except FileNotFoundError:
                return f"⚠ '{cmd_list[0]}' introuvable — installez-le et ajoutez-le au PATH.", False
            except subprocess.TimeoutExpired:
                return "⏱ Timeout (15s)", False
            except Exception as ex:
                return str(ex), False

        def _run():
            entry = RUNNERS.get(lang)
            if entry is None:
                frame.after(0, lambda: _show_output(
                    f"ℹ '{lang}' ne s'exécute pas directement ici.\n"
                    f"(HTML → navigateur, SQL → base de données, etc.)"))
                frame.after(0, lambda: status_label.configure(
                    text=f"ℹ {lang}", text_color="#aaaaaa"))
                return

            cmd_tpl, use_file, ext = entry
            tmp_dir = tempfile.mkdtemp()
            try:
                tmp  = os.path.join(tmp_dir, f"code{ext}")
                exe  = os.path.join(tmp_dir, "out.exe" if os.name == "nt" else "out")
                with open(tmp, "w", encoding="utf-8") as f:
                    f.write(code)

                def _build_cmd(tpl):
                    return [c.replace("__CODE__", code)
                             .replace("__FILE__", tmp)
                             .replace("__EXE__",  exe) for c in tpl]

                if not use_file:
                    out, ok = _exec(_build_cmd(cmd_tpl))

                elif lang in ("C", "C++", "Rust"):
                    cout, cok = _exec(_build_cmd(cmd_tpl))
                    if not cok:
                        out, ok = f"Erreur compilation :\n{cout}", False
                    else:
                        out, ok = _exec([exe])

                elif lang == "Java":
                    cout, cok = _exec(["javac", tmp])
                    if not cok:
                        out, ok = f"Erreur compilation :\n{cout}", False
                    else:
                        import re as _r
                        m = _r.search(r"public\s+class\s+(\w+)", code)
                        cname = m.group(1) if m else "code"
                        out, ok = _exec(["java", "-cp", tmp_dir, cname])
                else:
                    out, ok = _exec(_build_cmd(cmd_tpl))

            finally:
                shutil.rmtree(tmp_dir, ignore_errors=True)

            frame.after(0, lambda: _show_output(out))
            frame.after(0, lambda: status_label.configure(
                text="✓ Exécuté" if ok else "✗ Erreur",
                text_color="#44ee88" if ok else "#ff4444"))

        threading.Thread(target=_run, daemon=True).start()

    def clear_editor():
        editor.delete("1.0", "end")
        _show_output("")
        status_label.configure(text="")
        _update_lines()

    def copy_code():
        frame.clipboard_clear()
        frame.clipboard_append(editor.get("1.0", "end-1c"))
        status_label.configure(text="✓ Copié", text_color="#44ee88")
        frame.after(2000, lambda: status_label.configure(text=""))

    def save_code():
        import tkinter.filedialog as fd
        ext_map = {"Python":".py","JavaScript":".js","HTML":".html",
                   "CSS":".css","SQL":".sql","JSON":".json","Bash":".sh"}
        ext  = ext_map.get(lang_var.get(), ".txt")
        path = fd.asksaveasfilename(defaultextension=ext,
                                    filetypes=[(lang_var.get(), f"*{ext}"),("Tous","*.*")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(editor.get("1.0", "end-1c"))
            status_label.configure(text="✓ Sauvegardé", text_color="#44ee88")

    def open_file():
        import tkinter.filedialog as fd
        path = fd.askopenfilename(
            filetypes=[("Tous les fichiers","*.*"),
                       ("Code","*.py *.js *.ts *.html *.css *.sql *.json *.yaml *.xml *.sh *.c *.cpp *.cs *.java *.go *.rs *.rb *.php *.swift *.kt *.lua *.pl *.r *.m *.txt")])
        if path:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                code = f.read()
            editor.delete("1.0", "end")
            editor.insert("1.0", code)
            _update_lines()
            # Détecter la langue depuis l'extension
            import os as _os
            ext  = _os.path.splitext(path)[1].lower()
            lang = EXT_TO_LANG.get(ext, detect_lang_from_content(code))
            lang_var.set(lang)
            highlighter.apply()
            status_label.configure(text=f"✓ {os.path.basename(path)} [{lang}]",
                                   text_color="#44ee88")

    ctk.CTkButton(toolbar, text="▶ Run",    command=run_code,     **btn_cfg).pack(side="left", padx=2, pady=5)
    ctk.CTkButton(toolbar, text="📋 Copy",  command=copy_code,    **btn_cfg).pack(side="left", padx=2, pady=5)
    ctk.CTkButton(toolbar, text="💾 Save",  command=save_code,    **btn_cfg).pack(side="left", padx=2, pady=5)
    ctk.CTkButton(toolbar, text="📂 Open",  command=open_file,    **btn_cfg).pack(side="left", padx=2, pady=5)
    ctk.CTkButton(toolbar, text="🗑 Clear", command=clear_editor, **btn_cfg).pack(side="left", padx=2, pady=5)

    status_label = ctk.CTkLabel(toolbar, text="", font=("Arial", 11), text_color="#aaa")
    status_label.pack(side="left", padx=10)

    # ── Éditeur + numéros de lignes ───────────────────────────────────────
    editor_frame = ctk.CTkFrame(frame, fg_color="#1e1e1e")
    editor_frame.pack(fill="both", expand=True, padx=0, pady=(4, 0))

    line_numbers = ctk.CTkTextbox(
        editor_frame, width=46, fg_color="#252525",
        text_color="#4a4a4a", font=("Courier New", 13),
        state="disabled", corner_radius=0)
    line_numbers.pack(side="left", fill="y")

    editor = ctk.CTkTextbox(
        editor_frame, fg_color="#1e1e1e", text_color="#d4d4d4",
        font=("Courier New", 13), wrap="none",
        corner_radius=0, undo=True)
    editor.pack(side="left", fill="both", expand=True)
    editor.insert("1.0", "# Écrivez votre code ici\n")

    # Highlighter (créé après editor)
    highlighter = SyntaxHighlighter(editor, lang_var)

    def _update_lines(event=None):
        lines = editor.get("1.0", "end-1c").split("\n")
        nums  = "\n".join(str(i + 1) for i in range(len(lines)))
        line_numbers.configure(state="normal")
        line_numbers.delete("1.0", "end")
        line_numbers.insert("1.0", nums)
        line_numbers.configure(state="disabled")

    def _on_key(event=None):
        _update_lines()
        highlighter.schedule()

    editor.bind("<KeyRelease>", _on_key)
    _update_lines()
    highlighter.apply()

    # ── Output ────────────────────────────────────────────────────────────
    ctk.CTkLabel(frame, text="Output", font=("Arial", 11, "bold"),
                 text_color="#555", anchor="w").pack(fill="x", padx=8, pady=(6, 0))
    output_box = ctk.CTkTextbox(
        frame, height=110, fg_color="#141414",
        text_color="#44ee88", font=("Courier New", 12),
        state="disabled", corner_radius=8)
    output_box.pack(fill="x", padx=6, pady=(2, 6))

    def _show_output(text: str):
        output_box.configure(state="normal")
        output_box.delete("1.0", "end")
        output_box.insert("1.0", text)
        output_box.configure(state="disabled")

    frame.editor = editor
    return frame


# ─────────────────────────────────────────────
# CHAT (panneau droit)
# ─────────────────────────────────────────────

def make_chat_panel(master):
    """Chat intégré dans le panneau droit."""
    frame = ctk.CTkFrame(master, fg_color=BG_PANEL)
    frame.pack(fill="both", expand=True)

    title = ctk.CTkFrame(frame, fg_color=BG_HEADER, height=36)
    title.pack(fill="x")
    title.pack_propagate(False)
    ctk.CTkLabel(title, text="💬 Chat", font=("Arial", 13, "bold"),
                 text_color="#e0e0e0").pack(side="left", padx=10, pady=8)

    chat_box = ctk.CTkTextbox(frame, fg_color="#1e1e1e", text_color="#e0e0e0",
                               font=("Arial", 13), wrap="word",
                               state="disabled", corner_radius=0)
    chat_box.pack(fill="both", expand=True)

    input_frame = ctk.CTkFrame(frame, fg_color=BG_HEADER, height=44)
    input_frame.pack(fill="x", side="bottom")
    input_frame.pack_propagate(False)

    entry = ctk.CTkEntry(input_frame, placeholder_text="Message…",
                         font=("Arial", 12), corner_radius=8, height=30)
    entry.pack(side="left", fill="x", expand=True, padx=(8, 4), pady=7)

    def send(event=None):
        text = entry.get().strip()
        if not text:
            return
        entry.delete(0, "end")
        chat_box.configure(state="normal")
        chat_box.insert("end", f"Vous : {text}\n")
        chat_box.configure(state="disabled")
        chat_box.see("end")

    ctk.CTkButton(input_frame, text="➤", width=32, height=30,
                  fg_color="#1a5a3a", hover_color="#2a7a4a",
                  command=send).pack(side="left", padx=(0, 8), pady=7)
    entry.bind("<Return>", send)

    def inject_voice(text: str):
        entry.delete(0, "end")
        entry.insert(0, text)
        send()

    frame.inject_voice = inject_voice
    return frame


# legacy alias
def textarea(master):
    return make_code_editor(master)


# ─────────────────────────────────────────────
# POPUP utilitaire
# ─────────────────────────────────────────────

def _show_popup(master, message: str):
    win = ctk.CTkToplevel(master)
    win.title("Info")
    win.geometry("340x150")
    win.grab_set()
    ctk.CTkLabel(win, text=message, wraplength=300, font=("Arial", 13)).pack(pady=24)
    ctk.CTkButton(win, text="OK", width=80, command=win.destroy).pack()


# ─────────────────────────────────────────────
# BARRE DE FORCE DU MOT DE PASSE
# ─────────────────────────────────────────────

class PasswordStrengthBar(ctk.CTkFrame):
    COLORS = ["#ff4444", "#ff8800", "#ffcc00", "#44bb44", "#00cc88"]

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.bars = []
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x")
        for i in range(4):
            b = ctk.CTkFrame(row, width=48, height=6, corner_radius=3, fg_color="#444")
            b.pack(side="left", padx=2)
            self.bars.append(b)
        self.label = ctk.CTkLabel(self, text="", font=("Arial", 11), text_color="#aaa")
        self.label.pack()

    def update(self, pwd: str):
        if not pwd:
            for b in self.bars: b.configure(fg_color="#444")
            self.label.configure(text="")
            return
        score, label = password_strength(pwd)
        color = self.COLORS[score]
        for i, b in enumerate(self.bars):
            b.configure(fg_color=color if i < score else "#444")
        self.label.configure(text=label, text_color=color)


# ─────────────────────────────────────────────
# INSCRIPTION
# ─────────────────────────────────────────────

class RegisterFrame(ctk.CTkFrame):
    def __init__(self, master, on_success, **kwargs):
        super().__init__(master, **kwargs)
        self.on_success = on_success
        self.configure(fg_color=BG_PANEL, width=370, height=640)
        self._email_visible = False

        ctk.CTkLabel(self, text="Créer un Compte", font=("Arial", 20, "bold")).pack(pady=16)

        self.username = ctk.CTkEntry(self, placeholder_text="Nom d'utilisateur", width=240)
        self.username.pack(pady=6)

        email_row = ctk.CTkFrame(self, fg_color="transparent")
        email_row.pack(pady=6)
        self.email = ctk.CTkEntry(email_row, placeholder_text="Adresse email", width=198, show="*")
        self.email.pack(side="left", padx=(0, 6))
        self.eye_btn = ctk.CTkButton(
            email_row, text="👁", width=34, height=34,
            fg_color="#3a3a3a", hover_color="#4a4a4a",
            command=self.toggle_email_visibility
        )
        self.eye_btn.pack(side="left")

        self.password = ctk.CTkEntry(self, placeholder_text="Mot de passe", show="*", width=240)
        self.password.pack(pady=6)
        self.password.bind("<KeyRelease>", self._on_pwd_change)

        self.strength_bar = PasswordStrengthBar(self)
        self.strength_bar.pack(pady=2)

        self.confirm_password = ctk.CTkEntry(self, placeholder_text="Confirmer le mot de passe",
                                             show="*", width=240)
        self.confirm_password.pack(pady=6)

        self.remember_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self, text="Se souvenir de moi", variable=self.remember_var).pack(pady=4)

        self.error_label = ctk.CTkLabel(self, text="", text_color="#ff4444",
                                        font=("Arial", 12), wraplength=280)
        self.error_label.pack(pady=4)

        ctk.CTkButton(self, text="Créer le compte", width=240, command=self.save_user).pack(pady=8)
        ctk.CTkButton(self, text="Déjà un compte ? Se connecter",
                      fg_color="transparent", hover_color="#3a3a3a",
                      font=("Arial", 12), command=self.go_to_login).pack(pady=4)

    def _on_pwd_change(self, event=None):
        self.strength_bar.update(self.password.get())

    def toggle_email_visibility(self):
        self._email_visible = not self._email_visible
        self.email.configure(show="" if self._email_visible else "*")
        self.eye_btn.configure(text="🙈" if self._email_visible else "👁")

    def go_to_login(self):
        self.master.show_login_overlay()

    def save_user(self):
        user    = self.username.get().strip()
        email   = self.email.get().strip().lower()
        pwd     = self.password.get()
        confirm = self.confirm_password.get()

        if not user or not email or not pwd:
            self.error_label.configure(text="Tous les champs sont obligatoires.")
            return
        if not is_valid_email(email):
            self.error_label.configure(text="Adresse email invalide.")
            return
        if len(pwd) < 6:
            self.error_label.configure(text="Le mot de passe doit faire au moins 6 caractères.")
            return
        if pwd != confirm:
            self.error_label.configure(text="Les mots de passe ne correspondent pas.")
            return

        users = load_users()
        if any(u["username"].lower() == user.lower() for u in users):
            self.error_label.configure(text="Ce nom d'utilisateur est déjà pris.")
            return
        if any(u.get("email", "").strip().lower() == email for u in users):
            self.error_label.configure(text="Cette adresse email est déjà utilisée.")
            return

        data = {
            "id":              str(uuid.uuid4())[:8],
            "username":        user,
            "email":           email,
            "password":        hash_password(pwd),
            "avatar":          "👤",
            "login_history":   [],
            "failed_attempts": 0,
            "locked_until":    0
        }
        users.append(data)
        save_users(users)

        if self.remember_var.get():
            save_session(user)

        self.on_success(user, welcome=True)


# ─────────────────────────────────────────────
# CONNEXION
# ─────────────────────────────────────────────

class LoginOverlay(ctk.CTkFrame):
    def __init__(self, master, on_success, **kwargs):
        super().__init__(master, **kwargs)
        self.on_success = on_success
        self.configure(fg_color=BG_PANEL, width=370, height=460)

        ctk.CTkLabel(self, text="Connexion", font=("Arial", 20, "bold")).pack(pady=20)

        self.username = ctk.CTkEntry(self, placeholder_text="Nom d'utilisateur ou email", width=240)
        self.username.pack(pady=8)

        self.password = ctk.CTkEntry(self, placeholder_text="Mot de passe", show="*", width=240)
        self.password.pack(pady=8)

        self.remember_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self, text="Se souvenir de moi", variable=self.remember_var).pack(pady=4)

        self.error_label = ctk.CTkLabel(self, text="", text_color="#ff4444", font=("Arial", 12))
        self.error_label.pack(pady=4)

        ctk.CTkButton(self, text="Se connecter", width=240, command=self.login).pack(pady=8)
        ctk.CTkButton(self, text="Mot de passe oublié ?",
                      fg_color="transparent", hover_color="#3a3a3a",
                      font=("Arial", 12), command=self.forgot_password).pack(pady=2)
        ctk.CTkButton(self, text="Pas de compte ? S'inscrire",
                      fg_color="transparent", hover_color="#3a3a3a",
                      font=("Arial", 12), command=self.go_to_register).pack(pady=2)

    def go_to_register(self):
        self.master.show_register_screen()

    def forgot_password(self):
        self.master.show_forgot_password()

    def login(self):
        identifier = self.username.get().strip().lower()
        pwd        = self.password.get()

        if not identifier or not pwd:
            self.error_label.configure(text="Tous les champs sont obligatoires.")
            return

        users     = load_users()
        hashed    = hash_password(pwd)
        user_data = next(
            (u for u in users if
             u["username"].lower() == identifier or
             u.get("email", "").strip().lower() == identifier),
            None
        )

        if not user_data:
            self.error_label.configure(text="Identifiants incorrects.")
            return

        locked_until = user_data.get("locked_until", 0)
        if time.time() < locked_until:
            remaining = int(locked_until - time.time())
            self.error_label.configure(text=f"Compte bloqué. Réessayez dans {remaining}s.")
            return

        if user_data["password"] != hashed:
            user_data["failed_attempts"] = user_data.get("failed_attempts", 0) + 1
            if user_data["failed_attempts"] >= MAX_LOGIN_ATTEMPTS:
                user_data["locked_until"]    = time.time() + 60
                user_data["failed_attempts"] = 0
                save_users(users)
                self.error_label.configure(text="Trop de tentatives. Compte bloqué 60 secondes.")
            else:
                remaining = MAX_LOGIN_ATTEMPTS - user_data["failed_attempts"]
                save_users(users)
                self.error_label.configure(
                    text=f"Mot de passe incorrect. {remaining} tentative(s) restante(s).")
            return

        user_data["failed_attempts"] = 0
        user_data["locked_until"]    = 0
        save_users(users)
        record_login(user_data["username"])

        if self.remember_var.get():
            save_session(user_data["username"])

        self.on_success(user_data["username"], welcome=True)


# ─────────────────────────────────────────────
# MOT DE PASSE OUBLIÉ
# ─────────────────────────────────────────────

class ForgotPasswordFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=BG_PANEL, width=370, height=360)
        self._reset_code  = None
        self._target_user = None

        ctk.CTkLabel(self, text="Réinitialiser le mot de passe",
                     font=("Arial", 18, "bold")).pack(pady=20)

        self.email_entry = ctk.CTkEntry(self, placeholder_text="Votre adresse email", width=240)
        self.email_entry.pack(pady=8)

        self.code_entry = ctk.CTkEntry(self, placeholder_text="Code de réinitialisation", width=240)
        self.code_entry.pack(pady=8)
        self.code_entry.configure(state="disabled")

        self.new_pwd_entry = ctk.CTkEntry(self, placeholder_text="Nouveau mot de passe",
                                          show="*", width=240)
        self.new_pwd_entry.pack(pady=8)
        self.new_pwd_entry.configure(state="disabled")

        self.info_label = ctk.CTkLabel(self, text="", text_color="#aaaaaa",
                                       font=("Arial", 12), wraplength=280)
        self.info_label.pack(pady=4)

        self.action_btn = ctk.CTkButton(self, text="Envoyer le code", width=240,
                                        command=self.send_code)
        self.action_btn.pack(pady=8)

        ctk.CTkButton(self, text="← Retour à la connexion",
                      fg_color="transparent", hover_color="#3a3a3a",
                      font=("Arial", 12), command=self.go_back).pack(pady=4)

    def go_back(self):
        self.master.show_login_overlay()

    def send_code(self):
        email = self.email_entry.get().strip().lower()
        if not email:
            self.info_label.configure(text="Entrez votre email.", text_color="#ff4444")
            return
        users = load_users()
        user  = next((u for u in users if u.get("email", "").strip().lower() == email), None)
        if not user:
            self.info_label.configure(text="Aucun compte associé à cet email.",
                                      text_color="#ff4444")
            return
        self._reset_code  = "".join(random.choices(string.digits, k=6))
        self._target_user = user["username"]
        self.info_label.configure(
            text=f"Code : {self._reset_code}\n(En production, envoyé par email.)",
            text_color="#44bb44"
        )
        self.code_entry.configure(state="normal")
        self.new_pwd_entry.configure(state="normal")
        self.action_btn.configure(text="Confirmer", command=self.confirm_reset)

    def confirm_reset(self):
        code    = self.code_entry.get().strip()
        new_pwd = self.new_pwd_entry.get()
        if code != self._reset_code:
            self.info_label.configure(text="Code incorrect.", text_color="#ff4444")
            return
        if len(new_pwd) < 6:
            self.info_label.configure(text="Mot de passe trop court (6 min).",
                                      text_color="#ff4444")
            return
        users = load_users()
        for u in users:
            if u["username"] == self._target_user:
                u["password"] = hash_password(new_pwd)
                break
        save_users(users)
        self.info_label.configure(text="Mot de passe mis à jour !", text_color="#44bb44")
        self.action_btn.configure(state="disabled")
        self.master.after(2000, self.master.show_login_overlay)


# ─────────────────────────────────────────────
# PAGE DE PROFIL
# ─────────────────────────────────────────────

class ProfileFrame(ctk.CTkFrame):
    AVATARS = ["👤", "🧑", "👩", "🧔", "👨‍💻", "🧑‍🎨", "🦊", "🐼", "🤖", "🦁"]

    def __init__(self, master, username, on_close, **kwargs):
        super().__init__(master, **kwargs)
        self.username = username
        self.on_close = on_close
        self.configure(fg_color=BG_PANEL, width=400, height=580)

        users     = load_users()
        self.user = next((u for u in users if u["username"] == username), {})

        ctk.CTkLabel(self, text="Mon Profil", font=("Arial", 20, "bold")).pack(pady=16)

        self.avatar_label = ctk.CTkLabel(self, text=self.user.get("avatar", "👤"),
                                         font=("Arial", 48))
        self.avatar_label.pack()

        avatar_row = ctk.CTkFrame(self, fg_color="transparent")
        avatar_row.pack(pady=4)
        for av in self.AVATARS:
            ctk.CTkButton(avatar_row, text=av, width=32, height=32,
                          fg_color="transparent", hover_color="#3a3a3a",
                          font=("Arial", 18),
                          command=lambda a=av: self.set_avatar(a)).pack(side="left", padx=1)

        ctk.CTkLabel(self, text=f"@{username}", font=("Arial", 14),
                     text_color="#aaa").pack(pady=4)

        ctk.CTkLabel(self, text="Modifier l'email", font=("Arial", 13, "bold"),
                     anchor="w").pack(fill="x", padx=30, pady=(10, 2))
        self.new_email = ctk.CTkEntry(self, placeholder_text="Nouvel email", width=260)
        self.new_email.pack()

        ctk.CTkLabel(self, text="Modifier le mot de passe", font=("Arial", 13, "bold"),
                     anchor="w").pack(fill="x", padx=30, pady=(10, 2))
        self.new_pwd = ctk.CTkEntry(self, placeholder_text="Nouveau mot de passe",
                                    show="*", width=260)
        self.new_pwd.pack()
        self.new_pwd.bind("<KeyRelease>", self._on_pwd_change)
        self.strength_bar = PasswordStrengthBar(self)
        self.strength_bar.pack(pady=2)

        self.msg_label = ctk.CTkLabel(self, text="", font=("Arial", 12), text_color="#44bb44")
        self.msg_label.pack(pady=4)

        ctk.CTkButton(self, text="Sauvegarder", width=260, command=self.save_changes).pack(pady=6)

        history = self.user.get("login_history", [])
        if history:
            ctk.CTkLabel(self, text="Dernières connexions", font=("Arial", 13, "bold"),
                         anchor="w").pack(fill="x", padx=30, pady=(10, 2))
            for entry in reversed(history):
                ctk.CTkLabel(self, text=f"🕐 {entry}", font=("Arial", 11),
                             text_color="#aaa").pack()

        ctk.CTkButton(self, text="✕ Fermer", fg_color="transparent",
                      hover_color="#3a3a3a", command=self.on_close).pack(pady=10)

    def _on_pwd_change(self, event=None):
        self.strength_bar.update(self.new_pwd.get())

    def set_avatar(self, avatar: str):
        self.avatar_label.configure(text=avatar)
        users = load_users()
        for u in users:
            if u["username"] == self.username:
                u["avatar"] = avatar
                break
        save_users(users)
        self.master.update_avatar(avatar)

    def save_changes(self):
        users     = load_users()
        new_email = self.new_email.get().strip().lower()
        new_pwd   = self.new_pwd.get()
        changed   = False

        for u in users:
            if u["username"] == self.username:
                if new_email:
                    if not is_valid_email(new_email):
                        self.msg_label.configure(text="Email invalide.", text_color="#ff4444")
                        return
                    if any(x.get("email", "").strip().lower() == new_email
                           and x["username"] != self.username for x in users):
                        self.msg_label.configure(text="Email déjà utilisé.", text_color="#ff4444")
                        return
                    u["email"] = new_email
                    changed = True
                if new_pwd:
                    if len(new_pwd) < 6:
                        self.msg_label.configure(text="Mot de passe trop court.",
                                                 text_color="#ff4444")
                        return
                    u["password"] = hash_password(new_pwd)
                    changed = True
                break

        if changed:
            save_users(users)
            self.msg_label.configure(text="Modifications sauvegardées ✓", text_color="#44bb44")
            self.new_email.delete(0, "end")
            self.new_pwd.delete(0, "end")
            self.strength_bar.update("")
        else:
            self.msg_label.configure(text="Aucune modification.", text_color="#aaa")



# ─────────────────────────────────────────────
# SYSTÈME D'AMIS
# ─────────────────────────────────────────────

def load_friends() -> dict:
    if os.path.exists("friends.json"):
        with open("friends.json", "r") as f:
            return json.load(f)
    return {}

def save_friends(data: dict):
    with open("friends.json", "w") as f:
        json.dump(data, f, indent=4)

def get_friends(username: str) -> list:
    data = load_friends()
    return data.get(username, {}).get("friends", [])

def get_requests_received(username: str) -> list:
    data = load_friends()
    return data.get(username, {}).get("requests_in", [])

def get_requests_sent(username: str) -> list:
    data = load_friends()
    return data.get(username, {}).get("requests_out", [])

def send_friend_request(from_user: str, to_user: str) -> str:
    data = load_friends()
    for u in [from_user, to_user]:
        if u not in data:
            data[u] = {"friends": [], "requests_in": [], "requests_out": []}
    if to_user in data[from_user]["friends"]:
        return "already_friends"
    if to_user in data[from_user]["requests_out"]:
        return "already_sent"
    if to_user in data[from_user]["requests_in"]:
        return "already_received"
    data[from_user]["requests_out"].append(to_user)
    data[to_user]["requests_in"].append(from_user)
    save_friends(data)
    return "sent"

def accept_friend_request(username: str, from_user: str):
    data = load_friends()
    for u in [username, from_user]:
        if u not in data:
            data[u] = {"friends": [], "requests_in": [], "requests_out": []}
    if from_user in data[username]["requests_in"]:
        data[username]["requests_in"].remove(from_user)
    if username in data[from_user]["requests_out"]:
        data[from_user]["requests_out"].remove(username)
    if from_user not in data[username]["friends"]:
        data[username]["friends"].append(from_user)
    if username not in data[from_user]["friends"]:
        data[from_user]["friends"].append(username)
    save_friends(data)

def reject_friend_request(username: str, from_user: str):
    data = load_friends()
    if username in data and from_user in data[username]["requests_in"]:
        data[username]["requests_in"].remove(from_user)
    if from_user in data and username in data[from_user]["requests_out"]:
        data[from_user]["requests_out"].remove(username)
    save_friends(data)

def remove_friend(username: str, friend: str):
    data = load_friends()
    for u, other in [(username, friend), (friend, username)]:
        if u in data and other in data[u]["friends"]:
            data[u]["friends"].remove(other)
    save_friends(data)


class FriendsPage(ctk.CTkFrame):
    """Page dédiée au système d'amis."""

    def __init__(self, master, username: str, on_close, **kwargs):
        super().__init__(master, **kwargs)
        self.username = username
        self.on_close = on_close
        self.configure(fg_color=BG_PANEL, width=480, height=580)

        # ── Titre ──────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=BG_HEADER, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="👥  Mes Amis",
                     font=("Arial", 18, "bold"), text_color="#e0e0e0").pack(side="left", padx=16, pady=12)
        ctk.CTkButton(header, text="✕", width=30, height=30,
                      fg_color="transparent", hover_color="#3a3a3a",
                      command=self._close).pack(side="right", padx=10, pady=10)

        # ── Tabs ───────────────────────────────────────────────────────
        tab_row = ctk.CTkFrame(self, fg_color="#222")
        tab_row.pack(fill="x", pady=(8, 0))

        self._tab_btns = {}
        for label, key in [("👥 Amis", "friends"), ("🔔 Demandes", "requests"), ("🔍 Chercher", "search")]:
            b = ctk.CTkButton(tab_row, text=label, width=130,
                              fg_color="#333", hover_color="#444",
                              command=lambda k=key: self._show_tab(k))
            b.pack(side="left", padx=4, pady=6)
            self._tab_btns[key] = b

        # ── Contenu ────────────────────────────────────────────────────
        self.content = ctk.CTkFrame(self, fg_color=BG_PANEL)
        self.content.pack(fill="both", expand=True, padx=10, pady=10)

        self._show_tab("friends")

    def _close(self):
        self.on_close()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()
        for b in self._tab_btns.values():
            b.configure(fg_color="#333")

    # ── TAB AMIS ───────────────────────────────────────────────────────

    def _show_tab(self, key: str):
        self._clear_content()
        self._tab_btns[key].configure(fg_color="#1a5a3a")
        if key == "friends":
            self._build_friends()
        elif key == "requests":
            self._build_requests()
        elif key == "search":
            self._build_search()

    def _build_friends(self):
        friends = get_friends(self.username)
        users   = load_users()

        if not friends:
            ctk.CTkLabel(self.content, text="Vous n'avez pas encore d'amis.",
                         text_color="#666", font=("Arial", 13)).pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(self.content, fg_color=BG_PANEL)
        scroll.pack(fill="both", expand=True)

        for f in friends:
            udata  = next((u for u in users if u["username"] == f), {})
            avatar = udata.get("avatar", "👤")
            row    = ctk.CTkFrame(scroll, fg_color="#333", corner_radius=10)
            row.pack(fill="x", pady=4, padx=4)

            ctk.CTkLabel(row, text=f"{avatar}  {f}",
                         font=("Arial", 14), width=200, anchor="w").pack(side="left", padx=12, pady=10)
            ctk.CTkButton(row, text="Supprimer", width=90,
                          fg_color="#6a1a1a", hover_color="#8a2a2a",
                          command=lambda friend=f: self._remove(friend)).pack(side="right", padx=8, pady=8)

    def _remove(self, friend: str):
        remove_friend(self.username, friend)
        self._show_tab("friends")

    # ── TAB DEMANDES ───────────────────────────────────────────────────

    def _build_requests(self):
        received = get_requests_received(self.username)
        sent     = get_requests_sent(self.username)
        users    = load_users()

        scroll = ctk.CTkScrollableFrame(self.content, fg_color=BG_PANEL)
        scroll.pack(fill="both", expand=True)

        if received:
            ctk.CTkLabel(scroll, text="Demandes reçues",
                         font=("Arial", 13, "bold"), text_color="#44aaee").pack(anchor="w", pady=(8,4))
            for f in received:
                udata  = next((u for u in users if u["username"] == f), {})
                avatar = udata.get("avatar", "👤")
                row    = ctk.CTkFrame(scroll, fg_color="#1a2a3a", corner_radius=10)
                row.pack(fill="x", pady=3, padx=4)
                ctk.CTkLabel(row, text=f"{avatar}  {f}",
                             font=("Arial", 13), anchor="w", width=160).pack(side="left", padx=10, pady=8)
                ctk.CTkButton(row, text="✓ Accepter", width=90,
                              fg_color="#1a6a3a", hover_color="#2a8a4a",
                              command=lambda fr=f: self._accept(fr)).pack(side="right", padx=4, pady=6)
                ctk.CTkButton(row, text="✗ Refuser", width=80,
                              fg_color="#6a1a1a", hover_color="#8a2a2a",
                              command=lambda fr=f: self._reject(fr)).pack(side="right", padx=4, pady=6)

        if sent:
            ctk.CTkLabel(scroll, text="Demandes envoyées",
                         font=("Arial", 13, "bold"), text_color="#aaaaaa").pack(anchor="w", pady=(16,4))
            for f in sent:
                udata  = next((u for u in users if u["username"] == f), {})
                avatar = udata.get("avatar", "👤")
                row    = ctk.CTkFrame(scroll, fg_color="#2a2a2a", corner_radius=10)
                row.pack(fill="x", pady=3, padx=4)
                ctk.CTkLabel(row, text=f"{avatar}  {f}  —  En attente…",
                             font=("Arial", 13), text_color="#888",
                             anchor="w").pack(side="left", padx=10, pady=10)

        if not received and not sent:
            ctk.CTkLabel(scroll, text="Aucune demande en cours.",
                         text_color="#666", font=("Arial", 13)).pack(pady=40)

    def _accept(self, from_user: str):
        accept_friend_request(self.username, from_user)
        self._show_tab("requests")

    def _reject(self, from_user: str):
        reject_friend_request(self.username, from_user)
        self._show_tab("requests")

    # ── TAB RECHERCHE ──────────────────────────────────────────────────

    def _build_search(self):
        search_row = ctk.CTkFrame(self.content, fg_color="transparent")
        search_row.pack(fill="x", pady=(8, 4))

        self._search_entry = ctk.CTkEntry(search_row, placeholder_text="Nom d'utilisateur…",
                                          width=260, font=("Arial", 13))
        self._search_entry.pack(side="left", padx=(0, 8))
        ctk.CTkButton(search_row, text="🔍 Chercher", width=110,
                      command=self._do_search).pack(side="left")
        self._search_entry.bind("<Return>", lambda e: self._do_search())

        self._search_results = ctk.CTkFrame(self.content, fg_color="transparent")
        self._search_results.pack(fill="both", expand=True)

    def _do_search(self):
        query = self._search_entry.get().strip().lower()
        for w in self._search_results.winfo_children():
            w.destroy()
        if not query:
            return

        users   = load_users()
        friends = get_friends(self.username)
        sent    = get_requests_sent(self.username)
        results = [u for u in users
                   if query in u["username"].lower() and u["username"] != self.username]

        if not results:
            ctk.CTkLabel(self._search_results, text="Aucun utilisateur trouvé.",
                         text_color="#666", font=("Arial", 13)).pack(pady=20)
            return

        for u in results[:10]:
            uname  = u["username"]
            avatar = u.get("avatar", "👤")
            row    = ctk.CTkFrame(self._search_results, fg_color="#333", corner_radius=10)
            row.pack(fill="x", pady=4, padx=4)
            ctk.CTkLabel(row, text=f"{avatar}  {uname}",
                         font=("Arial", 14), anchor="w", width=200).pack(side="left", padx=12, pady=10)

            if uname in friends:
                ctk.CTkLabel(row, text="✓ Ami", text_color="#44ee88",
                             font=("Arial", 12)).pack(side="right", padx=12)
            elif uname in sent:
                ctk.CTkLabel(row, text="⏳ Envoyée", text_color="#aaa",
                             font=("Arial", 12)).pack(side="right", padx=12)
            else:
                ctk.CTkButton(row, text="➕ Ajouter", width=90,
                              fg_color="#1a5a8a", hover_color="#2a6a9a",
                              command=lambda un=uname, r=row: self._send_request(un, r)
                              ).pack(side="right", padx=8, pady=8)

    def _send_request(self, to_user: str, row):
        result = send_friend_request(self.username, to_user)
        msg_map = {
            "sent":             ("⏳ Envoyée", "#aaa"),
            "already_friends":  ("✓ Ami",     "#44ee88"),
            "already_sent":     ("⏳ Envoyée", "#aaa"),
            "already_received": ("✓ Reçue",   "#44aaee"),
        }
        text, color = msg_map.get(result, ("…", "#aaa"))
        for w in row.winfo_children():
            if isinstance(w, ctk.CTkButton):
                w.destroy()
        ctk.CTkLabel(row, text=text, text_color=color,
                     font=("Arial", 12)).pack(side="right", padx=12)

# ─────────────────────────────────────────────
# BANNIÈRE DE BIENVENUE
# ─────────────────────────────────────────────

class WelcomeBanner(ctk.CTkFrame):
    def __init__(self, master, username, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="#1a3a2a", corner_radius=10)
        users  = load_users()
        user   = next((u for u in users if u["username"] == username), {})
        avatar = user.get("avatar", "👤")
        hour   = dt.now().hour
        greet  = "Bonjour" if hour < 12 else ("Bon après-midi" if hour < 18 else "Bonsoir")
        ctk.CTkLabel(self, text=f"{avatar}  {greet}, {username} !",
                     font=("Arial", 15, "bold"), text_color="#44ee88").pack(padx=20, pady=10)
        master.after(4000, self.destroy)


# ─────────────────────────────────────────────
# APP PRINCIPALE
# ─────────────────────────────────────────────

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ChatCode")
        self.geometry("900x600")
        self.configure(fg_color=BG_DARK)
        self.current_user   = None
        self.auth_overlay   = None
        self._inactivity_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── HEADER ──
        self.header = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color=BG_HEADER)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)

        self.login_toggle = ctk.CTkButton(
            self.header, text="Login", width=100, command=self.toggle_login
        )
        self.login_toggle.pack(side="left", padx=20, pady=14)

        self.avatar_label = ctk.CTkLabel(self.header, text="", font=("Arial", 20), cursor="hand2")
        self.avatar_label.pack(side="left", padx=(10, 4))
        self.avatar_label.bind("<Button-1>", lambda e: self.show_profile())

        self.user_label = ctk.CTkLabel(self.header, text="", font=("Arial", 13), cursor="hand2")
        self.user_label.pack(side="left")
        self.user_label.bind("<Button-1>", lambda e: self.show_profile())

        self.friends_btn = ctk.CTkButton(
            self.header, text="👥 Amis", width=90,
            fg_color="#1a3a5a", hover_color="#2a4a6a",
            command=self.show_friends
        )
        self.friends_btn.pack(side="left", padx=(16, 0), pady=14)
        self.friends_btn.pack_forget()   # caché tant que non connecté

        ctk.CTkButton(self.header, text="X", width=35, fg_color="#c42b1c",
                      command=self.destroy).pack(side="right", padx=20)

        # ── BODY ── (créé avant les boutons qui ont besoin de right_panel)
        self.body_container = ctk.CTkFrame(self, fg_color=BG_DARK)
        self.body_container.grid(row=1, column=0, sticky="nsew")

        self.right_panel = ctk.CTkFrame(self.body_container, width=280, fg_color=BG_PANEL)
        self.right_panel.pack(side="right", fill="y")
        self.right_panel.pack_propagate(False)

        # ── Boutons header qui dépendent de right_panel ──
        self._voice_panel_ref = {"voice": None}
        make_voice_button(
            self.header,
            panel_ref=self._voice_panel_ref,
            right_panel=self.right_panel,
            on_transcript=self._on_voice_transcript
        ).pack(side="right", padx=4)

        self._cam_panel_ref = {"cam": None}
        make_camera_button(
            self.header,
            panel_ref=self._cam_panel_ref,
            right_panel=self.right_panel,
            on_photo=self._on_photo_captured
        ).pack(side="right", padx=4)

        # ── Chat dans le panneau droit (en haut, au-dessus de cam/vocal) ──
        self._chat_frame = make_chat_panel(self.right_panel)

        create_draggable_sash(self.body_container, self.right_panel)

        # ── Éditeur de code au centre ──
        self.main_container = ctk.CTkFrame(self.body_container, fg_color=BG_DARK)
        self.main_container.pack(side="left", fill="both", expand=True)

        make_code_editor(self.main_container)

        self.bind_all("<Motion>",   self._reset_inactivity)
        self.bind_all("<KeyPress>", self._reset_inactivity)

        # ── Session persistante ──
        session = load_session()
        if session.get("username"):
            users = load_users()
            if any(u["username"] == session["username"] for u in users):
                self.unlock_app(session["username"], welcome=False)
                return

        if load_users():
            self.show_login_overlay()
        else:
            self.show_register_screen()

    def _reset_inactivity(self, event=None):
        if self.current_user is None:
            return
        if self._inactivity_id:
            self.after_cancel(self._inactivity_id)
        self._inactivity_id = self.after(INACTIVITY_TIMEOUT, self._auto_logout)

    def _auto_logout(self):
        if self.current_user:
            self.logout()

    def show_register_screen(self):
        self._clear_auth_overlay()
        self.auth_overlay = RegisterFrame(master=self, on_success=self.unlock_app,
                                          corner_radius=15, border_width=2)
        self.auth_overlay.place(relx=0.5, rely=0.5, anchor="center")

    def show_login_overlay(self):
        self._clear_auth_overlay()
        self.auth_overlay = LoginOverlay(master=self, on_success=self.unlock_app,
                                         corner_radius=15, border_width=2)
        self.auth_overlay.place(relx=0.5, rely=0.5, anchor="center")

    def show_forgot_password(self):
        self._clear_auth_overlay()
        self.auth_overlay = ForgotPasswordFrame(master=self, corner_radius=15, border_width=2)
        self.auth_overlay.place(relx=0.5, rely=0.5, anchor="center")

    def show_profile(self):
        if not self.current_user:
            return
        self._clear_auth_overlay()
        self.auth_overlay = ProfileFrame(master=self, username=self.current_user,
                                         on_close=self._clear_auth_overlay,
                                         corner_radius=15, border_width=2)
        self.auth_overlay.place(relx=0.5, rely=0.5, anchor="center")

    def show_friends(self):
        if not self.current_user:
            return
        self._clear_auth_overlay()
        self.auth_overlay = FriendsPage(
            master=self, username=self.current_user,
            on_close=self._clear_auth_overlay,
            corner_radius=15, border_width=2
        )
        self.auth_overlay.place(relx=0.5, rely=0.5, anchor="center")

    def toggle_login(self):
        if self.auth_overlay is not None:
            self._clear_auth_overlay()
        elif self.current_user is None:
            self.show_login_overlay()

    def _clear_auth_overlay(self):
        if self.auth_overlay is not None:
            self.auth_overlay.destroy()
            self.auth_overlay = None

    def unlock_app(self, username: str, welcome: bool = True):
        self.current_user = username
        self._clear_auth_overlay()
        users  = load_users()
        user   = next((u for u in users if u["username"] == username), {})
        avatar = user.get("avatar", "👤")
        self.avatar_label.configure(text=avatar)
        self.user_label.configure(text=username)
        self.login_toggle.configure(text="Déconnexion", command=self.logout)
        self.friends_btn.pack(side="left", padx=(16, 0), pady=14)
        if welcome:
            banner = WelcomeBanner(self.main_container, username)
            banner.place(relx=0.5, rely=0.05, anchor="n")
        self._reset_inactivity()

    def update_avatar(self, avatar: str):
        self.avatar_label.configure(text=avatar)

    def logout(self):
        self.current_user = None
        if self._inactivity_id:
            self.after_cancel(self._inactivity_id)
            self._inactivity_id = None
        clear_session()
        self.avatar_label.configure(text="")
        self.user_label.configure(text="")
        self.login_toggle.configure(text="Login", command=self.toggle_login)
        self.friends_btn.pack_forget()
        self.show_login_overlay()

    def _on_photo_captured(self, path: str):
        banner = ctk.CTkLabel(self.main_container,
                              text=f"📷  Photo sauvegardée : {path}",
                              fg_color="#1a3a2a", corner_radius=8,
                              font=("Arial", 12), text_color="#44ee88")
        banner.place(relx=0.5, rely=0.96, anchor="s")
        self.after(3500, banner.destroy)

    def _on_voice_transcript(self, text: str):
        """Envoie le texte vocal directement dans le chat."""
        if hasattr(self, "_chat_frame") and self._chat_frame:
            try:
                self._chat_frame.inject_voice(text)
            except Exception:
                pass


if __name__ == "__main__":
    app = App()
    app.mainloop()
