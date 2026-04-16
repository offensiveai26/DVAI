from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.db import get_db
from app.models import Progress
from app.challenges.registry import get_challenges

router = APIRouter()


@router.get("/")
def get_progress(db: Session = Depends(get_db)):
    all_challenges = get_challenges()
    completed = {p.challenge_id: p for p in db.query(Progress).all()}
    return {
        "total": len(all_challenges),
        "completed": sum(1 for p in completed.values() if p.completed),
        "challenges": {
            c["id"]: {
                "completed": completed[c["id"]].completed if c["id"] in completed else False,
                "attempts": completed[c["id"]].attempts if c["id"] in completed else 0,
            }
            for c in all_challenges
        },
    }


@router.post("/complete/{challenge_id}")
def mark_complete(challenge_id: str, db: Session = Depends(get_db)):
    progress = db.query(Progress).filter(Progress.challenge_id == challenge_id).first()
    if not progress:
        progress = Progress(challenge_id=challenge_id)
        db.add(progress)
    progress.completed = True
    progress.completed_at = datetime.utcnow()
    progress.attempts = (progress.attempts or 0) + 1
    db.commit()
    return {"status": "completed"}
