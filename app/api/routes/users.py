# app/api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, Game
from app.core.dependencies import get_current_user
from app.models.schemas import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/me/stats")
def get_my_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    games = db.query(Game).filter(Game.user_id == current_user.id).all()

    if not games:
        return {"total_games": 0, "message": "No games analyzed yet"}

    return {
        "username": current_user.username,
        "total_games": len(games),
        "joined": current_user.created_at,
    }


@router.delete("/me")
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted successfully"}
