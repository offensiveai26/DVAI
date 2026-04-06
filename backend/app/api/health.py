from fastapi import APIRouter
from app.llm import _check_ollama, reset_status

router = APIRouter()


@router.get("/health")
async def health_check():
    ollama_ok = await _check_ollama()
    return {
        "status": "ok",
        "service": "dvai",
        "ollama": "connected" if ollama_ok else "not connected (simulation mode)",
    }


@router.post("/health/reset-ollama")
async def reset_ollama():
    reset_status()
    ollama_ok = await _check_ollama()
    return {"ollama": "connected" if ollama_ok else "not connected"}
