# [파일 역할] 질문 기록 조회 API(GET /logs, GET /logs/{id}). /query/ask가 남긴 query_logs 가운데 로그인한
# 사용자 본인 것만 돌려준다.
# [누가 쓰나] 채팅 화면이 로그인할 때 /logs?limit=10&detail=true 한 번으로 최근 질문과 그 출처·단계별
# 지연을 받아 그린다(app/web/static/chat.js). 예전에는 요약 목록을 받은 뒤 항목마다 /logs/{id}를 다시
# 불러, 로그인마다 요청 11번(요청마다 토큰 확인과 사용자 조회 포함)이 들었다.

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import TypeAdapter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.query_log import QueryLog
from app.models.user import User
from app.schemas.logs import QueryLogDetail, QueryLogSummary

router = APIRouter(prefix="/logs", tags=["logs"])

# 목록 응답을 검증하고 JSON 바이트로 직렬화하는 어댑터. detail 값에 따라 둘 중 하나를 쓴다.
# - FastAPI가 response_model로 하던 일(ORM 객체를 from_attributes로 검증한 뒤 Pydantic이 바로 JSON 바이트로
#   직렬화, fastapi/routing.py의 serialize_response)을 그대로 따라 하므로, 기본(요약) 응답은 detail 인자가
#   생기기 전과 바이트 단위로 같다(tests/test_logs.py가 그때의 실제 응답 바이트로 고정).
# - 응답 모델을 두 모양의 합집합(list[요약] | list[상세])으로 두고 검증·직렬화를 FastAPI에 맡기지 않는 이유:
#   ORM 객체는 두 모양 모두에 맞고, 그때 Pydantic의 합집합 검증은 필드가 더 많은 상세 쪽을 고른다(Pydantic
#   2.13에서 확인). 그러면 detail을 주지 않은 기본 응답에도 상세 필드가 섞인다.
SUMMARY_LIST = TypeAdapter(list[QueryLogSummary])
DETAIL_LIST = TypeAdapter(list[QueryLogDetail])


# 내 질문 기록 목록(최신순). limit은 1~100, offset은 0 이상으로 제한해 범위를 벗어난 값은 422가 된다. WHERE
# user_id = 현재 사용자 조건으로 다른 사람의 기록은 보이지 않는다. 이 질의는 query_logs의
# (user_id, created_at DESC) 인덱스로 정렬 없이 읽힌다(app/models/query_log.py, 마이그레이션 0005).
# detail=true면 항목마다 단건 상세(GET /logs/{id})와 같은 필드(검색된 청크, 모델 이름, 토큰 수, 단계별 지연)를
# 담는다. 질의는 detail과 상관없이 같은 행 전체를 읽으므로 DB 비용은 같고, 응답만 길어진다. detail은 참·거짓
# 값만 받아 'maybe' 같은 값은 422다.
# response_model은 OpenAPI 문서에 두 응답 모양을 모두 적는 데만 쓰인다. 함수가 Response를 직접 돌려주므로
# FastAPI는 이를 다시 검증·직렬화하지 않는다(위 어댑터가 한다).
@router.get("", response_model=list[QueryLogSummary] | list[QueryLogDetail])
async def list_logs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    # 아래 description은 OpenAPI 문서(/docs)에 그대로 나가는 글이라 다른 API 문구처럼 영어로 둔다.
    detail: bool = Query(
        False,
        description=(
            "Return every log with the fields of GET /logs/{log_id} (retrieved chunks, model, "
            "token counts and step latencies) instead of the summary."
        ),
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    result = await db.execute(
        select(QueryLog)
        .where(QueryLog.user_id == current_user.id)
        .order_by(QueryLog.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    adapter = DETAIL_LIST if detail else SUMMARY_LIST
    logs = adapter.validate_python(result.scalars().all(), from_attributes=True)
    # by_alias=True도 FastAPI의 기본값(response_model_by_alias)과 같게 둔다. 지금 두 스키마에는 별칭이 없다.
    return Response(content=adapter.dump_json(logs, by_alias=True), media_type="application/json")


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
