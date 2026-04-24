# main.py
from fastapi import FastAPI
from app.db.session import Base, engine
from app.api.routes import chess, auth

Base.metadata.create_all(bind=engine)  # creates tables on startup

app = FastAPI(title="AutoChessCommentary")

app.include_router(auth.router)
app.include_router(chess.router)


@app.get("/")
def root():
    return {"message": "AutoChessCommentary running..."}
