from dataclasses import dataclass, field
import pygame as py
from math import sqrt


@dataclass
class Cell:
    x: int
    y: int
    ind: int
    size: int
    g_cost: float = 0
    h_cost: float = 0
    f_cost: float = 0
    color: str = "gray"
    parent: ... = None
    _visited: bool = False
    _trached: bool = False
    _cell_type: str = "normal"
    debug: bool = False
    neighbors: list = field(default_factory=list)

    # -- property as a maze cell --
    side: int = -1
    is_visited: bool = False
    re_visited: bool = False
    _selected: bool = False
    border_thickness: int = 2
    neighbors_maze_cell: list = field(default_factory=list)

    # -- maze selection
    def __post_init__(self):
        self.borders = [True, True, True, True]
        # self.borders = [False, False, False, False]
        # self.borders = [False, False, False, True]
        self.colors = ["red", "brown", "green"]

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value
        if self._selected and not self.is_visited:
            self.is_visited = True

    def get_row_col(self):
        row = self.x // self.size
        col = self.y // self.size
        return row, col

    @property
    def cell_type(self):
        return self._cell_type

    @cell_type.setter
    def cell_type(self, value):
        self._cell_type = value
        if value == "sp":
            self.color = "violet"
        if value == "start":
            self.visited = True
            self.color = "orange"
        if value == "end":
            self.trached = True
            self.color = "pink"
        if value == "normal":
            self.visited = False
            self.trached = False

    @property
    def visited(self):
        return self._visited

    @visited.setter
    def visited(self, value):
        self._visited = value
        if value and self.cell_type == "normal":
            self.color = "red"

    @property
    def trached(self):
        return self._trached

    @trached.setter
    def trached(self, value):
        self._trached = value
        if value and self.cell_type == "normal":
            self.color = "green"

    def reset(self):
        # self.is_visited = False
        # self.re_visited = False
        # self.selected = False
        self.parent = None
        self.neighbors = []
        # self.neighbors_maze_cell = []
        self.visited = False
        self.trached = False
        self.cell_type = "normal"
        self.color = "gray"
        # self.parent = None
        # self.debug = False

    def get_pos(self):
        return self.x, self.y

    def draw(self, app, font, debug):
        if self.selected or self.is_visited or self.re_visited:
            pattern = [self.selected, self.re_visited, self.is_visited]
            py.draw.rect(
                app,
                self.colors[pattern.index(1)],
                (
                    self.x,  # + #(self.boeder_thickness * 2),
                    self.y,  # + (self.boeder_thickness * 2),
                    self.size,  # - (self.boeder_thickness * 3),
                    self.size,  # - (self.boeder_thickness * 3),\
                ),
            )

        if self.visited or self.trached:
            # if self.cell_type in ("sp", "start", "end"):
            if not debug:
                py.draw.rect(app, self.color, (self.x, self.y, self.size, self.size))
            elif self.cell_type in ("sp", "start", "end"):
                py.draw.rect(app, self.color, (self.x, self.y, self.size, self.size))

        # if self._cell_type == "normal":
        #     render_cost = font.render(str(int(self.f_cost)), 1, "black")
        #     app.blit(render_cost, (self.x + 10, self.y + 10))

        for ind, border in enumerate(self.borders):
            # ind = 0
            if border and ind == 0:
                py.draw.line(
                    app,
                    "black",
                    (self.x, self.y),
                    (self.x, self.y + self.size - 1),
                    self.border_thickness,
                )
            if border and ind == 1:
                py.draw.line(
                    app,
                    "black",
                    (self.x + self.size, self.y),
                    (self.x + self.size, self.y + self.size),
                    self.border_thickness,
                )
            if border and ind == 2:
                py.draw.line(
                    app,
                    "black",
                    (self.x, self.y),
                    (self.x + self.size, self.y),
                    self.border_thickness,
                )
            if border and ind == 3:
                py.draw.line(
                    app,
                    "black",
                    (self.x, self.y + self.size),
                    (self.x + self.size, self.y + self.size),
                    self.border_thickness,
                )


def get_row_col(cell: Cell):
    row = cell.x // cell.size
    col = cell.y // cell.size

    return row, col


def remove_border(side: int, cell_a: Cell, cell_b: Cell = None):
    r_side = 0

    if side == 0:
        r_side = 1
    if side == 1:
        r_side = 0
    if side == 2:
        r_side = 3
    if side == 3:
        r_side = 2

    cell_a.borders[side] = False
    if cell_b:
        cell_b.borders[r_side] = False


def found_open_border(side: int, cell_a: Cell, cell_b: Cell = None):
    r_side = 0

    if side == 0:
        r_side = 1
    if side == 1:
        r_side = 0
    if side == 2:
        r_side = 3
    if side == 3:
        r_side = 2

    if cell_a.borders[side] == False:
        if cell_b and cell_b.borders[r_side] == False:
            return True
        return True
    return False


def get_valid_cell(ind, parent: Cell, board: list[Cell]):
    nab = None
    for cell in board:
        if cell.ind == ind:
            nab = cell
            break

    if not nab:
        return None

    p_row, p_col = get_row_col(parent)
    n_row, n_col = get_row_col(nab)

    # if p_col == n_col:
    #     return nab
    # elif abs(p_col - n_col) == 1:
    #     if p_row == n_row:
    #         return nab

    side = nab.ind - parent.ind  # -- for left right side
    if abs(side) == 1 and found_open_border(side == abs(side), parent, nab):
        if p_col == n_col:
            return nab
    side = n_col - p_col
    if abs(side) == 1 and found_open_border((side == abs(side)) + 2, parent, nab):
        if p_row == n_row:
            return nab

    return None


def get_distance(a: Cell, b: Cell):
    return sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


def calculate_costs(cell: Cell, start: Cell, end: Cell):
    cell.g_cost = get_distance(cell, start)
    cell.h_cost = get_distance(cell, end)
    cell.f_cost = cell.g_cost + cell.h_cost


def calculate_valid_neighbors(cell: Cell, board: list[Cell], rows: int):
    neighbors = []

    for i in [-1, 1]:
        ind = cell.ind + i
        neighbors.append(get_valid_cell(ind, cell, board))

    for j in [-1, 1]:
        ind = cell.ind + j * rows
        neighbors.append(get_valid_cell(ind, cell, board))

    neighbors = list(
        filter(lambda neb: neb != None and neb.visited == False, neighbors)
    )

    # map(lambda neb: calculate_costs(neb, cell), neighbors)

    cell.neighbors = neighbors
    return neighbors


# -- maze section --


def get_valid_maze_cell(ind, parent: Cell, board: list[Cell]):
    nab = None
    for cell in board:
        if cell.ind == ind:
            nab = cell
            break

    if not nab:
        return None

    p_row, p_col = get_row_col(parent)
    n_row, n_col = get_row_col(nab)

    if p_col == n_col:
        return nab
    elif abs(p_col - n_col) == 1:
        if p_row == n_row:
            return nab

    return None


def get_valid_maze_neighbors(cell: Cell, board: list[Cell], rows: int):
    neighbors = []

    for i in [-1, 1]:
        ind = cell.ind + i
        neighbors.append(get_valid_maze_cell(ind, cell, board))

    for j in [-1, 1]:
        ind = cell.ind + j * rows
        neighbors.append(get_valid_maze_cell(ind, cell, board))

    for ind, neb in enumerate(neighbors):
        if neb:
            neb.side = ind

    neighbors = list(
        filter(lambda neb: neb != None and neb.is_visited == False, neighbors)
    )
    cell.neighbors_maze_cell = neighbors
    return neighbors
