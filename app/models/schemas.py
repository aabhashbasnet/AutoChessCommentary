from pydantic import BaseModel


class PGNRequest(BaseModel):
    pgn: str
    depth: int = 15
    time_per_move: float = 1.0
