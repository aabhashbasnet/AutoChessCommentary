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
        game_result = None  # ← track result

        for move_number, move in enumerate(game.mainline_moves(), start=1):
            fen_before = board.fen()
            is_white_turn = board.turn == chess.WHITE

            self.stockfish.set_fen_position(fen_before)
            eval_before = self.get_eval()
            best_move = self.stockfish.get_best_move()

            san_move = board.san(move)
            board.push(move)

            fen_after = board.fen()
            self.stockfish.set_fen_position(fen_after)
            eval_after = self.get_eval()

            eval_before_white = eval_before if is_white_turn else -eval_before
            eval_after_white = -eval_after if is_white_turn else eval_after

            if is_white_turn:
                cpl = max(0, eval_before_white - eval_after_white)
            else:
                cpl = max(0, eval_after_white - eval_before_white)

            # ✅ detect special endings
            is_checkmate = board.is_checkmate()
            is_stalemate = board.is_stalemate()
            is_draw = board.is_insufficient_material() or board.is_seventyfive_moves()

            if is_checkmate:
                quality = "Checkmate 🏆" if is_white_turn else "Checkmate 🏆"
                game_result = "White wins" if is_white_turn else "Black wins"
                cpl = 0  # delivering checkmate is not a blunder
            elif is_stalemate:
                game_result = "Stalemate 🤝"
                quality = self.classify_move(cpl)
            elif is_draw:
                game_result = "Draw 🤝"
                quality = self.classify_move(cpl)
            else:
                quality = self.classify_move(cpl)

            moves_data.append(
                {
                    "move_number": move_number,
                    "move": san_move,
                    "fen_before": fen_before,
                    "fen_after": fen_after,
                    "eval_before": eval_before_white,
                    "eval_after": eval_after_white,
                    "centipawn_loss": cpl,
                    "best_move": best_move,
                    "quality": quality,
                    "is_checkmate": is_checkmate,  # ← new
                    "is_stalemate": is_stalemate,  # ← new
                }
            )

        return moves_data, game_result  # ← return result too
