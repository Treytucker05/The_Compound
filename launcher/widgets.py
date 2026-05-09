"""
widgets.py — Reusable UI components for the COMPOUND_APPROACH Portal launcher.

Dark-themed tkinter widgets matching the MUD client aesthetic.
"""

import tkinter as tk
from tkinter import ttk

# Nord-inspired dark palette
COLORS = {
    "bg": "#0a0a0a",
    "bg_card": "#111111",
    "bg_input": "#1a1a1a",
    "border": "#222222",
    "text": "#d4d4d4",
    "text_dim": "#666666",
    "accent_joseph": "#88c0d0",
    "accent_trey": "#a3be8c",
    "accent_shared": "#ebcb8b",
    "accent_default": "#5e81ac",
    "success": "#a3be8c",
    "error": "#bf616a",
    "warn": "#ebcb8b",
}

FONTS = {
    "mono": ("Courier New", 10),
    "mono_small": ("Courier New", 9),
    "label": ("Segoe UI", 9, "bold"),
    "body": ("Segoe UI", 9),
    "status": ("Segoe UI", 8),
}


class DarkFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", COLORS["bg_card"])
        kwargs.setdefault("highlightbackground", COLORS["border"])
        kwargs.setdefault("highlightthickness", 1)
        super().__init__(parent, **kwargs)


class StatusCard(tk.Frame):
    def __init__(self, parent, title: str, value: str = "—", accent: str = None):
        super().__init__(parent, bg=COLORS["bg_card"], highlightbackground=COLORS["border"], highlightthickness=1)
        self.accent = accent or COLORS["accent_default"]

        self.title_label = tk.Label(self, text=title.upper(), bg=COLORS["bg_card"], fg=COLORS["text_dim"],
                                    font=FONTS["status"])
        self.title_label.pack(anchor="w", padx=10, pady=(8, 0))

        self.value_label = tk.Label(self, text=value, bg=COLORS["bg_card"], fg=self.accent,
                                    font=FONTS["mono"])
        self.value_label.pack(anchor="w", padx=10, pady=(0, 8))

    def set_value(self, text: str, color: str = None):
        self.value_label.config(text=text, fg=color or self.accent)


class ActionButton(tk.Button):
    def __init__(self, parent, text: str, command=None, accent: str = None, **kwargs):
        self.accent = accent or COLORS["accent_default"]
        kwargs.setdefault("bg", COLORS["bg_input"])
        kwargs.setdefault("fg", self.accent)
        kwargs.setdefault("activebackground", COLORS["border"])
        kwargs.setdefault("activeforeground", self.accent)
        kwargs.setdefault("font", FONTS["label"])
        kwargs.setdefault("relief", tk.FLAT)
        kwargs.setdefault("cursor", "hand2")
        kwargs.setdefault("padx", 16)
        kwargs.setdefault("pady", 6)
        super().__init__(parent, text=text, command=command, **kwargs)


class LogViewer(tk.Text):
    def __init__(self, parent, height=12, **kwargs):
        kwargs.setdefault("bg", COLORS["bg"])
        kwargs.setdefault("fg", COLORS["text_dim"])
        kwargs.setdefault("font", FONTS["mono_small"])
        kwargs.setdefault("relief", tk.FLAT)
        kwargs.setdefault("state", tk.DISABLED)
        kwargs.setdefault("wrap", tk.WORD)
        kwargs.setdefault("height", height)
        super().__init__(parent, **kwargs)

        self.tag_config("info", foreground=COLORS["text"])
        self.tag_config("success", foreground=COLORS["success"])
        self.tag_config("error", foreground=COLORS["error"])
        self.tag_config("warn", foreground=COLORS["warn"])
        self.tag_config("system", foreground=COLORS["accent_default"])

    def append(self, text: str, tag: str = "info"):
        self.config(state=tk.NORMAL)
        self.insert(tk.END, text + "\n", tag)
        self.see(tk.END)
        self.config(state=tk.DISABLED)
        # Keep only last 500 lines
        count = int(self.index("end-1c").split(".")[0])
        if count > 500:
            self.delete("1.0", f"{count - 500}.0")
