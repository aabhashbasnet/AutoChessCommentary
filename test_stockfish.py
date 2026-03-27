from app.utils.stockfish import get_stockfish
import chess

stockfish = get_stockfish()

board = chess.Board()

board.push_san("e4")
board.push_san("e5")

stockfish.set_fen_position(board.fen())

print("Best move:", stockfish.get_best_move())
print("Evaluation:", stockfish.get_evaluation())
