"""Worker threads for CPU-bound model calls.

Model calls (embeddings, the cross-encoder) are too slow to run on the event loop:
while one runs, every other request the server is handling waits. With six questions
sent at once, a static page request waited up to 0.7 s. They run on a pool of
MODEL_THREADS worker threads instead.

The default of 6 was measured against 1 on the running stack (six concurrent
questions while a static page was requested every 20 ms, four rounds each):
- 1 thread: calls never compete for CPU cores, but queued embeddings waited up to
  2.5 s and one page request still took 242 ms.
- 6 threads: every page request stayed under the 200 ms budget, and each embedding
  took a steady 0.5-0.6 s. Total response times were about the same (mostly
  generation), 10.6 s against 10.0 s on average.
"""

# [파일 역할] CPU를 오래 쓰는 동기 모델 호출(임베딩, cross-encoder)을 전용 스레드 풀에서 돌리는 한
# 함수(run_model)를 제공한다.
# [왜 필요한가] 위 docstring처럼 비동기 핸들러 안에서 모델을 그대로 부르면 그동안 이벤트 루프 전체가 멈춘다.
# 별도 풀에 넘기면 루프는 다른 요청을 계속 처리하고, 모델 호출만 풀 크기(MODEL_THREADS)만큼 동시에 돈다.
# [왜 전용 풀인가] 다른 용도의 스레드 풀(asyncio의 기본 실행기, Starlette의 run_in_threadpool)과 나눠 두면
# 동시에 도는 모델 호출 수를 정확히 MODEL_THREADS로 묶을 수 있다. 로그인의 bcrypt는 일부러 이 풀이 아니라
# run_in_threadpool을 써서 임베딩 뒤에 줄 서지 않게 한다(app/routers/auth.py 주석).
# [호출 위치] 질문 임베딩(app/routers/query.py), 재정렬 점수(app/services/retrieval.py의 rerank_search), 적재
# 임베딩(app/services/ingestion.py). 동작은 tests/test_event_loop.py가 느린 가짜 모델로 확인한다.

import asyncio
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache, partial
from typing import TypeVar

from app.config import get_settings

# run_model이 넘겨받은 함수의 반환 타입을 그대로 돌려준다는 것을 타입 검사기에 알려 주는 타입 변수.
T = TypeVar("T")


# 프로세스 전체가 공유하는 모델 스레드 풀을 처음 쓸 때 한 번만 만든다(lru_cache). 풀 크기는 설정
# MODEL_THREADS(기본 6, README에 1개와 6개를 실제 스택에서 비교한 결과가 있다). 스레드 이름 앞에 model을 붙여
# 디버깅할 때 어느 스레드인지 알아보기 쉽게 한다.
@lru_cache
def _model_threads() -> ThreadPoolExecutor:
    return ThreadPoolExecutor(
        max_workers=get_settings().model_threads, thread_name_prefix="model"
    )


# fn(*args)를 모델 스레드에서 실행하고 결과를 기다린다. 스레드가 모두 바쁘면 풀의 대기열에서 차례를 기다린다.
# 기다리는 동안 이벤트 루프는 다른 요청을 처리한다.
# run_in_executor에는 partial로 함수와 인자를 묶어 넘긴다. 예외가 나면 그대로 호출한 쪽의 await에서 다시
# 올라온다.
async def run_model(fn: Callable[..., T], *args) -> T:
    """Run `fn(*args)` on a model thread, queued if all of them are busy."""
    return await asyncio.get_running_loop().run_in_executor(_model_threads(), partial(fn, *args))
