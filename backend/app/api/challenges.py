from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import importlib

from app.challenges.registry import get_categories, get_challenges, get_challenge

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
def submit_flag(challenge_id: str, body: FlagSubmission):
    challenge = get_challenge(challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    correct = body.flag.strip() == challenge["flag"]
    return {"correct": correct, "message": "🎉 Flag captured!" if correct else "❌ Wrong flag. Keep trying!"}
