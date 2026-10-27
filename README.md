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
git clone https://github.com/your-username/polyglot-syntax-validator.git
cd polyglot-syntax-validator
pip install pygments tree-sitter-language-pack
python validator.py
