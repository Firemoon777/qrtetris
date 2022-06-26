import logging
import argparse

from qrtetris.qrtetris import QRTetris

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

parser = argparse.ArgumentParser(description='Create QR animation')
parser.add_argument(
    "-d",
    "--data",
    dest="data",
    action="store",
    type=str,
    required=True,
    help="data for QR code"
)
parser.add_argument(
    "-i",
    "--interval",
    dest="interval",
    type=float,
    default=0.5,
    required=False,
    help="interval between moves in tetris (default=0.5s)"
)
parser.add_argument(
    "-f",
    "--fast-interval",
    dest="fast_interval",
    type=float,
    default=0.1,
    required=False,
    help="interval between fast moves in tetris (default=0.1s)"
)
parser.add_argument(
    "-o",
    "--output",
    dest="output",
    type=str,
    default=None,
    required=False,
    help="output filename"
)
parser.add_argument(
    "-s",
    "--show",
    dest="show",
    action="store_const",
    const=True,
    default=False,
    help="Preview image on tty"
)
parser.add_argument(
    "-p",
    "--program",
    dest="program",
    default=None,
    required=False,
    help="List of moves, or file contains moves"
)

args = parser.parse_args()
if args.program is not None:
    program = list()
    if args.program.startswith("@"):
        with open(args.program[1:], "r") as f:
            arr = f.read().strip().split("\n")
    else:
        arr = args.program.replace(";", "\n").split("\n")

    for line in arr:
        stripped = line.strip()
        if stripped:
            program.append(stripped)
else:
    program = [
        "spawn z",
        "down",
        "left",
        "down",
        "left",
        "rotate 1",
        "drop"
    ]

qr = QRTetris(args.data, program)
qr.build()
qr.cut()
qr.run(
    interval=args.interval,
    fast_interval=args.fast_interval,
    output=args.output,
    show=args.show
)

exit(0)