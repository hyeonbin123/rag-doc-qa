# [파일 역할] 앱의 기본 로깅 형식을 한곳에서 정한다. app/main.py의 lifespan이 서버 시작 때 한 번 부른다.

import logging


# 루트 로거를 INFO 수준, '시각 수준 로거이름 메시지' 형식으로 설정한다. 로거 이름(%(name)s)이 찍히므로 어느
# 모듈에서 나온 로그인지 구분할 수 있다.
# basicConfig는 루트 로거에 핸들러가 이미 있으면 아무것도 하지 않으므로, 여러 번 불려도 핸들러가 중복으로 붙지
# 않는다.
def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
