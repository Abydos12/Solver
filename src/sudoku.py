from __future__ import annotations

from collections.abc import Iterator
from copy import deepcopy
from typing import Optional

from utils import Timer

s1 = [
    [5, 3, None, None, 7, None, None, None, None],
    [6, None, None, 1, 9, 5, None, None, None],
    [None, 9, 8, None, None, None, None, 6, None],
    [8, None, None, None, 6, None, None, None, 3],
    [4, None, None, 8, None, 3, None, None, 1],
    [7, None, None, None, 2, None, None, None, 6],
    [None, 6, None, None, None, None, 2, 8, None],
    [None, None, None, 4, 1, 9, None, None, 5],
    [None, None, None, None, 8, None, None, 7, 9],
]

s2 = [
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, 3, None, 8, 5],
    [None, None, 1, None, 2, None, None, None, None],
    [None, None, None, 5, None, 7, None, None, None],
    [None, None, 4, None, None, None, 1, None, None],
    [None, 9, None, None, None, None, None, None, None],
    [5, None, None, None, None, None, None, 7, 3],
    [None, None, 2, None, 1, None, None, None, None],
    [None, None, None, None, 4, None, None, None, 9],
]

s3 = [
    [None, 4, None, 1, None, None, 2, None, None],
    [6, None, None, 4, 3, None, 5, None, None],
    [None, None, None, 2, None, None, 9, None, None],
    [None, 2, None, None, 8, None, None, 1, None],
    [None, 5, 8, None, None, None, 7, 3, None],
    [None, 9, None, None, 4, None, None, 5, None],
    [None, None, 1, None, None, 4, None, None, 8],
    [None, None, 4, None, 9, 5, None, None, 6],
    [None, None, 7, None, None, 3, None, 2, None],
]

s2_solved = [
    [9, 8, 7, 6, 5, 4, 3, 2, 1],
    [2, 4, 6, 1, 7, 3, 9, 8, 5],
    [3, 5, 1, 9, 2, 8, 7, 4, 6],
    [1, 2, 8, 5, 3, 7, 6, 9, 4],
    [6, 3, 4, 8, 9, 2, 1, 5, 7],
    [7, 9, 5, 4, 6, 1, 8, 3, 2],
    [5, 1, 9, 2, 8, 6, 4, 7, 3],
    [4, 7, 2, 3, 1, 9, 5, 6, 8],
    [8, 6, 3, 7, 4, 5, 2, 1, 9],
]

grid_format = """
╔═╤═╤═╦═╤═╤═╦═╤═╤═╗
║{}│{}│{}║{}│{}│{}║{}│{}│{}║
╟─┼─┼─╫─┼─┼─╫─┼─┼─╢
║{}│{}│{}║{}│{}│{}║{}│{}│{}║
╟─┼─┼─╫─┼─┼─╫─┼─┼─╢
║{}│{}│{}║{}│{}│{}║{}│{}│{}║
╠═╪═╪═╬═╪═╪═╬═╪═╪═╣
║{}│{}│{}║{}│{}│{}║{}│{}│{}║
╟─┼─┼─╫─┼─┼─╫─┼─┼─╢
║{}│{}│{}║{}│{}│{}║{}│{}│{}║
╟─┼─┼─╫─┼─┼─╫─┼─┼─╢
║{}│{}│{}║{}│{}│{}║{}│{}│{}║
╠═╪═╪═╬═╪═╪═╬═╪═╪═╣
║{}│{}│{}║{}│{}│{}║{}│{}│{}║
╟─┼─┼─╫─┼─┼─╫─┼─┼─╢
║{}│{}│{}║{}│{}│{}║{}│{}│{}║
╟─┼─┼─╫─┼─┼─╫─┼─┼─╢
║{}│{}│{}║{}│{}│{}║{}│{}│{}║
╚═╧═╧═╩═╧═╧═╩═╧═╧═╝

"""


POSSIBILITIES = set(range(1, 10))
SUB_GRID_INDEX = {i: i - i % 3 for i in range(9)}

Grid = list[list[Optional[int]]]


def sub_grid_range(row: int, col: int) -> Iterator[tuple[int, int]]:
    return (
        (r, c)
        for r in range(row - row % 3, SUB_GRID_INDEX[row] + 3)
        for c in range(SUB_GRID_INDEX[col], SUB_GRID_INDEX[col] + 3)
    )


def grid_range() -> Iterator[tuple[int, int]]:
    return ((row, col) for row in range(9) for col in range(9))


def empty_grid():
    return [[None for _ in range(9)] for _ in range(9)]


class Sudoku:
    _grid: Grid = empty_grid()
    _track_iterations: int = 0
    _p: dict[tuple[int, int], set[int]]

    def __init__(self, grid: Grid):
        self._grid = deepcopy(grid)
        self._p = dict()
        for row, col in grid_range():
            self._p[row, col] = self.possibilities(row, col)

    def values(self) -> Iterator[int | None]:
        return (self._grid[r][c] for r, c in grid_range())

    def is_full(self):
        return not any(c is None for r in self._grid for c in r)

    def is_valid(self):
        for r, c in grid_range():
            cell = self._grid[r][c]
            if cell is None:
                continue
            if cell < 1 or cell > 9:
                return False
            if not self.is_cell_valid(r, c):
                return False
        return True

    def is_complete(self) -> bool:
        return self.is_full() and self.is_valid()

    def is_cell_valid(self, row: int, col: int) -> bool:
        return (
            self._grid[row][col] not in self.row_values(row, col)
            and self._grid[row][col] not in self.col_values(row, col)
            and self._grid[row][col] not in self.sub_grid_values(row, col)
        )

    def row_values(self, row: int, col: int, except_cell=True):
        return (self._grid[row][c] for c in range(9) if not except_cell or c != col)

    def col_values(self, row: int, col: int, except_cell=True):
        return (self._grid[r][col] for r in range(9) if not except_cell or r != row)

    def sub_grid_values(self, row: int, col: int, except_cell=True):
        return (
            self._grid[r][c]
            for r, c in sub_grid_range(row, col)
            if not except_cell or (r != row and c != col)
        )

    def _find_less_possibilities_cell(self) -> tuple[int | None, int | None]:
        row, col, least = None, None, 10
        for r, c in grid_range():
            if self._grid[r][c] is not None:
                continue
            count = len(self.possibilities(r, c))
            if least == 1 or least == 0:
                return row, col
            if count < least:
                row, col, least = r, c, count
        return row, col

    def _find_first_empty_cell(self) -> tuple[int | None, int | None]:
        for r, c in grid_range():
            if not self._grid[r][c]:
                return r, c
        return None, None

    def is_valid_move(self, row: int, col: int, value: int):
        return not (
            value in self._grid[row]
            or any(self._grid[r][col] == value for r in range(9))
            or any(self._grid[r][c] == value for r, c in sub_grid_range(row, col))
        )

    def taken_values(self, row: int, col: int) -> set[int | None]:
        r_values = set(self._grid[row])
        c_values = {self._grid[r][col] for r in range(9)}
        sub_grid_values = {self._grid[r][c] for r, c in sub_grid_range(row, col)}
        return (r_values | c_values | sub_grid_values) - {None}

    def taken_values2(self, row: int, col: int):
        emited = set()
        for c in range(9):
            v = self._grid[row][c]
            if v in emited:
                continue
            emited.add(v)
            yield v

        c_values = {self._grid[r][col] for r in range(9)}
        sub_grid_values = {self._grid[r][c] for r, c in sub_grid_range(row, col)}
        return (c_values | sub_grid_values) - {None}

    def possibilities(self, row, col):
        return POSSIBILITIES - self.taken_values(row, col)

    def solve(self) -> bool:
        self._track_iterations = 0
        return self._solve()

    def _solve(self) -> bool:
        self._track_iterations += 1
        if self.is_complete():
            return True
        row, col = self._find_less_possibilities_cell()
        if row is None or col is None:
            return False
        for val in self.possibilities(row, col):
            self._grid[row][col] = val
            if self._solve():
                return True
            self._grid[row][col] = None
        return False

    def _solve_2(self) -> bool:
        self._track_iterations += 1
        if self.is_complete():
            return True
        row, col = self._find_less_possibilities_cell()
        if row is None or col is None:
            return False
        for val in self.possibilities(row, col):
            self._grid[row][col] = val
            if self._solve():
                return True
            self._grid[row][col] = None
        return False

    def __str__(self):
        return grid_format.format(*(self._grid[r][c] or "-" for r, c in grid_range()))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Sudoku):
            return self._grid == other._grid


if __name__ == "__main__":
    sudoku = Sudoku(s2)
    sudoku_solved = Sudoku(s2_solved)
    print(sudoku)
    with Timer():
        solved = sudoku.solve()
    print(sudoku)
    print(
        f"Solution {'not ' if not solved else ''}found with {sudoku._track_iterations} iterations"
    )
