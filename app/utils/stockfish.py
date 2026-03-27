from stockfish import Stockfish
import os
from os import path


def get_stockfish():
    path.os.getenv("STOCKFISH_PATH")
    stockfish = Stockfish(path)
    stockfish.set_depth(15)
    return stockfish
