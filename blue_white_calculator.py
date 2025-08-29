#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blue-White Calculator (Tkinter)
Author: ChatGPT
Description:
  A clean, modern-looking calculator GUI in a blue & white theme.
  - Safe arithmetic evaluation (supports +, -, *, /, %, **, parentheses)
  - Keyboard support (Enter = "=", Backspace = delete, Esc = clear)
  - Nice layout with responsive button sizing
"""
import tkinter as tk
from tkinter import ttk
import ast
import operator as op

# ---------- Safe evaluator ----------
# Supported operators
_ALLOWED_BINOP = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
}
_ALLOWED_UNARY = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}

def _eval_ast(node):
    if isinstance(node, ast.Expression):
        return _eval_ast(node.body)
    elif isinstance(node, ast.Constant):  # numbers
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Unsupported constant")
    elif isinstance(node, ast.Num):  # for older Python
        return node.n
    elif isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOP:
        left = _eval_ast(node.left)
        right = _eval_ast(node.right)
        return _ALLOWED_BINOP[type(node.op)](left, right)
    elif isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        operand = _eval_ast(node.operand)
        return _ALLOWED_UNARY[type(node.op)](operand)
    elif isinstance(node, ast.Expr):
        return _eval_ast(node.value)
    elif isinstance(node, ast.Tuple):
        # Reject tuples
        raise ValueError("Unsupported expression")
    else:
        raise ValueError("Unsupported expression")

def safe_eval(expr: str):
    """
    Evaluate a math expression safely using a restricted AST.
    Supports: +, -, *, /, %, **, parentheses, unary +/-
    """
    # Map pretty symbols to Python ops
    sanitized = (
        expr.replace('×', '*')
            .replace('÷', '/')
            .replace('−', '-')
    )
    # Caret ^ -> ** (power)
    sanitized = sanitized.replace('^', '**')
    # Remove whitespace
    sanitized = ''.join(sanitized.split())

    if not sanitized:
        return 0

    # Parse and evaluate
    tree = ast.parse(sanitized, mode='eval')
    return _eval_ast(tree)

# ---------- UI ----------
class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("เครื่องคิดเลข - Blue & White")
        self.configure(bg="#f5f9ff")
        self.resizable(False, False)

        # Colors / theme
        self.COLOR_BG = "#f5f9ff"
        self.COLOR_PANEL = "#e6f0ff"
        self.COLOR_BLUE = "#2563eb"
        self.COLOR_BLUE_DARK = "#1d4ed8"
        self.COLOR_TEXT = "#0f172a"
        self.COLOR_WHITE = "#ffffff"

        # Fonts
        self.FONT_DISPLAY = ("Segoe UI", 26, "bold")
        self.FONT_BTN = ("Segoe UI", 14, "bold")
        self.FONT_HDR = ("Segoe UI", 12, "bold")

        # Header bar
        header = tk.Frame(self, bg=self.COLOR_BLUE, height=46)
        header.pack(fill="x", side="top")
        tk.Label(
            header, text="เครื่องคิดเลข", fg=self.COLOR_WHITE, bg=self.COLOR_BLUE,
            font=("Segoe UI", 16, "bold"), pady=6
        ).pack(side="left", padx=14)

        # Container
        container = tk.Frame(self, bg=self.COLOR_BG, padx=14, pady=14)
        container.pack(fill="both", expand=True)

        # Display
        display_wrap = tk.Frame(container, bg=self.COLOR_BG)
        display_wrap.grid(row=0, column=0, sticky="ew")
        self.display_var = tk.StringVar(value="")
        self.display = tk.Entry(
            display_wrap, textvariable=self.display_var, justify="right",
            bd=0, relief="flat", font=self.FONT_DISPLAY,
        )
        self.display.configure(bg=self.COLOR_WHITE, fg=self.COLOR_TEXT, insertbackground=self.COLOR_TEXT)
        self.display.pack(fill="x", padx=4, pady=(0, 12), ipady=12)

        # Hint
        hint = tk.Label(
            display_wrap,
            text="คีย์ลัด: Enter=คำนวณ  •  Esc=ล้าง  •  Backspace=ลบทีละตัว",
            bg=self.COLOR_BG, fg="#334155", font=self.FONT_HDR
        )
        hint.pack(anchor="e", pady=(0, 10))

        # Buttons
        btns = tk.Frame(container, bg=self.COLOR_BG)
        btns.grid(row=1, column=0, sticky="nsew")
        for i in range(5):
            btns.grid_rowconfigure(i, weight=1, minsize=64)
        for j in range(4):
            btns.grid_columnconfigure(j, weight=1, minsize=78)

        # Button definitions: text, row, col, kind
        # kind: "op" (blue), "eq" (primary), "ctrl" (light), "num" (white)
        buttons = [
            ("C",   0, 0, "ctrl"), ("⌫",  0, 1, "ctrl"), ("%",  0, 2, "op"),  ("÷", 0, 3, "op"),
            ("7",   1, 0, "num"),  ("8",  1, 1, "num"),  ("9",  1, 2, "num"), ("×", 1, 3, "op"),
            ("4",   2, 0, "num"),  ("5",  2, 1, "num"),  ("6",  2, 2, "num"), ("−", 2, 3, "op"),
            ("1",   3, 0, "num"),  ("2",  3, 1, "num"),  ("3",  3, 2, "num"), ("+", 3, 3, "op"),
            ("0",  4, 1, "num"),  (".",  4, 2, "num"), ("=", 4, 3, "eq"),
        ]

        for (text, r, c, kind) in buttons:
            self._make_button(btns, text, r, c, kind)

        # Keyboard bindings
        self.bind("<Return>", lambda e: self._calculate())
        self.bind("=", lambda e: self._calculate())
        self.bind("<Escape>", lambda e: self._clear())
        self.bind("<BackSpace>", lambda e: self._backspace())
        for ch in "0123456789+-*/().%":
            self.bind(ch, self._type_char)
        # Support '^' for power (will show as caret; allowed by evaluator)
        self.bind("^", self._type_char)

        # Focus the display
        self.display.focus_set()

        # Center the window on screen
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = int((sw - w) / 2)
        y = int((sh - h) / 2.2)
        self.geometry(f"+{x}+{y}")

    # ---------- Button/UI helpers ----------
    def _make_button(self, parent, text, r, c, kind):
        if kind == "eq":
            bg = self.COLOR_BLUE_DARK
            fg = self.COLOR_WHITE
            active = "#1e40af"
        elif kind == "op":
            bg = self.COLOR_BLUE
            fg = self.COLOR_WHITE
            active = "#1e3a8a"
        elif kind == "ctrl":
            bg = self.COLOR_PANEL
            fg = self.COLOR_TEXT
            active = "#c7dbff"
        else:  # num
            bg = self.COLOR_WHITE
            fg = self.COLOR_TEXT
            active = "#e5e7eb"

        btn = tk.Button(
            parent, text=text, font=self.FONT_BTN, bd=0,
            bg=bg, fg=fg, activebackground=active, activeforeground=fg,
            cursor="hand2",
            relief="flat"
        )
        btn.grid(row=r, column=c, sticky="nsew", padx=6, pady=6, ipady=10)

        # Bind action
        if text == "C":
            btn.configure(command=self._clear)
        elif text == "⌫":
            btn.configure(command=self._backspace)
        elif text == "=":
            btn.configure(command=self._calculate)
        else:
            btn.configure(command=lambda t=text: self._insert_text(t))

    # ---------- Actions ----------
    def _insert_text(self, t: str):
        self.display.insert("end", t)

    def _clear(self):
        self.display_var.set("")

    def _backspace(self):
        current = self.display.get()
        if current:
            self.display_var.set(current[:-1])

    def _calculate(self):
        expr = self.display.get()
        try:
            result = safe_eval(expr)
            # Clean formatting: int if whole number, else float
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self.display_var.set(str(result))
        except Exception:
            self.display_var.set("Error")

    def _type_char(self, event):
        # Allow only relevant printable keys
        ch = event.char
        if ch:
            self.display.insert("end", ch)

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
