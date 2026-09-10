
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db.session import get_db
from app.models.user import User
from app.services.embedding import EmbeddingService, get_embedding_service
from app.services.generation import GenerationService, get_generation_service
from app.services.security import InvalidTokenError, TokenType, decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = decode_token(token, TokenType.ACCESS)
    except InvalidTokenError as exc:
        raise credentials_error from exc

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_error
    return user


def get_embedder() -> EmbeddingService:
    return get_embedding_service()


def get_generator() -> GenerationService:
    return get_generation_service()


async def require_admin_token(
    x_admin_token: str = Header(...),
    settings: Settings = Depends(get_settings),
) -> None:
    if x_admin_token != settings.admin_ingest_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin token")
