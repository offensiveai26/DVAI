from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
import importlib

from app.challenges.registry import get_categories, get_challenges, get_challenge
from app.db import get_db
from app.models import Progress

router = APIRouter()


class ChallengeInput(BaseModel):
    input: str
    difficulty: int = 1


class FlagSubmission(BaseModel):
    flag: str


@router.get("/categories")
def list_categories():
    return get_categories()


@router.get("/")
def list_challenges(category: Optional[str] = None):
    challenges = get_challenges(category)
    # Strip flags and module paths from response
    return [
        {k: v for k, v in c.items() if k not in ("flag", "module")}
        for c in challenges
    ]


@router.get("/{challenge_id}")
def get_challenge_detail(challenge_id: str):
    challenge = get_challenge(challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    # Strip flag from response
    return {k: v for k, v in challenge.items() if k != "flag"}


@router.post("/{challenge_id}/interact")
async def interact(challenge_id: str, body: ChallengeInput):
    challenge = get_challenge(challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    try:
        mod = importlib.import_module(challenge["module"])
        result = await mod.handle(body.input, body.difficulty)
        return result
    except ModuleNotFoundError:
        raise HTTPException(status_code=501, detail="Challenge not yet implemented")


@router.post("/{challenge_id}/submit")
def submit_flag(challenge_id: str, body: FlagSubmission, db: Session = Depends(get_db)):
    challenge = get_challenge(challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    correct = body.flag.strip() == challenge["flag"]
    if correct:
        progress = db.query(Progress).filter(Progress.challenge_id == challenge_id).first()
        if not progress:
            progress = Progress(challenge_id=challenge_id)
            db.add(progress)
        progress.completed = True
        progress.completed_at = datetime.utcnow()
        progress.attempts = (progress.attempts or 0) + 1
        db.commit()
    return {"correct": correct, "message": "🎉 Flag captured!" if correct else "❌ Wrong flag. Keep trying!"}
