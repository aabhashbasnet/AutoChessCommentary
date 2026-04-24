# app/api/routes/chess.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.schemas import PGNRequest
from app.core.analyzer import ChessAnalyzer
from app.core.dependencies import get_current_user, get_optional_user
from app.db.session import get_db
from app.db.models import User, Game, Move

router = APIRouter(prefix="/chess", tags=["chess"])


@router.post("/analyze")
def analyze_game(
    data: PGNRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_user),
):
    analyzer = ChessAnalyzer(depth=data.depth, time_per_move=data.time_per_move)

    moves, game_result = analyzer.analyze_game(data.pgn)  # ← unpack tuple

    if current_user:
        game = Game(user_id=current_user.id, pgn=data.pgn)
        db.add(game)
        db.commit()
        db.refresh(game)

        for m in moves:
            db.add(
                Move(
                    game_id=game.id,
                    move_number=m["move_number"],
                    move=m["move"],
                    quality=m["quality"],
                    centipawn_loss=m["centipawn_loss"],
                    best_move=m["best_move"],
                    eval_before=m["eval_before"],
                    eval_after=m["eval_after"],
                )
            )
        db.commit()

        return {"game_id": game.id, "game_result": game_result, "moves": moves}

    return {"game_result": game_result, "moves": moves}


@router.get("/history")
def game_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    games = db.query(Game).filter(Game.user_id == current_user.id).all()
    return {
        "games": [{"id": g.id, "pgn": g.pgn, "created_at": g.created_at} for g in games]
    }
