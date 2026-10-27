import astimport json
import re
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

# ═══════════════════════════════════════════════════════════════════════════
# LOGIQUE D'ANALYSE (conservée de ta version)
# ═══════════════════════════════════════════════════════════════════════════

def heuristic_language(source):
text = source.strip()
low = text.lower()
if not text: return "text"
if low.startswith("<!doctype html") or re.search(r"<\s*(html|head|body|div|script|style|p|span)\b", low): return "html"
if text.startswith("<?xml"): return "xml"
if text.startswith("<?php"): return "php"
if text.startswith("{") or text.startswith("["):
try:
json.loads(text); return "json"
except json.JSONDecodeError: pass
if re.search(r"^\s*(def|class)\s+\w+", text, re.MULTILINE): return "python"
if re.search(r"\b(const|let|var)\s+\w+\s*=", text): return "javascript"
if re.search(r"\bpublic\s+class\s+\w+", text): return "java"
if re.search(r"^\s*#include\s*[<\"]", text, re.MULTILINE): return "cpp"
if re.search(r"\bpackage\s+main\b|\bfunc\s+main\s*\(", text): return "go"
if re.search(r"\bfn\s+main\s*\(", text): return "rust"
return "text"

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
return [{"line": row, "column": column, "message": exc.msg or "Erreur Python", "start": start}]

def json_syntax_errors(source):
try:
json.loads(source)
return []
except json.JSONDecodeError as exc:
return [{"line": exc.lineno, "column": exc.colno, "message": exc.msg, "start": exc.pos}]

def inspect_code(source, language):
if not source.strip(): return [], False
if language in {"python", "py", "python3", "py3"}: return python_syntax_errors(source), True
if language == "json": return json_syntax_errors(source), True
return [], False # Pas de tree-sitter sur a-Shell

def syntax_score(source, issues, checked):
if not checked or not source.strip(): return None
if not issues: return 100
penalty = sum(15 for _ in issues)
return max(0, 100 - penalty)

# ═══════════════════════════════════════════════════════════════════════════
# INTERFACE HTML (remplace Tkinter)
# ═══════════════════════════════════════════════════════════════════════════

HTML = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>NEXUS Editor</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#111827;color:#e5e7eb;font-family:monospace;height:100vh;display:flex;flex-direction:column;overflow:hidden}
.header{background:#1f2937;padding:10px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;border-bottom:1px solid #374151}
.header button{background:#3b82f6;color:#fff;border:none;padding:8px 16px;border-radius:6px;font-weight:bold;font-family:inherit;font-size:14px}
.header button:active{background:#2563eb}
.header select{background:#111827;color:#e5e7eb;border:1px solid #374151;padding:8px;border-radius:6px;font-family:inherit}
.header .status{color:#9ca3af;font-size:12px;margin-left:auto}
.editor-container{flex:1;display:flex;overflow:hidden}
.line-numbers{background:#1f2937;color:#6b7280;padding:10px 8px;text-align:right;font-size:14px;line-height:1.5;overflow:hidden;user-select:none;min-width:40px}
#editor{flex:1;background:#111827;color:#e5e7eb;border:none;padding:10px;font-family:monospace;font-size:14px;line-height:1.5;resize:none;outline:none;overflow:auto}
.console{background:#0b1220;border-top:1px solid #374151;padding:10px;height:150px;overflow-y:auto;font-size:13px;line-height:1.5}
.console .error{color:#f87171}
.console .success{color:#4ade80}
.console .warning{color:#fbbf24}
</style>
</head>
<body>
<div class="header">
<button onclick="check()">Vérifier</button>
<button onclick="clearAll()">Effacer</button>
<select id="lang" onchange="check()">
<option value="auto">Auto</option>
<option value="python">Python</option>
<option value="json">JSON</option>
<option value="javascript">JavaScript</option>
<option value="html">HTML</option>
<option value="css">CSS</option>
</select>
<span class="status" id="status">Prêt</span>
</div>
<div class="editor-container">
<div class="line-numbers" id="lines">1</div>
<textarea id="editor" spellcheck="false" placeholder="Colle ton code ici..."></textarea>
</div>
<div class="console" id="console">> En attente...</div>
<script>
const editor=document.getElementById('editor');
const lines=document.getElementById('lines');
const consoleEl=document.getElementById('console');
const statusEl=document.getElementById('status');

function updateLines(){
const count=editor.value.split('\n').length;
let html='';
for(let i=1;i<=count;i++) html+=i+'<br>';
lines.innerHTML=html;
}
editor.addEventListener('input',updateLines);
editor.addEventListener('scroll',()=>{lines.scrollTop=editor.scrollTop;});

async function check(){
const code=editor.value;
const lang=document.getElementById('lang').value;
statusEl.textContent='Analyse...';
const res=await fetch('/analyze',{
method:'POST',
headers:{'Content-Type':'application/json'},
body:JSON.stringify({code,language:lang})
});
const data=await res.json();
statusEl.textContent=data.language.toUpperCase()+' | Score: '+(data.score!==null?data.score+'%':'—');
let html='';
if(data.issues.length===0){
html='<div class="success">✅ Aucune erreur détectée.</div>';
}else{
data.issues.forEach(i=>{
html+=`<div class="error">❌ Ligne ${i.line}, Col ${i.column}: ${i.message}</div>`;
});
}
consoleEl.innerHTML=html;
}
function clearAll(){editor.value='';updateLines();consoleEl.innerHTML='> En attente...';statusEl.textContent='Prêt';}
updateLines();
</script>
</body>
</html>"""

# ═══════════════════════════════════════════════════════════════════════════
# SERVEUR HTTP
# ═══════════════════════════════════════════════════════════════════════════

class Handler(BaseHTTPRequestHandler):
def log_message(self, *args): pass

def do_GET(self):
self.send_response(200)
self.send_header("Content-Type", "text/html; charset=utf-8")
self.end_headers()
self.wfile.write(HTML.encode())

def do_POST(self):
if self.path == "/analyze":
length = int(self.headers.get('Content-Length', 0))
data = json.loads(self.rfile.read(length).decode())
code = data.get("code", "")
lang_choice = data.get("language", "auto")

if lang_choice == "auto":
language = heuristic_language(code)
else:
language = lang_choice

issues, checked = inspect_code(code, language)
score = syntax_score(code, issues, checked)

result = {
"language": language,
"issues": issues,
"score": score,
"checked": checked
}

self.send_response(200)
self.send_header("Content-Type", "application/json")
self.end_headers()
self.wfile.write(json.dumps(result).encode())

if __name__ == "__main__":
PORT = 8080
print(f"🌐 Serveur lancé sur http://localhost:{PORT}")
print("Ouvre Safari et va à cette adresse.")
print("Ctrl+C pour arrêter.")

server = HTTPServer(("0.0.0.0", PORT), Handler)
try:
server.serve_forever()
except KeyboardInterrupt:
print("\nArrêt.")
