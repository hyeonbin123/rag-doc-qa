# [파일 역할] 상태 확인 API(GET /health). DB 연결이 되는지와 지금 서버가 어떤 모델·검색 모드로 도는지 알려
# 준다.
# [누가 쓰나] 채팅 화면이 맨 위 상태 줄에 이 값을 보여 준다(app/web/static/chat.js). 배포 뒤 설정 확인(예:
# 한국어 임베딩 모델이 무엇으로 떠 있는지)에도 쓸 수 있다.

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db.session import get_db

router = APIRouter(tags=["health"])


# 인증 없이 열려 있는 상태 확인. DB에 SELECT 1을 보내 연결을 확인하고, 실패해도 예외를 밖으로 던지지 않고
# status="degraded", db="error"로 응답한다. 그래서 DB가 죽어도 이 엔드포인트는 500 대신 상태를 알려 준다.
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

    # 현재 생성 제공자에 맞는 모델 이름을 고른다(Ollama면 Ollama 모델, 아니면 Claude 모델).
    generation_model = (
        settings.ollama_model_name
        if settings.generation_provider == "ollama"
        else settings.claude_model_name
    )
    # 설정값만 보고하며 비밀값(API 키, JWT 키, 관리자 토큰)은 넣지 않는다.
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "db": db_status,
        "embedding_model": settings.embedding_model_name,
        "embedding_model_ko": settings.embedding_model_name_ko,
        "retrieval_mode": settings.retrieval_mode,
        "generation_provider": settings.generation_provider,
        "generation_model": generation_model,
    }
