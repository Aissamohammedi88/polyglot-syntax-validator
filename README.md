# polyglot-syntax-validator
A multilingual code editor with real-time syntax validation powered by tree-sitter and Pygments. Supports Python, JSON, JavaScript, TypeScript, Go, Rust, C/C++, Java, SQL, HTML, CSS, and 40+ more languages.
# Polyglot Syntax Validator

A multilingual code editor with real-time syntax validation powered by tree-sitter and Pygments.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey)

## Overview

Polyglot Syntax Validator is a lightweight desktop code editor that detects the programming language of your code and validates its syntax as you type. It combines Pygments for lexical analysis and language detection with tree-sitter for accurate, grammar-based syntax error detection across 40+ languages.

Whether you're debugging a snippet, checking a configuration file, or exploring a new language, this tool gives you instant feedback: syntax score, error locations, and highlighted issues — all in a single window.

## Features

- **Automatic language detection** — Filename-based, heuristic, and Pygments `guess_lexer` fallback
- **Tree-sitter syntax validation** — Grammar-based error detection for 40+ languages including Python, JavaScript, TypeScript, Go, Rust, C/C++, Java, SQL, HTML, CSS, and more
- **Python & JSON native checkers** — Uses `ast.parse` and `json.loads` for precise error positions
- **Syntax score** — 0–100% score based on error count and code length
- **Error highlighting** — Errors are underlined in red directly in the editor
- **Language selector** — Manual override with "Auto" detection mode
- **Line numbers** — Synchronized with the editor scroll
- **Copy-paste workflow** — No file required; paste code, get feedback

## Requirements

- Python 3.10+
- Tkinter (included with most Python distributions; on Linux you may need `sudo apt install python3-tk`)
- Internet connection for the first `tree-sitter-language-pack` install

## Installation

```bash
git clone https://github.com/Aissamohammedi88/polyglot-syntax-validator.git
cd polyglot-syntax-validator
    On Debian/Ubuntu, if Tkinter is missing: sudo apt install python3-tk

Usage

    Launch the application: python validator.py

    Paste or type your code in the editor

    Select a language from the dropdown (or leave "Auto" for automatic detection)

    The editor validates syntax after 500ms of inactivity

    Check the Console panel for detailed error messages and the status bar for the syntax score

Supported Languages (partial list)
Language	Detection	Validation
Python	✅ Filename / heuristic	✅ ast.parse
JSON	✅ Content-based	✅ json.loads
JavaScript / TypeScript	✅ Heuristic / Pygments	✅ tree-sitter
Go, Rust, C/C++, Java	✅ Heuristic / Pygments	✅ tree-sitter
HTML, CSS, SQL	✅ Heuristic / Pygments	✅ tree-sitter
YAML, TOML, Dockerfile, Makefile	✅ Pygments	✅ tree-sitter (if available)
30+ additional languages	✅ Pygments	⚠️ depends on tree-sitter grammar availability
How It Works
text

User input
    │
    ▼
Language detection (filename → heuristic → Pygments guess_lexer)
    │
    ▼
┌─────────────────────────────────────────────┐
│ Python → ast.parse                          │
│ JSON   → json.loads                         │
│ Others → tree-sitter parser (grammar pack)  │
└─────────────────────────────────────────────┘
    │
    ▼
Error extraction (byte offset → char offset conversion)
    │
    ▼
Syntax score + error highlighting + console output

The syntax score is computed as:
text

score = max(0, 100 - sum(18 + min(12, 120 // line_count) for each error))

A score of 100% means no syntax errors were detected. The score is — when the language is not supported or the editor is empty.
Project Structure
text

polyglot-syntax-validator/
├── validator.py       # Main application (single file)
├── README.md
├── LICENSE
└── .gitignore

Limitations

    Tree-sitter grammar coverage — Not all languages supported by Pygments have a corresponding grammar in tree-sitter-language-pack. Unsupported languages show ⚠️ Grammaire non disponible in the console.

    No semantic analysis — Only syntax is validated. Type errors, undefined variables, etc. are not detected.

    Desktop only — Requires a graphical environment; no headless mode.

    First-run download — tree-sitter-language-pack downloads grammars on first import, which may take a moment.

Contributing

Issues and pull requests are welcome. Please open an issue first to discuss major changes.

    Fork the repository

    Create a feature branch (git checkout -b feature/your-feature)

    Commit your changes (git commit -am 'Add feature')

    Push to the branch (git push origin feature/your-feature)

    Open a Pull Request

License

This project is licensed under the MIT License. See LICENSE for details.

Built by Aissa Mohammedi (DGK) — Nexus Quantum
text

## LICENSE (MIT

MIT License

Copyright (c) 2026 Aissa Mohammedi (DGK)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
text

