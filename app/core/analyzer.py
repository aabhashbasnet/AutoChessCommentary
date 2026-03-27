import chess
import chess.pgn
from io import StringIO

from app.utils.stockfish import get_stockfish


class ChessAnalyzer:

    def __init__(self, depth=15, time_per_move=1.0):
        self.stockfish = get_stockfish()
        self.depth = depth
        self.time_per_move = time_per_move

    def classify_move(self, diff):

        if diff >= 300:
            return "Blunder 🔴"
        elif diff >= 150:
            return "Mistake 🟠"
        elif diff >= 80:
            return "Inaccuracy 🟡"
        elif diff >= 30:
            return "Good 🟢"
        elif diff >= 10:
            return "Excellent ✅"
        else:
            return "Best 🔥"

    def get_eval(self):

        evaluation = self.stockfish.get_evaluation()

        if evaluation["type"] == "cp":
            return evaluation["value"]

        if evaluation["type"] == "mate":
            return 10000 if evaluation["value"] > 0 else -10000

        return 0

    def analyze_game(self, pgn_text):

        game = chess.pgn.read_game(StringIO(pgn_text))

        if not game:
            return []

        board = game.board()

        moves_data = []

        for move_number, move in enumerate(game.mainline_moves(), start=1):

            fen_before = board.fen()

            # set position before move
            self.stockfish.set_fen_position(fen_before)
            eval_before = self.get_eval()

            best_move = self.stockfish.get_best_move()

            san_move = board.san(move)

            board.push(move)

            fen_after = board.fen()

            # set position after move
            self.stockfish.set_fen_position(fen_after)
            eval_after = self.get_eval()

            diff = abs(eval_before - eval_after)

            quality = self.classify_move(diff)

            move_data = {
                "move_number": move_number,
                "move": san_move,
                "fen_before": fen_before,
                "fen_after": fen_after,
                "eval_before": eval_before,
                "eval_after": eval_after,
                "centipawn_loss": diff,
                "best_move": best_move,
                "quality": quality,
            }

            moves_data.append(move_data)

        return moves_data
