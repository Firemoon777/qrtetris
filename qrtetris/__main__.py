import logging
import os
import sys
import time
from copy import deepcopy

import imageio
import qrcode

from qrtetris.qrtetris import QRTetris

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

data = """Я сразу смазал карту будня,
плеснувши краску из стакана;
я показал на блюде студня
косые скулы океана.
На чешуе жестяной рыбы
прочёл я зовы новых губ.
А вы
ноктюрн сыграть
могли бы
на флейте водосточных труб?"""

data = "https://selectel.ru/blog/category/selectel-news/"

program = [
    "spawn z",
    "down",
    "left",
    "down",
    "left",
    "rotate 1",
    "drop"
]

qr = QRTetris(data, program)
qr.build()
qr.cut()
qr.run()

exit(0)



qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H
)
qr.add_data(data, optimize=True)
qr.get_matrix()
qr.make()


square = [
    [True, True],
    [True, True]
]

corner = [
    [True, True, True],
    [False, True, False]
]

figures = [square, corner]
fig_num = 2
original = deepcopy(qr.modules)
step = 0

for f in range(fig_num):
    fixed = False
    x = qr.modules_count // 2
    y = 0
    figure = figures[f]
    while not fixed:
        # os.system("clear")

        qr.modules = deepcopy(original)
        for i in range(len(figure)):
            for j in range(len(figure[i])):
                qr.modules[y+i][x+j] |= figure[i][j]

        # qr.print_ascii()
        qr.make_image().save(f"/tmp/{step:04}.png")
        step += 1

        i = len(figure)
        for j in range(len(figure[-1])):
            if qr.modules[y+i][x+j] and figure[-1][j]:
                fixed = True
                original = deepcopy(qr.modules)
                break

        y += 1

        # time.sleep(0.5)

with imageio.get_writer('/tmp/movie.gif', mode='I', duration=0.3) as writer:
    for filename in [f"/tmp/{i:04}.png" for i in range(step)]:
        image = imageio.imread(filename)
        writer.append_data(image)
