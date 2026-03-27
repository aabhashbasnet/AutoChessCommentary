from fastapi import APIRouter
from app.models.schemas import PGNRequest
from app.core.analyzer import ChessAnalyzer

router = APIRouter()


@router.post("/analyze")
def analyze_game(data: PGNRequest):

    analyzer = ChessAnalyzer(depth=data.depth, time_per_move=data.time_per_move)

    result = analyzer.analyze_game(data.pgn)

    return {"moves": result}
