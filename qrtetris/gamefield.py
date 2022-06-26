import os
import tempfile
import time
from copy import deepcopy
from typing import List, Tuple, Optional

import imageio
from qrcode import QRCode


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


class GameField:
    qr: QRCode
    interval: float
    fast_interval: float

    tty_enabled: bool = False

    gif_enabled: bool = True
    gif_output: Optional[str]
    gif_duration: List[int]
    gif_frame_number = 0
    gif_frame_mask = "{prefix}/{step:04}.png"
    gif_tmp_dir = None

    FIGURE_SQUARE = 0
    FIGURE_T = 1
    FIGURE_Z = 2
    FIGURE_Z_REVERSED = 3
    FIGURE_I = 4

    figures = {
        FIGURE_SQUARE: [
            [True, True],
            [True, True]
        ],
        FIGURE_T: [
            [True, True, True],
            [False, True, False]
        ],
        FIGURE_Z: [
            [True, True, False],
            [False, True, True],
        ],
        FIGURE_Z_REVERSED: [
            [False, True, True],
            [True, True, False],
        ],
        FIGURE_I: [
            [True, True, True, True]
        ]
    }
    fig_names = {
        "square": FIGURE_SQUARE,
        "t": FIGURE_T,
        "z": FIGURE_Z,
        "z_reversed": FIGURE_Z_REVERSED,
        "i": FIGURE_I
    }

    modules: List[List[bool]]
    current_figure: List[List[bool]]
    current_position: Tuple[int, int]

    def __init__(
            self,
            qr,
            interval=0.5,
            fast_interval=0.1,
            gif_output=None,
            tty_enabled=True
    ):
        self.qr = qr
        self.interval = interval
        self.fast_interval = fast_interval
        self.gif_output = gif_output
        self.gif_duration = list()
        if self.gif_output:
            self.gif_tmp_dir = tempfile.TemporaryDirectory()
        self.tty_enabled = tty_enabled

        self.current_position = self.qr.modules_count / 2, 0
        self.current_figure = [[]]

        self.save()
        self.draw(fast=False)

    def save(self):
        self.modules = deepcopy(self.qr.modules)

    def load(self):
        self.qr.modules = deepcopy(self.modules)

    def cleanup(self):
        if self.gif_tmp_dir:
            self.gif_tmp_dir.cleanup()

    def _is_next_move_available(self) -> bool:
        x, y = self.current_position
        n, m = len(self.current_figure[0]), len(self.current_figure)

        for i in range(m):
            for j in range(n):
                if self.qr.modules[y+i][x+j] and not self.current_figure[i][j]:
                    return False

        for j in range(n):
            if self.qr.modules[y+m][x+j] and self.current_figure[-1][j]:
                return False

        return True

    def draw(self, fast=False):
        self.load()
        x, y = self.current_position
        n, m = len(self.current_figure[0]), len(self.current_figure)

        for i in range(m):
            for j in range(n):
                self.qr.modules[y+i][x+j] |= self.current_figure[i][j]

        if self.tty_enabled:
            cls()
            self.qr.print_ascii()
            time.sleep(self.fast_interval if fast else self.interval)

        if self.gif_output:
            filename = self.gif_frame_mask.format(
                prefix=self.gif_tmp_dir.name,
                step=self.gif_frame_number
            )
            self.gif_frame_number += 1
            self.qr.make_image().save(filename)
            self.gif_duration.append(self.fast_interval if fast else self.interval)

    def execute(self, instruction: str):
        tokens = instruction.split(" ")
        cmd = tokens[0]
        args = tokens[1:]
        try:
            f = getattr(self, f"move_{cmd}")
        except AttributeError:
            return
        f(*args)

        self.draw(fast=False)

    def save_gif(self):
        with imageio.get_writer(self.gif_output, mode='I', duration=self.gif_duration) as writer:
            filenames = [
                self.gif_frame_mask.format(prefix=self.gif_tmp_dir.name, step=i)
                for i in range(self.gif_frame_number)
            ]
            for filename in filenames:
                image = imageio.imread(filename)
                writer.append_data(image)

    def move_spawn(self, *args):
        try:
            fig = args[0]
        except IndexError:
            fig = 0

        if isinstance(fig, str):
            fig = self.fig_names.get(fig.lower(), 0)

        self.save()

        self.current_figure = deepcopy(self.figures[fig])
        self.current_position = (self.qr.modules_count // 2, 0)

    def _get_step(self, *args) -> int:
        try:
            return max(int(args[0]), 1)
        except (IndexError, ValueError):
            return 1

    def move_down(self, *args):
        step = self._get_step(*args)
        x, y = self.current_position
        self.current_position = x, y + step

    def move_right(self, *args):
        step = self._get_step(*args)
        x, y = self.current_position
        self.current_position = x + step, y

    def move_left(self, *args):
        step = self._get_step(*args)
        x, y = self.current_position
        self.current_position = x - step, y

    def move_drop(self, *_):
        while self._is_next_move_available():
            self.move_down(1)
            self.draw(fast=True)

    def move_rotate(self, *args):
        try:
            angle = int(args[0])
            angle = min(max(angle, 1), 4)
        except (ValueError, IndexError):
            angle = 1

        for _ in range(angle):
            n, m = len(self.current_figure[0]), len(self.current_figure)
            tmp = []
            for i in range(n):
                row = []
                for j in range(m):
                    row.append(self.current_figure[m-j-1][i])
                tmp.append(row)
            self.current_figure = deepcopy(tmp)