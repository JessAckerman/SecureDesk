from __future__ import annotations

import tkinter as tk


class SignaturePad(tk.Frame):
    def __init__(self, parent, width: int = 420, height: int = 150, on_change=None) -> None:
        super().__init__(parent, bg="#FFFFFF", highlightbackground="#D5DFEA", highlightthickness=1)
        self.width = width
        self.height = height
        self.on_change = on_change
        self._strokes: list[list[tuple[int, int]]] = []
        self._current_stroke: list[tuple[int, int]] = []

        self.canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            bg="#FFFFFF",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self._start_stroke)
        self.canvas.bind("<B1-Motion>", self._draw)
        self.canvas.bind("<ButtonRelease-1>", self._end_stroke)

        self._draw_placeholder()

    def _draw_placeholder(self) -> None:
        self.canvas.delete("placeholder")
        if not self._strokes and not self._current_stroke:
            self.canvas.create_text(
                self.width // 2,
                self.height // 2,
                text="Firma aqui con el mouse",
                fill="#90A7BF",
                font=("Segoe UI", 12),
                tags="placeholder",
            )

    def _start_stroke(self, event) -> None:
        self._current_stroke = [(event.x, event.y)]
        self._draw_placeholder()

    def _draw(self, event) -> None:
        if not self._current_stroke:
            self._current_stroke = [(event.x, event.y)]
            return
        x1, y1 = self._current_stroke[-1]
        x2, y2 = event.x, event.y
        self.canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            fill="#0B1F33",
            width=2.5,
            capstyle=tk.ROUND,
            smooth=True,
        )
        self._current_stroke.append((x2, y2))

    def _end_stroke(self, _event) -> None:
        if len(self._current_stroke) >= 2:
            self._strokes.append(self._current_stroke[:])
        self._current_stroke = []
        self._draw_placeholder()
        if self.on_change:
            self.on_change()

    def clear(self) -> None:
        self._strokes.clear()
        self._current_stroke = []
        self.canvas.delete("all")
        self._draw_placeholder()
        if self.on_change:
            self.on_change()

    def has_signature(self) -> bool:
        return bool(self._strokes)

    def export_svg(self) -> str:
        paths = []
        for stroke in self._strokes:
            if len(stroke) < 2:
                continue
            commands = [f"M {stroke[0][0]} {stroke[0][1]}"]
            commands.extend(f"L {x} {y}" for x, y in stroke[1:])
            paths.append(
                f'<path d="{" ".join(commands)}" stroke="#0B1F33" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            )
        svg_body = "".join(paths)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}">{svg_body}</svg>'
        )
