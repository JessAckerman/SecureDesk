from __future__ import annotations

from tkinter import ttk


COLORS = {
    "navy": "#10324A",
    "blue": "#1F5C8D",
    "sky": "#DCEAF7",
    "surface": "#F4F7FA",
    "panel": "#FFFFFF",
    "text": "#1E2A36",
    "muted": "#627282",
    "border": "#D1D9E0",
    "success": "#2F855A",
    "warning": "#B7791F",
    "danger": "#C53030",
}


def apply_theme(root) -> None:
    style = ttk.Style(root)
    style.theme_use("clam")

    root.configure(bg=COLORS["surface"])

    style.configure(
        "App.TFrame",
        background=COLORS["surface"],
    )
    style.configure(
        "Panel.TFrame",
        background=COLORS["panel"],
        relief="flat",
    )
    style.configure(
        "Sidebar.TFrame",
        background=COLORS["navy"],
    )
    style.configure(
        "Title.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=("Segoe UI Semibold", 20),
    )
    style.configure(
        "Subtitle.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["muted"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "PanelTitle.TLabel",
        background=COLORS["panel"],
        foreground=COLORS["text"],
        font=("Segoe UI Semibold", 14),
    )
    style.configure(
        "PanelText.TLabel",
        background=COLORS["panel"],
        foreground=COLORS["muted"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "Sidebar.TLabel",
        background=COLORS["navy"],
        foreground="white",
        font=("Segoe UI", 10),
    )
    style.configure(
        "SidebarTitle.TLabel",
        background=COLORS["navy"],
        foreground="white",
        font=("Segoe UI Semibold", 18),
    )
    style.configure(
        "Primary.TButton",
        background=COLORS["blue"],
        foreground="white",
        borderwidth=0,
        focusthickness=0,
        font=("Segoe UI Semibold", 10),
        padding=(14, 10),
    )
    style.map(
        "Primary.TButton",
        background=[("active", COLORS["navy"])],
    )
    style.configure(
        "Secondary.TButton",
        background=COLORS["panel"],
        foreground=COLORS["text"],
        borderwidth=1,
        bordercolor=COLORS["border"],
        font=("Segoe UI", 10),
        padding=(12, 9),
    )
    style.map(
        "Secondary.TButton",
        background=[("active", COLORS["sky"])],
    )
    style.configure(
        "Treeview",
        background=COLORS["panel"],
        fieldbackground=COLORS["panel"],
        foreground=COLORS["text"],
        bordercolor=COLORS["border"],
        rowheight=32,
        font=("Segoe UI", 10),
    )
    style.configure(
        "Treeview.Heading",
        background=COLORS["sky"],
        foreground=COLORS["text"],
        font=("Segoe UI Semibold", 10),
        relief="flat",
    )
    style.map("Treeview.Heading", background=[("active", COLORS["sky"])])
