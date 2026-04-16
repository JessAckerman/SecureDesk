from __future__ import annotations

from tkinter import ttk


COLORS = {
    "navy": "#0B1F33",
    "navy_soft": "#16324D",
    "blue": "#1E5AA8",
    "cyan": "#4AA3D8",
    "surface": "#EEF3F8",
    "surface_alt": "#E4ECF5",
    "panel": "#FFFFFF",
    "panel_alt": "#F7FAFD",
    "text": "#172635",
    "muted": "#5D7288",
    "border": "#D5DFEA",
    "success": "#2F855A",
    "warning": "#C18A2C",
    "danger": "#C53B3B",
    "sidebar_text": "#EAF3FF",
}


def apply_theme(root) -> None:
    style = ttk.Style(root)
    style.theme_use("clam")

    root.configure(bg=COLORS["surface"])

    style.configure("App.TFrame", background=COLORS["surface"])
    style.configure("Panel.TFrame", background=COLORS["panel"], relief="flat")
    style.configure("Card.TFrame", background=COLORS["panel"], relief="flat")
    style.configure("SoftCard.TFrame", background=COLORS["panel_alt"], relief="flat")
    style.configure("Sidebar.TFrame", background=COLORS["navy"])
    style.configure("Hero.TFrame", background=COLORS["navy"])

    style.configure(
        "Title.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=("Segoe UI Semibold", 24),
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
        font=("Segoe UI Semibold", 15),
    )
    style.configure(
        "PanelText.TLabel",
        background=COLORS["panel"],
        foreground=COLORS["muted"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "HeroTitle.TLabel",
        background=COLORS["navy"],
        foreground="white",
        font=("Segoe UI Semibold", 30),
    )
    style.configure(
        "HeroText.TLabel",
        background=COLORS["navy"],
        foreground=COLORS["sidebar_text"],
        font=("Segoe UI", 11),
    )
    style.configure(
        "StatValue.TLabel",
        background=COLORS["panel"],
        foreground=COLORS["text"],
        font=("Segoe UI Semibold", 22),
    )
    style.configure(
        "StatCaption.TLabel",
        background=COLORS["panel"],
        foreground=COLORS["muted"],
        font=("Segoe UI", 9),
    )
    style.configure(
        "ErrorFeedback.TLabel",
        background=COLORS["panel"],
        foreground=COLORS["danger"],
        font=("Segoe UI", 9),
    )
    style.configure(
        "SuccessFeedback.TLabel",
        background=COLORS["panel"],
        foreground=COLORS["success"],
        font=("Segoe UI", 9),
    )
    style.configure(
        "Sidebar.TLabel",
        background=COLORS["navy"],
        foreground=COLORS["sidebar_text"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "SidebarTitle.TLabel",
        background=COLORS["navy"],
        foreground="white",
        font=("Segoe UI Semibold", 20),
    )
    style.configure(
        "SidebarCaption.TLabel",
        background=COLORS["navy"],
        foreground="#90A7BF",
        font=("Segoe UI", 9),
    )

    style.configure(
        "Primary.TButton",
        background=COLORS["blue"],
        foreground="white",
        borderwidth=0,
        focusthickness=0,
        font=("Segoe UI Semibold", 10),
        padding=(16, 11),
    )
    style.map("Primary.TButton", background=[("active", COLORS["navy_soft"])])

    style.configure(
        "Secondary.TButton",
        background=COLORS["panel"],
        foreground=COLORS["text"],
        borderwidth=1,
        bordercolor=COLORS["border"],
        font=("Segoe UI", 10),
        padding=(12, 9),
    )
    style.map("Secondary.TButton", background=[("active", COLORS["surface_alt"])])

    style.configure(
        "Nav.TButton",
        background=COLORS["navy"],
        foreground=COLORS["sidebar_text"],
        borderwidth=0,
        focusthickness=0,
        font=("Segoe UI Semibold", 10),
        padding=(14, 12),
        anchor="w",
    )
    style.map(
        "Nav.TButton",
        background=[("active", COLORS["navy_soft"])],
        foreground=[("active", "white")],
    )

    style.configure(
        "Logout.TButton",
        background="#10263E",
        foreground="white",
        borderwidth=0,
        focusthickness=0,
        font=("Segoe UI Semibold", 10),
        padding=(12, 10),
    )
    style.map("Logout.TButton", background=[("active", "#183754")])

    style.configure(
        "Treeview",
        background=COLORS["panel"],
        fieldbackground=COLORS["panel"],
        foreground=COLORS["text"],
        bordercolor=COLORS["border"],
        rowheight=34,
        font=("Segoe UI", 10),
    )
    style.configure(
        "Treeview.Heading",
        background=COLORS["surface_alt"],
        foreground=COLORS["text"],
        font=("Segoe UI Semibold", 10),
        relief="flat",
    )
    style.map("Treeview.Heading", background=[("active", COLORS["surface_alt"])])

    style.configure(
        "Valid.TEntry",
        fieldbackground="#F1FBF5",
        bordercolor=COLORS["success"],
        lightcolor=COLORS["success"],
        darkcolor=COLORS["success"],
    )
    style.configure(
        "Invalid.TEntry",
        fieldbackground="#FFF5F5",
        bordercolor=COLORS["danger"],
        lightcolor=COLORS["danger"],
        darkcolor=COLORS["danger"],
    )
    style.configure(
        "Valid.TCombobox",
        fieldbackground="#F1FBF5",
        bordercolor=COLORS["success"],
        lightcolor=COLORS["success"],
        darkcolor=COLORS["success"],
        arrowsize=16,
    )
    style.configure(
        "Invalid.TCombobox",
        fieldbackground="#FFF5F5",
        bordercolor=COLORS["danger"],
        lightcolor=COLORS["danger"],
        darkcolor=COLORS["danger"],
        arrowsize=16,
    )
