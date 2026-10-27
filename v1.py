import astimport json
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from pygments import lex
from pygments.lexers import (
get_all_lexers,
get_lexer_by_name,
get_lexer_for_filename,
guess_lexer,
)
from pygments.token import Token
from tree_sitter_language_pack import get_parser

GRAMMAR_ALIASES = {
"py": "python", "python3": "python", "py3": "python",
"javascript": "javascript", "js": "javascript", "jsx": "javascript",
"typescript": "typescript", "ts": "typescript", "tsx": "tsx",
"html": "html", "xml": "xml", "css": "css", "scss": "scss",
"json": "json", "json5": "json", "yaml": "yaml", "yml": "yaml",
"java": "java", "c": "c", "cpp": "cpp", "c++": "cpp", "cxx": "cpp",
"csharp": "c_sharp", "c#": "c_sharp", "cs": "c_sharp",
"go": "go", "golang": "go", "rust": "rust", "rs": "rust",
"ruby": "ruby", "rb": "ruby", "php": "php",
"bash": "bash", "sh": "bash", "shell": "bash",
"sql": "sql", "swift": "swift", "kotlin": "kotlin", "kt": "kotlin",
"lua": "lua", "perl": "perl", "r": "r", "dart": "dart",
"scala": "scala", "haskell": "haskell", "elixir": "elixir",
"erlang": "erlang", "clojure": "clojure", "clj": "clojure",
"ocaml": "ocaml", "objc": "objc", "objective-c": "objc",
"toml": "toml", "docker": "dockerfile", "dockerfile": "dockerfile",
"make": "make", "makefile": "make", "markdown": "markdown", "md": "markdown",
"graphql": "graphql", "vue": "vue",
}

def build_language_list():
aliases = set()
for _name, lexer_aliases, _filenames, _mimetypes in get_all_lexers():
aliases.update(lexer_aliases)
return ["Auto"] + sorted(aliases, key=str.lower)

def heuristic_language(source):
text = source.strip()
low = text.lower()
if not text: return None
if low.startswith("<!doctype html") or re.search(r"<\s*(html|head|body|div|script|style|p|span)\b", low): return "html"
if text.startswith("<?xml"): return "xml"
if text.startswith("<?php"): return "php"
if text.startswith("{") or text.startswith("["):
try:
json.loads(text); return "json"
except json.JSONDecodeError: pass
if re.search(r"^\s*(def|class)\s+\w+", text, re.MULTILINE): return "python"
if re.search(r"^\s*(import\s+\w+|from\s+\w+\s+import\s+)", text, re.MULTILINE): return "python"
if re.search(r"\b(const|let|var)\s+\w+\s*=", text): return "javascript"
if re.search(r"\b(function\s+\w+|console\.log\s*\()", text): return "javascript"
if re.search(r"\bpublic\s+class\s+\w+", text): return "java"
if re.search(r"^\s*#include\s*[<\"]", text, re.MULTILINE): return "cpp"
if re.search(r"\bpackage\s+main\b|\bfunc\s+main\s*\(", text): return "go"
if re.search(r"\bfn\s+main\s*\(", text): return "rust"
if re.search(r"^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE TABLE)\b", text, re.IGNORECASE): return "sql"
if re.search(r"^[\w.#:[\] >+~,()-]+\s*\{[^{}]*:[^{}]*\}", text, re.MULTILINE): return "css"
return None

def detect_language(source, filename=None):
if filename:
try:
lexer = get_lexer_for_filename(filename, source)
if lexer.aliases: return lexer.aliases[0]
except Exception: pass
quick = heuristic_language(source)
if quick: return quick
if not source.strip(): return "text"
try:
lexer = guess_lexer(source)
if lexer.aliases: return lexer.aliases[0]
except Exception: pass
return "text"

def grammar_name(language):
key = language.lower().strip()
return GRAMMAR_ALIASES.get(key, key)

def byte_to_char_offset(source_bytes, byte_offset):
byte_offset = max(0, min(byte_offset, len(source_bytes)))
return len(source_bytes[:byte_offset].decode("utf-8", errors="ignore"))

def python_syntax_errors(source):
try:
ast.parse(source)
return []
except SyntaxError as exc:
lines = source.splitlines(keepends=True)
row = max(1, exc.lineno or 1)
column = max(1, exc.offset or 1)
before = sum(len(line) for line in lines[: row - 1])
start = before + column - 1
if row <= len(lines):
current_line = lines[row - 1]
line_end = before + len(current_line.rstrip("\r\n"))
else:
line_end = len(source)
if exc.end_lineno == exc.lineno and exc.end_offset:
end = before + exc.end_offset - 1
else:
end = start + 1
start = max(0, min(start, len(source)))
end = max(start + 1, min(end, max(len(source), start + 1)))
if line_end > start: end = min(end, line_end)
return [{"start": start, "end": end, "message": exc.msg or "Erreur Python"}]

def json_syntax_errors(source):
try:
json.loads(source)
return []
except json.JSONDecodeError as exc:
start = max(0, min(exc.pos, len(source)))
return [{"start": start, "end": min(len(source), start + 1), "message": exc.msg}]

def tree_sitter_errors(source, language):
grammar = grammar_name(language)
try:
parser = get_parser(grammar)
except Exception:
return None
source_bytes = source.encode("utf-8")
tree = parser.parse(source_bytes)
found = []
stack = [tree.root_node]
while stack and len(found) < 200:
node = stack.pop()
if not getattr(node, "has_error", False) and not getattr(node, "is_missing", False): continue
if getattr(node, "is_missing", False):
start = byte_to_char_offset(source_bytes, node.start_byte)
found.append({"start": start, "end": min(len(source), start + 1), "message": f"Élément manquant : {node.type}"})
continue
if node.type == "ERROR":
start = byte_to_char_offset(source_bytes, node.start_byte)
end = byte_to_char_offset(source_bytes, node.end_byte)
found.append({"start": start, "end": max(start + 1, end), "message": "Syntaxe non reconnue"})
continue
stack.extend(reversed(node.children))
return sorted({(i["start"], i["end"], i["message"]): i for i in found}.values(), key=lambda x: (x["start"], x["end"]))

def inspect_code(source, language):
if not source.strip(): return [], False
if language in {"python", "py", "python3", "py3"}: return python_syntax_errors(source), True
if language in {"json"}: return json_syntax_errors(source), True
issues = tree_sitter_errors(source, language)
return (issues, True) if issues is not None else ([], False)

def syntax_score(source, issues, checked):
if not checked or not source.strip(): return None
if not issues: return 100
line_count = max(1, len(source.splitlines()))
penalty = sum(18 + min(12, 120 // line_count) for _ in issues)
return max(0, 100 - min(100, penalty))

class CodeEditor(tk.Tk):
def __init__(self):
super().__init__()
self.title("Éditeur multilangage — débogage syntaxique")
self.geometry("1150x760")
self.filename = None
self.pending_refresh = None
self.languages = build_language_list()
self.language_choice = tk.StringVar(value="Auto")
self.detected_language = tk.StringVar(value="Langage : —")
self.score_text = tk.StringVar(value="Score syntaxique : —")
self.location_text = tk.StringVar(value="Ligne 1, colonne 1")
self.state_text = tk.StringVar(value="Prêt")
self.configure(bg="#111827")
self.create_widgets()
self.configure_tags()
self.bind_shortcuts()
self.editor.insert("1.0", "# Colle ton code ici.\n")
self.schedule_refresh()

def create_widgets(self):
toolbar = ttk.Frame(self, padding=8)
toolbar.pack(fill="x")
ttk.Button(toolbar, text="Ouvrir", command=self.open_file).pack(side="left", padx=3)
ttk.Button(toolbar, text="Vérifier", command=self.refresh).pack(side="left", padx=3)
ttk.Label(toolbar, text="Langage :").pack(side="left", padx=(20, 5))
self.language_menu = ttk.Combobox(toolbar, textvariable=self.language_choice, values=self.languages, width=24, state="readonly")
self.language_menu.pack(side="left", padx=3)
self.language_menu.bind("<<ComboboxSelected>>", lambda _: self.refresh())

main = ttk.PanedWindow(self, orient="vertical")
main.pack(fill="both", expand=True, padx=8, pady=5)
editor_frame = ttk.Frame(main)
main.add(editor_frame, weight=4)

self.line_numbers = tk.Text(editor_frame, width=5, padx=6, borderwidth=0, state="disabled", bg="#1f2937", fg="#9ca3af", font=("TkFixedFont", 11))
self.line_numbers.grid(row=0, column=0, sticky="ns")
self.editor = tk.Text(editor_frame, undo=True, wrap="none", font=("TkFixedFont", 11), bg="#111827", fg="#e5e7eb", insertbackground="white", padx=8, pady=8, borderwidth=0, tabs=("4c",))
self.editor.grid(row=0, column=1, sticky="nsew")

scrollbar_y = ttk.Scrollbar(editor_frame, orient="vertical", command=self.editor.yview)
scrollbar_y.grid(row=0, column=2, sticky="ns")
self.editor.configure(yscrollcommand=scrollbar_y.set)
editor_frame.rowconfigure(0, weight=1)
editor_frame.columnconfigure(1, weight=1)

console_frame = ttk.Frame(main, padding=5)
main.add(console_frame, weight=1)
ttk.Label(console_frame, text="Console").pack(anchor="w")
self.console = tk.Text(console_frame, height=8, wrap="word", state="disabled", font=("TkFixedFont", 10), bg="#0b1220", fg="#d1d5db", padx=8, pady=6, borderwidth=0)
self.console.pack(fill="both", expand=True)

status = ttk.Frame(self, padding=(8, 4))
status.pack(fill="x")
ttk.Label(status, textvariable=self.detected_language).pack(side="left", padx=(0, 16))
ttk.Label(status, textvariable=self.score_text).pack(side="left", padx=(0, 16))
ttk.Label(status, textvariable=self.location_text).pack(side="left", padx=(0, 16))
ttk.Label(status, textvariable=self.state_text).pack(side="right")

self.editor.bind("<KeyRelease>", self.on_editor_change)
self.editor.bind("<ButtonRelease-1>", self.update_cursor_location)

def configure_tags(self):
self.editor.tag_configure("error", background="#7f1d1d", underline=True)
self.editor.tag_configure("keyword", foreground="#c084fc")
self.editor.tag_configure("string", foreground="#86efac")
self.editor.tag_configure("comment", foreground="#6b7280")
self.editor.tag_configure("number", foreground="#fbbf24")

def bind_shortcuts(self):
self.bind("<Control-o>", lambda _: self.open_file())
self.bind("<Control-Return>", lambda _: self.refresh())

def on_editor_change(self, _=None):
self.update_line_numbers()
self.update_cursor_location()
self.schedule_refresh()

def update_line_numbers(self):
last_line = int(self.editor.index("end-1c").split(".")[0])
numbers = "\n".join(str(n) for n in range(1, last_line + 1))
self.line_numbers.configure(state="normal")
self.line_numbers.delete("1.0", "end")
self.line_numbers.insert("1.0", numbers)
self.line_numbers.configure(state="disabled")
try: self.line_numbers.yview_moveto(self.editor.yview()[0])
except Exception: pass

def update_cursor_location(self, _=None):
line, column = self.editor.index("insert").split(".")
self.location_text.set(f"Ligne {line}, colonne {int(column) + 1}")

def schedule_refresh(self):
if self.pending_refresh is not None: self.after_cancel(self.pending_refresh)
self.pending_refresh = self.after(500, self.refresh)

def get_source(self): return self.editor.get("1.0", "end-1c")

def get_language(self, source):
selected = self.language_choice.get()
return selected.lower() if selected.lower() != "auto" else detect_language(source, self.filename)

def refresh(self):
self.pending_refresh = None
source = self.get_source()
language = self.get_language(source)
self.detected_language.set(f"Langage : {language or '—'}")
self.editor.tag_remove("error", "1.0", "end")

if not source.strip():
self.score_text.set("Score : —")
return

# Coloration (version simplifiée pour éviter le crash)
try:
lexer = get_lexer_by_name(language if language != "text" else "text")
offset = 0
for token_type, value in lex(source, lexer):
if token_type in Token.Comment: self.editor.tag_add("comment", f"1.0 + {offset} chars", f"1.0 + {offset + len(value)} chars")
elif token_type in Token.Keyword: self.editor.tag_add("keyword", f"1.0 + {offset} chars", f"1.0 + {offset + len(value)} chars")
offset += len(value)
except Exception: pass

issues, checked = inspect_code(source, language)
score = syntax_score(source, issues, checked)
self.score_text.set(f"Score : {score} %" if score is not None else "Score : —")
# Marquage des erreurs
for issue in issues:
self.editor.tag_add("error", f"1.0 + {issue['start']} chars", f"1.0 + {issue['end']} chars")
# Console
self.console.configure(state="normal")
self.console.delete("1.0", "end")
if not checked:
self.console.insert("end", f"⚠️ Grammaire non disponible pour {language}. Impossible de vérifier.\n")
elif not issues:
self.console.insert("end", f"✅ Aucune erreur détectée en {language}.\n", "success")
else:
for issue in issues:
self.console.insert("end", f"❌ {issue['message']}\n", "error")
self.console.configure(state="disabled")
self.update_line_numbers()

def open_file(self):
path = filedialog.askopenfilename()
if not path: return
self.filename = path
try:
content = Path(path).read_text(encoding="utf-8")
self.editor.delete("1.0", "end")
self.editor.insert("1.0", content)
self.refresh()
except Exception as e:
messagebox.showerror("Erreur", str(e))

if __name__ == "__main__":
app = CodeEditor()
app.mainloop()
