# [파일 역할] 질문 기록 조회 API(GET /logs, GET /logs/{id}). /query/ask가 남긴 query_logs 가운데 로그인한
# 사용자 본인 것만 돌려준다.
# [누가 쓰나] 채팅 화면이 로그인할 때 /logs?limit=10으로 최근 질문을 불러오고, 각 항목을 /logs/{id}로 다시
# 받아 출처와 지연을 그린다(app/web/static/chat.js).

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.query_log import QueryLog
from app.models.user import User
from app.schemas.logs import QueryLogDetail, QueryLogSummary

router = APIRouter(prefix="/logs", tags=["logs"])


# 내 질문 기록 목록(최신순). limit은 1~100, offset은 0 이상으로 제한해 범위를 벗어난 값은 422가 된다. WHERE
# user_id = 현재 사용자 조건으로 다른 사람의 기록은 보이지 않는다.
@router.get("", response_model=list[QueryLogSummary])
async def list_logs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[QueryLog]:
    result = await db.execute(
        select(QueryLog)
        .where(QueryLog.user_id == current_user.id)
        .order_by(QueryLog.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all())


# 기록 하나의 상세(검색 결과, 토큰, 단계별 지연). log_id를 UUID로 받아 형식이 틀리면 422다.
# 남의 기록이면 403이 아니라 '없음'과 같은 404를 돌려줘, 그 id의 기록이 있는지조차 알 수 없게 한다.
@router.get("/{log_id}", response_model=QueryLogDetail)
async def get_log(
    log_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QueryLog:
    log = await db.get(QueryLog, log_id)
    if log is None or log.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return log
