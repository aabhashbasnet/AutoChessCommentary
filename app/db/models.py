# app/db/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    games = relationship("Game", back_populates="user")


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pgn = Column(Text, nullable=False)
    opening = Column(String, nullable=True)
    accuracy = Column(Float, nullable=True)
    result = Column(String, nullable=True)  # "1-0", "0-1", "1/2-1/2"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="games")
    moves = relationship("Move", back_populates="game")


class Move(Base):
    __tablename__ = "moves"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    move_number = Column(Integer, nullable=False)
    move = Column(String, nullable=False)
    quality = Column(String, nullable=False)
    centipawn_loss = Column(Integer, nullable=False)
    best_move = Column(String, nullable=True)
    eval_before = Column(Float, nullable=True)
    eval_after = Column(Float, nullable=True)

    game = relationship("Game", back_populates="moves")
