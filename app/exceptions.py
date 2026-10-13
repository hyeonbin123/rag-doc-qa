# [파일 역할] 앱 전용 예외 클래스 두 개를 정의한 파일이다.
# [현재 상태] 저장소 전체를 검색해 보면 NotFoundError와 AuthError를 import하거나 raise하는 곳이 없다. 라우터는
# FastAPI의 HTTPException(404, 401)을 직접 쓰고, 토큰 오류는 app/services/security.py의 InvalidTokenError로
# 처리한다. 지금은 쓰이지 않는 정의다.

# 찾는 대상이 없음을 뜻하는 예외(현재 사용처 없음).
class NotFoundError(Exception):
    pass


# 인증 실패를 뜻하는 예외(현재 사용처 없음).
class AuthError(Exception):
    pass
