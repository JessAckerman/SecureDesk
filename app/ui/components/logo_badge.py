from __future__ import annotations

import tkinter as tk


class LogoBadge(tk.Canvas):
    def __init__(self, parent, size: int = 76, bg: str = "#F4F7FA") -> None:
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=bg,
            highlightthickness=0,
            bd=0,
        )
        self.size = size
        self._draw()

    def _draw(self) -> None:
        s = self.size
        self.create_oval(6, 6, s - 6, s - 6, fill="#DCEAF7", outline="")
        self.create_oval(13, 13, s - 13, s - 13, fill="#10324A", outline="")
        self.create_polygon(
            s * 0.5,
            s * 0.18,
            s * 0.78,
            s * 0.30,
            s * 0.78,
            s * 0.56,
            s * 0.5,
            s * 0.82,
            s * 0.22,
            s * 0.56,
            s * 0.22,
            s * 0.30,
            fill="#1F5C8D",
            outline="",
        )
        self.create_rectangle(s * 0.35, s * 0.40, s * 0.65, s * 0.58, fill="white", outline="")
        self.create_line(s * 0.40, s * 0.40, s * 0.40, s * 0.58, fill="#10324A", width=2)
        self.create_line(s * 0.60, s * 0.40, s * 0.60, s * 0.58, fill="#10324A", width=2)
        self.create_line(s * 0.35, s * 0.49, s * 0.65, s * 0.49, fill="#10324A", width=2)
        self.create_text(
            s * 0.5,
            s * 0.66,
            text="S",
            fill="white",
            font=("Segoe UI Semibold", max(10, int(s * 0.16))),
        )
