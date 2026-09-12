from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    generation_model = (
        settings.ollama_model_name
        if settings.generation_provider == "ollama"
        else settings.claude_model_name
    )
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "db": db_status,
        "embedding_model": settings.embedding_model_name,
        "embedding_model_ko": settings.embedding_model_name_ko,
        "retrieval_mode": settings.retrieval_mode,
        "generation_provider": settings.generation_provider,
        "generation_model": generation_model,
    }
