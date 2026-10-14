# [테스트 묶음] 질문 기록 API(/logs, app/routers/logs.py)의 입력 검증 테스트. 잘못된 id와 범위를 벗어난 페이지
# 값이 500이 아니라 422로 끝나는지 확인한다.
# [왜 중요한가] 기록 id를 UUID로, limit을 1~100, offset을 0 이상으로 검증하기 전에는 이런 입력이 Postgres까지
# 가서 500이 났다(커밋 9e7d6eb).

import uuid

import pytest


# UUID가 아닌 기록 id는 422.
@pytest.mark.asyncio
async def test_a_malformed_log_id_is_rejected_not_a_server_error(authed_client):
    resp = await authed_client.get("/logs/not-a-uuid")
    assert resp.status_code == 422


# 형식은 맞지만 없는(또는 다른 사용자의) 기록 id는 404.
@pytest.mark.asyncio
async def test_an_unknown_log_id_is_not_found(authed_client):
    resp = await authed_client.get(f"/logs/{uuid.uuid4()}")
    assert resp.status_code == 404


# limit 음수·0·101, offset 음수는 모두 422. 경계 밖 값 네 가지를 parametrize로 한 번에 검사한다.
@pytest.mark.asyncio
@pytest.mark.parametrize("query", ["limit=-1", "offset=-1", "limit=0", "limit=101"])
async def test_paging_outside_the_bounds_is_rejected(authed_client, query):
    # 예전에는 음수 값이 Postgres까지 가서 거부되며 500이 났다.
    resp = await authed_client.get(f"/logs?{query}")
    assert resp.status_code == 422


# 경계 안의 최댓값(limit=100, offset=0)은 200이고, 질문한 적이 없는 새 사용자라 빈 목록이다.
@pytest.mark.asyncio
async def test_paging_within_the_bounds_works(authed_client):
    resp = await authed_client.get("/logs?limit=100&offset=0")
    assert resp.status_code == 200
    assert resp.json() == []
