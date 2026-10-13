# [파일 역할] 모든 ORM 모델(app/models/*)이 상속하는 SQLAlchemy 2.0 선언형 기반 클래스.
# [왜 따로 두나] 모델들이 같은 Base.metadata에 등록되어야 Alembic(alembic/env.py의 target_metadata)과
# 테스트(tests/conftest.py의 Base.metadata.create_all)가 전체 스키마를 한 번에 볼 수 있다. 모델 파일과 분리해
# 두면 순환 import 없이 어디서든 가져올 수 있다.

from sqlalchemy.orm import DeclarativeBase


# 추가 설정 없는 기본 선언형 Base. 테이블 정의는 각 모델 클래스가 Mapped[...] 타입 힌트로 한다.
class Base(DeclarativeBase):
    pass
