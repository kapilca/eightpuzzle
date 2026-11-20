#!/usr/bin/env python3
"""8-Puzzle sliding tile game built with tkinter.

Rules:
- Tiles 1-8 on a 3x3 grid with one empty space.
- Click a tile next to the empty space (or use arrow keys) to slide it.
- Arrange the tiles in order 1..8 with the empty space last to win.
"""

import random
import tkinter as tk
from tkinter import messagebox

GRID_SIZE = 3
TILE_SIZE = 100
FONT = ("Helvetica", 32, "bold")
BG = "#2b2b2b"
TILE_COLOR = "#4a90d9"
TILE_ACTIVE = "#5ba3ec"
TILE_TEXT = "#ffffff"
SOLVED = tuple(list(range(1, GRID_SIZE * GRID_SIZE)) + [0])  # 0 = empty


class EightPuzzle:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("8-Puzzle")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        # board[i] = tile number at cell i (0 = empty). Starts solved.
        self.board: list[int] = list(SOLVED)
        self.moves = 0
        self.selected = None  # index of selected tile (keyboard play)

        # --- Header: move counter ---
        header = tk.Frame(root, bg=BG)
        header.pack(pady=(12, 4))
        tk.Label(
            header, text="Moves:", font=("Helvetica", 14), bg=BG, fg="#aaaaaa"
        ).pack(side=tk.LEFT)
        self.move_label = tk.Label(
            header, text="0", font=("Helvetica", 14, "bold"), bg=BG, fg="#ffffff"
        )
        self.move_label.pack(side=tk.LEFT, padx=(4, 0))

        # --- Board canvas ---
        canvas_px = GRID_SIZE * TILE_SIZE
        self.canvas = tk.Canvas(
            root,
            width=canvas_px,
            height=canvas_px,
            bg=BG,
            highlightthickness=0,
        )
        self.canvas.pack(padx=12, pady=8)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_hover)
        self.canvas.bind("<Leave>", lambda e: self.draw(hover=None))

        # --- Buttons ---
        btns = tk.Frame(root, bg=BG)
        btns.pack(pady=(0, 12))
        tk.Button(
            btns, text="New Game", font=("Helvetica", 12), command=self.new_game
        ).pack(side=tk.LEFT, padx=4)
        tk.Button(
            btns, text="Solve", font=("Helvetica", 12), command=self.solve
        ).pack(side=tk.LEFT, padx=4)

        # --- Arrow-key controls ---
        root.bind("<Left>", lambda e: self.move_blank("left"))
        root.bind("<Right>", lambda e: self.move_blank("right"))
        root.bind("<Up>", lambda e: self.move_blank("up"))
        root.bind("<Down>", lambda e: self.move_blank("down"))

        self.new_game()

    # ------------------------------------------------------------------ helpers
    @property
    def blank_index(self) -> int:
        return self.board.index(0)

    def neighbors(self, i: int) -> list[int]:
        """Cell indices adjacent (up/down/left/right) to cell i."""
        row, col = divmod(i, GRID_SIZE)
        out = []
        if row > 0:
            out.append(i - GRID_SIZE)
        if row < GRID_SIZE - 1:
            out.append(i + GRID_SIZE)
        if col > 0:
            out.append(i - 1)
        if col < GRID_SIZE - 1:
            out.append(i + 1)
        return out

    # ------------------------------------------------------------------ actions
    def new_game(self) -> None:
        """Shuffle by making random legal slides from the solved state,
        which guarantees a solvable position."""
        self.board = list(SOLVED)
        prev = None
        for _ in range(150):
            options = [n for n in self.neighbors(self.blank_index) if n != prev]
            choice = random.choice(options)
            prev = self.blank_index
            self.board[self.blank_index], self.board[choice] = (
                self.board[choice],
                self.board[self.blank_index],
            )
        self.moves = 0
        self.selected = None
        self.update_status()
        self.draw()

    def solve(self) -> None:
        self.board = list(SOLVED)
        self.moves = 0
        self.selected = None
        self.update_status()
        self.draw()

    def slide(self, cell: int) -> bool:
        """Slide the tile at `cell` into the blank, if adjacent."""
        if cell == self.blank_index or cell not in self.neighbors(self.blank_index):
            return False
        b = self.blank_index
        self.board[b], self.board[cell] = self.board[cell], self.board[b]
        self.moves += 1
        self.update_status()
        self.draw()
        self.check_win()
        return True

    def move_blank(self, direction: str) -> None:
        """Arrow keys move a tile INTO the blank (tile slides opposite way)."""
        b = self.blank_index
        row, col = divmod(b, GRID_SIZE)
        target = {
            "left": (row, col + 1),    # tile to the right slides left
            "right": (row, col - 1),   # tile to the left slides right
            "up": (row + 1, col),      # tile below slides up
            "down": (row - 1, col),    # tile above slides down
        }[direction]
        tr, tc = target
        if 0 <= tr < GRID_SIZE and 0 <= tc < GRID_SIZE:
            self.slide(tr * GRID_SIZE + tc)

    def check_win(self) -> None:
        if tuple(self.board) == SOLVED:
            self.draw()
            self.root.after(150, lambda: messagebox.showinfo(
                "You win!",
                f"Solved in {self.moves} moves!",
            ))

    def update_status(self) -> None:
        self.move_label.config(text=str(self.moves))

    # ------------------------------------------------------------------ drawing
    def cell_at(self, x: int, y: int) -> int | None:
        col, row = x // TILE_SIZE, y // TILE_SIZE
        if 0 <= col < GRID_SIZE and 0 <= row < GRID_SIZE:
            return row * GRID_SIZE + col
        return None

    def on_click(self, event: tk.Event) -> None:
        cell = self.cell_at(event.x, event.y)
        if cell is not None:
            if not self.slide(cell):
                # flash invalid tile
                self.draw(hover=None, flash=cell)

    def on_hover(self, event: tk.Event) -> None:
        cell = self.cell_at(event.x, event.y)
        movable = cell is not None and cell in self.neighbors(self.blank_index)
        self.draw(hover=cell if movable else None)

    def draw(self, hover: int | None = None, flash: int | None = None) -> None:
        c = self.canvas
        c.delete("all")
        for i, tile in enumerate(self.board):
            row, col = divmod(i, GRID_SIZE)
            x1, y1 = col * TILE_SIZE, row * TILE_SIZE
            x2, y2 = x1 + TILE_SIZE, y1 + TILE_SIZE
            if tile == 0:
                continue  # leave blank cell empty
            fill = TILE_ACTIVE if i == hover else TILE_COLOR
            if i == flash:
                fill = "#d9534f"  # red flash for invalid move
            c.create_rectangle(
                x1 + 4, y1 + 4, x2 - 4, y2 - 4,
                fill=fill, outline="#2a5f8f", width=2,
            )
            c.create_text(
                (x1 + x2) // 2, (y1 + y2) // 2,
                text=str(tile), font=FONT, fill=TILE_TEXT,
            )
        if flash is not None:
            c.after(120, lambda: self.draw())


def main() -> None:
    root = tk.Tk()
    EightPuzzle(root)
    root.mainloop()


if __name__ == "__main__":
    main()
