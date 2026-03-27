import os
from stockfish import Stockfish
from dotenv import load_dotenv

load_dotenv()


def get_stockfish():

    path = os.getenv("STOCKFISH_PATH")

    if not path:
        raise Exception("Stockfish path not found in .env")

    stockfish = Stockfish(path)

    stockfish.set_depth(15)

    return stockfish
