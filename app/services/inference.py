"""CPU를 쓰는 모델 호출용 작업 스레드.

모델 호출(임베딩, cross-encoder)은 이벤트 루프에서 돌리기에는 너무 느리다. 하나가 도는 동안 서버가 처리
중인 다른 요청이 모두 기다린다. 질문 6개를 한꺼번에 보내자 정적 페이지 요청 하나가 최대 0.7초 기다렸다.
그래서 모델 호출은 MODEL_THREADS개의 작업 스레드 풀에서 돌린다.

기본값 6은 실제로 띄운 스택에서 1과 비교해 정했다(질문 6개를 동시에 보내면서 정적 페이지를 20ms마다
요청, 각 4회):
- 스레드 1개: 호출끼리 CPU 코어를 다투지는 않지만, 줄 선 임베딩이 최대 2.5초 기다렸고 페이지 요청
  하나는 여전히 242ms 걸렸다.
- 스레드 6개: 페이지 요청이 모두 200ms 예산 안에 들었고, 임베딩은 한 번에 0.5~0.6초로 고르게 걸렸다.
  전체 응답 시간은 거의 같았다(대부분 생성 시간). 평균 10.6초 대 10.0초.
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
    """`fn(*args)`를 모델 스레드에서 실행한다. 스레드가 모두 바쁘면 대기열에서 차례를 기다린다."""
    return await asyncio.get_running_loop().run_in_executor(_model_threads(), partial(fn, *args))
