import argparse

from bz import BZReaction
from conway import GameOfLife

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parent = argparse.ArugmentParser()
    parent.add_argument('--height', type=int, default=100)
    parent.add_argument('--width', type=int, default=100)
    parent.add_argument('--seed', type=int, default=100)
    parent.add_argument('--wrap', action='store_true')

    subparsers = parser.add_subparsers(title="Commands", dest="command")

    conway = subparsers.add_parser("conway", parents=[parent],
                                   help="Conway's Game of Life")
    conway.set_defaults(automaton=GameOfLife)

    bz = subparsers.add_parser("bz", parents=[parent],
                               help="Belousov–Zhabotinsky reaction")
    bz.set_defaults(automaton=BZReaction)
    bz.add_argument('k1', type=float)
    bz.add_argument('k2', type=float)
    bz.add_argument('g', type=float)

    args = parser.parse_args()

    ca = args.automaton(**vars(args)).run()
