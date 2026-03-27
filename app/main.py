from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="AutoChessCommentary")

app.include_router(router)


@app.get("/")
def root():
    return {"message": "AutoChessCommentary running..."}
