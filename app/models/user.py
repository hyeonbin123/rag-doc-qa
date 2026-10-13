# [파일 역할] users 테이블의 ORM 모델. JWT 로그인 계정 한 개가 한 행이다.
# [연결] 가입·로그인(app/routers/auth.py, app/services/users.py), 토큰 검증(app/dependencies.py의
# get_current_user), 데모 계정 시드(scripts/seed_demo_user.py)가 쓴다.

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


# - email: 가입 때 EmailStr로 정규화한 주소(도메인 소문자). unique라 같은 주소로 두 번 가입할 수 없고(라우터가
#   409), 로그인 조회용 인덱스가 있다.
# - hashed_password: bcrypt 해시 문자열. 원문 비밀번호는 저장하지 않는다.
# - is_active: False면 토큰이 유효해도 인증을 거부한다(get_current_user, /auth/refresh). default=True는 파이썬
#   쪽 기본값이고, 마이그레이션 0001에는 DB 기본값(true)도 있다.
class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
