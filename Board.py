from dataclasses import dataclass, field
from utils import Point, Ball, Arrow
from typing import Optional
from random import choice
from math import sqrt
import pygame as py
from Cell import *


@dataclass
class Board:
    rows: int
    cols: int
    size: int
    done: bool = True
    end: Cell = None
    start: Cell = None
    current: Cell = None
    first_move: bool = True
    path_found: bool = False
    board: list[Cell] = field(default_factory=list)
    history: list[Cell] = field(default_factory=list)

    mouse_pressed: bool = False
    picked: Optional[Cell] = None
    picked_type: Optional[str] = None

    should_find_path: bool = False
    show_sp_path: bool = True

    find_delay: int = 500
    frame_count: int = 0

    ignore: bool = True
    speed_line: int = -1
    speed_ball_count: int = 10
    draw_speed_ball: bool = True

    draw_arrow: bool = True
    speed_arrows_count: int = 3
    board_cells_reset: bool = True

    # -- maze section
    reverse: bool = False
    maze_is_generated: bool = False
    current_maze_cell: Optional[Cell] = None
    maze_history: list[int] = field(default_factory=list)

    def __post_init__(self, start=None, end=None):
        self.speed_balls: list[Ball] = []
        for i in range(self.speed_ball_count):
            self.speed_balls.append(Ball(-1, Point()))

        self.speed_arrows: list[Arrow] = []
        for i in range(self.speed_arrows_count):
            self.speed_arrows.append(Arrow(-1, self.size / 2.5, Point(0, 0)))

        self.setup_board()
        # -- initialize the start and end cell
        self.init(start, end)

    def init(self, start=None, end=None):
        self.start = choice(self.board) if not start else self.board[start]
        self.start.visited = True
        self.start.color = "orange"
        self.start.cell_type = "start"
        self.end = choice(self.board) if not end else self.board[end]
        # self.end.visited = True
        self.end.trached = True
        self.end.color = "pink"
        self.end.cell_type = "end"

        self.current = self.start
        self.first_move = True

        self.speed_line = -1

        # -- maze selection
        self.current_maze_cell = self.get_cell_for_maze()
        self.current_maze_cell.selected = True

    def reset(self, start=None, end=None):
        self.board.clear()
        self.history.clear()
        self.maze_history.clear()
        self.current_maze_cell = None
        self.__post_init__(start, end)

    def setup_board(self):
        for j in range(self.cols):
            for i in range(self.rows):
                ind = i + j * self.rows
                cell = Cell(i * self.size, j * self.size, ind, self.size)
                self.board.append(cell)

    def get_cell_with_min_cost(self):
        valid_cells = list(filter(lambda neb: neb.visited == False, self.history))

        if not valid_cells:
            return self.current

        min_cost_cell = min(valid_cells, key=lambda neb: neb.f_cost)

        # if min_cost_cell.f_cost > self.current.f_cost:
        #     # print("occer at :", int(min_cost_cell.f_cost), int(self.current.f_cost))
        #     return min(valid_cells, key=lambda neb: neb.h_cost)

        return min_cost_cell

    def sortest_path(self):
        if self.path_found:
            return

        if self.current == self.start:
            self.path_found = True
            return

        if not self.current:
            return

        self.current.cell_type = "sp"
        self.current = self.current.parent

    def mark_cells(self, cell: Cell):
        calculate_valid_neighbors(cell, self.board, self.rows)
        for neb in cell.neighbors:
            if not neb.visited:
                calculate_costs(neb, self.start, self.end)
                neb.trached = True

    def get_cell(self):
        calculate_valid_neighbors(self.current, self.board, self.rows)
        for neb in self.current.neighbors:
            if neb == self.start:
                continue
            if neb.ind == self.end.ind:
                print("found in :", self.end.ind)
                neb.parent = self.current
                self.done = True
                return self.current
            neb.parent = self.current
            self.history.append(neb)

        # if len(self.current.neighbors) == 0:
        #     # self.done = True
        #     # return self.current
        #     pass

        return self.get_cell_with_min_cost()

    def update(self):
        pass

    def update2(self):
        if not self.mouse_pressed:
            self.picked = None
            self.picked_type = None

            if not self.board_cells_reset:
                self.board_cells_reset = True
                self.first_move = True
                self.history.clear()
                self.current = self.start
                self.start.neighbors = []
                self.end.neighbors = []

            return

        self.board_cells_reset = False

        mx, my = py.mouse.get_pos()

        p_row = mx // self.size
        p_col = my // self.size

        press_index = p_row + p_col * self.rows

        pos_x = p_row * self.size
        pos_y = p_col * self.size

        if not self.picked:
            self.picked = list(
                filter(lambda cell: cell.ind == press_index, (self.start, self.end))
            )[0]

            self.picked_type = self.picked.cell_type
            print(self.picked_type)

        if not (0 <= press_index <= len(self.board)):
            return

        if pos_x > (self.rows - 1) * self.size or pos_x < 0:
            return

        if press_index == self.picked.ind:
            self.board_cells_reset = True
            return

        temp = self.board[press_index].cell_type
        self.board[press_index].reset()
        self.board[press_index].cell_type = self.picked_type
        self.picked.cell_type = temp
        # self.picked.visited = False
        self.picked = self.board[press_index]

        if self.picked_type == "start":
            self.first_move = True
            self.start = self.board[press_index]
            self.current = self.start
        if self.picked_type == "end":
            self.end = self.board[press_index]
            self.first_move = True
            self.current = self.start

        self.history.clear()
        self.path_found = False
        for ball in self.speed_balls:
            ball.ind = -1
        for arrow in self.speed_arrows:
            arrow.ind = -1
        for cell in self.board:
            if cell.cell_type in ("normal", "sp"):
                cell.reset()

        if self.should_find_path:
            self.done = False

    def next_step(self):
        if self.first_move:
            self.first_move = False
            self.mark_cells(self.current)
            return

        next = self.get_cell()
        next.visited = True
        self.mark_cells(next)

        self.current = next

    def find_path(self):
        if self.done and self.show_sp_path:
            self.sortest_path()
        if self.done:
            return
        self.next_step()

    def get_cell_for_maze(self, n=None):
        if not self.current_maze_cell:
            cell = choice(self.board)
            if n:
                cell = self.board[n]
            get_valid_maze_neighbors(cell, self.board, self.rows)
            self.maze_history.append(cell.ind)
            return cell

        if len(self.current_maze_cell.neighbors_maze_cell):
            cell = choice(self.current_maze_cell.neighbors_maze_cell)
            get_valid_maze_neighbors(cell, self.board, self.rows)
            if self.reverse:
                self.maze_history.append(self.current_maze_cell.ind)
                self.reverse = False
            return cell

        cell = self.board[self.maze_history.pop()]
        self.reverse = True
        if cell.is_visited:
            cell.re_visited = True
        get_valid_maze_neighbors(cell, self.board, self.rows)
        return cell

    def next_step_for_maze(self):
        next = self.get_cell_for_maze()
        if next.ind not in self.maze_history and not self.reverse:
            remove_border(next.side, self.current_maze_cell, next)
            self.maze_history.append(next.ind)
        self.current_maze_cell.selected = False
        next.selected = True
        self.current_maze_cell = next

    def generate_maze(self):
        if self.maze_is_generated:
            return
        if self.reverse and len(self.maze_history) == 0:
            self.current_maze_cell.selected = False
            self.maze_is_generated = True
            return

        self.next_step_for_maze()

    def draw_segment_line(self, app):
        for i in range(self.speed_ball_count - 1):
            if self.speed_balls[i].ind == -1 or self.speed_balls[i].pos.x == None:
                return
            if (
                self.speed_balls[i + 1].ind == -1
                or self.speed_balls[i + 1].pos.x == None
            ):
                return
            d = abs(self.speed_balls[i].pos.x - self.speed_balls[i + 1].pos.x)

            if d < self.size:
                py.draw.line(
                    app,
                    "purple",
                    self.speed_balls[i].pos,
                    self.speed_balls[i + 1].pos,
                    20,
                )

    def render_speed_ball(self, app):
        parent = self.end
        next_cell = parent.parent

        pp = parent

        color = "black"

        while self.done:
            if not next_cell:
                break

            x1 = parent.x + parent.size // 2
            y1 = parent.y + parent.size // 2
            x2 = next_cell.x + next_cell.size // 2
            y2 = next_cell.y + next_cell.size // 2

            py.draw.line(app, "gray", (x1, y1), (x2, y2), 2)

            for ball in self.speed_balls:
                if parent.ind != ball.ind:
                    continue

                dx = (x1 - x2) / 10
                dy = (y1 - y2) / 10

                ball.pos.x += dx
                ball.pos.y += dy

                color = "green"

                if ball.ind == self.end.ind:
                    color = "red"

                # py.draw.circle(app, color, (ball.pos.x, ball.pos.y), pp.size // 8)

                if ball.pos.x == x1 and ball.pos.y == y1:
                    ball.ind = pp.ind

                dist = sqrt((x2 - ball.pos.x) ** 2 + (y2 - ball.pos.y) ** 2)

                if dist > pp.size:
                    if ball.ind == self.end.ind:
                        ball.ind = -1

            for arrow in self.speed_arrows:
                if parent.ind != arrow.ind:
                    continue

                dx = (x1 - x2) / 10
                dy = (y1 - y2) / 10

                if dx > 0:
                    arrow.angle = 180
                else:
                    arrow.angle = 0

                if dy < 0:
                    arrow.angle = 90
                if dy > 0:
                    arrow.angle = 270

                arrow.pos.x += dx
                arrow.pos.y += dy

                arrow.update()

                color = "green"

                if arrow.ind == self.end.ind:
                    color = "red"

                # py.draw.circle(app, color, (ball.pos.x, ball.pos.y), pp.size // 8)
                py.draw.polygon(app, color, arrow.polygon)

                if arrow.pos.x == x1 and arrow.pos.y == y1:
                    arrow.ind = pp.ind

                dist = sqrt((x2 - arrow.pos.x) ** 2 + (y2 - arrow.pos.y) ** 2)

                if dist > pp.size:
                    if arrow.ind == self.end.ind:
                        arrow.ind = -1

            if parent == self.end:
                py.draw.circle(app, color, (x1, y1), parent.size // 4, 4)

            if next_cell == self.start:
                if self.speed_line == -1:
                    self.speed_line = parent.ind
                    self.spx = x2
                    self.spy = y2

                for ball in self.speed_balls:
                    if self.ignore:
                        break
                    if ball.ind == -1:
                        ball.ind = parent.ind
                        ball.pos.x = x2
                        ball.pos.y = y2
                        break
                for arrow in self.speed_arrows:
                    if self.ignore:
                        break
                    if arrow.ind == -1:
                        arrow.ind = parent.ind
                        arrow.pos.x = x2
                        arrow.pos.y = y2
                        break

                break

            pp = parent

            parent = next_cell
            next_cell = parent.parent

    def handel_speed_ball(self, app):
        # self.draw_segment_line(app)

        self.ignore = True

        self.frame_count += 1
        self.frame_count %= 5

        if self.frame_count == 0:
            self.ignore = False

        self.render_speed_ball(app)

    def handel_speed_arrow(self):
        pass

    def draw(self, app, font):
        for cell in self.board:
            cell.draw(app, font, self.path_found or self.done)

        if self.draw_speed_ball:
            self.handel_speed_ball(app)
