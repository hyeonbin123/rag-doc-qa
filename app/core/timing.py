# [파일 역할] 코드 구간의 걸린 시간을 밀리초로 재는 작은 도구. /query/ask가 임베딩·검색·생성 단계를 따로 재서
# 응답(latency_ms)과 query_logs에 남기는 데 쓴다(app/routers/query.py).
# [왜 필요한가] README의 응답 예시·채팅 화면의 단계별 시간 막대가 이 값을 보여 준다. 어느 단계가 느린지(대부분
# 생성) 요청마다 기록해 두려는 것이다.

import time
from contextlib import contextmanager


# 한 구간의 경과 시간을 담는 객체. measure() 블록이 끝나면 elapsed_ms가 채워진다. 측정 전에는 0이다.
class Stopwatch:
    def __init__(self) -> None:
        self.elapsed_ms: int = 0

    # with sw.measure(): ... 형태로 블록 실행 시간을 잰다.
    # perf_counter를 쓰는 이유: 시스템 시계 조정의 영향을 받지 않는 단조 증가 고해상도 시계라 구간 측정에
    # 알맞다.
    # finally에서 기록하므로 블록 안에서 예외가 나도 그때까지 걸린 시간은 남는다.
    @contextmanager
    def measure(self):
        start = time.perf_counter()
        try:
            yield self
        finally:
            self.elapsed_ms = int((time.perf_counter() - start) * 1000)
