import pygame as py
from Board import Board
import Cell


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

app = py.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = py.time.Clock()

py.font.init()
my_font = py.font.SysFont("Arial", 20)


size = 20
rows = SCREEN_WIDTH // size
cols = SCREEN_HEIGHT // size

board = Board(rows, cols, size)
board.show_sp_path = False


FPS = 260
pressed = False
pause = False
while True:
    for event in py.event.get():
        if event.type == py.QUIT:
            py.quit()
            exit()
        if event.type == py.KEYDOWN:
            if event.key == py.K_ESCAPE:
                print(board.speed_arrows)
                py.quit()
                exit()
            if event.key == py.K_SPACE:
                pause = True if not pause else False
            if event.key == py.K_f:
                FPS = 10 if FPS == 260 else 260
            if event.key == py.K_s:
                FPS = 60
            if event.key == py.K_g:
                board.done = True if not board.done else False
                board.should_find_path = True  # if board.should_find_path else False
                board.path_found = False
            if event.key == py.K_r:
                board.reset()
            if event.key == py.K_n:
                board.next_step()
                # if board.done:
                #     board.sortest_path()
            if event.key == py.K_a:
                board.next_step_for_maze()
            if event.key == py.K_m:
                board.maze_is_generated = False if board.maze_is_generated else True
        if event.type == py.MOUSEBUTTONDOWN:
            board.mouse_pressed = True
        if event.type == py.MOUSEBUTTONUP:
            board.mouse_pressed = False

    if pause:
        continue

    app.fill(120)
    clock.tick(FPS)

    board.find_path()
    board.update2()

    board.generate_maze()

    board.draw(app, my_font)

    py.display.flip()
