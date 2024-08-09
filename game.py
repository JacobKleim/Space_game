import asyncio
import curses
import itertools
import time
from random import choice, randint

from curses_tools import draw_frame, get_frame_size, read_controls
from animations.fire import fire
from read_frames import read_frames

TIC_TIMEOUT = 0.1


async def animate_spaceship(canvas, start_row, start_column, frames):
    frame_cycle = itertools.cycle(frames)
    while True:
        for frame in frame_cycle:
            rows_direction, columns_direction, _ = read_controls(canvas)
            frame_height, frame_width = get_frame_size(frame)

            start_row = min(max(1, start_row + rows_direction),
                            canvas.getmaxyx()[0] - frame_height - 1)

            start_column = min(max(1, start_column + columns_direction),
                               canvas.getmaxyx()[1] - frame_width - 1)

            draw_frame(canvas, start_row, start_column, frame)
            canvas.refresh()
            await asyncio.sleep(0)
            await asyncio.sleep(0)
            draw_frame(canvas, start_row, start_column, frame, negative=True)


async def blink(canvas, row, column, symbol='*'):

    curses.start_color()
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLACK)

    while True:

        canvas.addstr(row, column, symbol, curses.color_pair(2))
        for _ in range(20):
            await asyncio.sleep(0)

        for _ in range(randint(0, 10)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.color_pair(1))
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)
    canvas.border()

    rows, columns = curses.window.getmaxyx(canvas)
    max_row, max_column = rows - 2, columns - 2

    frames = read_frames('animations/rocket_frames')

    coroutines = [
        blink(canvas, randint(2, max_row), randint(2, max_column),
              choice(['*', '+', ':'])) for _ in range(40)
    ]

    fire_coroutine = fire(
        canvas, rows / 2,
        columns / 2,
        rows_speed=-0.3,
        columns_speed=0
    )
    coroutines.append(fire_coroutine)

    rocket_corutine = animate_spaceship(
        canvas,
        rows / 2 - 1,
        columns / 2 - 1,
        frames
    )
    coroutines.append(rocket_corutine)

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
            if len(coroutines) == 0:
                break
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
