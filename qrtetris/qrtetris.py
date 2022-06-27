from copy import deepcopy
from logging import getLogger
from typing import Optional, Tuple, List

import numpy as np

import qrcode
from qrcode import QRCode

from qrtetris.gamefield import GameField

logger = getLogger(__name__)


class QRTetris:

    qr: Optional[QRCode]
    content: str
    program: Optional[List]

    markers: Tuple[int, int]

    def __init__(self, content: str, program: str):
        self.content = content
        self.qr = None
        self.program = program

    def build(self):
        self.qr = QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_H
        )
        self.qr.add_data(self.content, optimize=True)
        self.qr.make()

    def _find_markers(self):
        s = 0
        while self.qr.modules[0][s] is True and self.qr.modules[0][s + 1] is True:
            s += 1
        s += 1

        f = self.qr.modules_count - 1
        while self.qr.modules[0][f] is True and self.qr.modules[0][f - 1] is True:
            f -= 1
        f -= 1

        self.markers = s, f

    def get_points(self):
        d = self.qr.modules_count // 3
        s, f = self.markers

        return [
            (s, 0),
            (f, 0),
            ((s+f) / 2, -d)
        ]

    def cut(self):
        if self.qr is None:
            logger.error(f"No QR code generated. Call build() first!")
            return

        self._find_markers()

        points = self.get_points()
        count = len(points)

        A = []
        b = []
        for x, y in points:
            A.append(
                [x**i for i in reversed(range(count))]
            )
            b.append(y)

        result = tuple(np.linalg.solve(A, b))
        logger.debug(f"Solution: {result}")

        for i in range(self.qr.modules_count):
            for j in range(self.qr.modules_count):
                s = 0
                for index, k in enumerate(reversed(range(count))):
                    s += result[index] * j**k
                if s < -i:
                    self.qr.modules[i][j] = False

    def print_ascii(self, **kwargs):
        if self.qr is None:
            logger.error(f"No QR code generated. Call build() first!")
            return

        self.qr.print_ascii(**kwargs)

    def rotate(self, clockwise=True):
        if self.qr is None:
            logger.error(f"No QR code generated. Call build() first!")
            return

        modules = deepcopy(self.qr.modules)
        n = self.qr.modules_count
        for i in range(n):
            for j in range(n):
                if clockwise:
                    self.qr.modules[j][n-i-1] = modules[i][j]
                else:
                    self.qr.modules[i][j] = modules[j][n-i-1]

    def run(
            self,
            interval = 0.5,
            fast_interval = 0.1,
            output: Optional[str] = None,
            show=True
    ):
        field = GameField(
            self.qr,
            interval=interval,
            fast_interval=fast_interval,
            gif_output=output,
            tty_enabled=show
        )

        for instruction in self.program:
            field.execute(instruction)

        if output:
            field.save_gif()

        field.cleanup()
