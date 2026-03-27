from fastapi import APIRouter
from app.models.schemas import PGNRequest

router = APIRouter()


@router.post("/analyze")
def analyze_game(data: PGNRequest):
    return {"status": "received", "pgn": data.pgn}
