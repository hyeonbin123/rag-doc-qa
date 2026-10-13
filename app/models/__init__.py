# [파일 역할] ORM 모델 네 개(Chunk, Document, QueryLog, User)를 한 패키지로 묶어 내보낸다.
# [왜 필요한가] 이 패키지를 import하면 네 모델 파일이 모두 실행되어 Base.metadata에 테이블이 등록된다.
# alembic/env.py가 `from app.models import ...`로 이 효과를 이용한다. relationship("Document") 같은 문자열
# 참조도 상대 모델이 등록돼 있어야 풀리므로, 모델을 한꺼번에 불러오는 지점이 있으면 안전하다.

from app.models.chunk import Chunk
from app.models.document import Document
from app.models.query_log import QueryLog
from app.models.user import User

# from app.models import * 로 내보낼 이름 목록.
__all__ = ["Chunk", "Document", "QueryLog", "User"]
