from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import db
from app.models.user import User

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
    }
    from app.config import settings

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str:
    from app.config import settings

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def get_db():
    from app import db as _db

    async with _db.AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    token: str | None = Header(default=None, alias="Authorization"),
    session: AsyncSession = Depends(get_db),
) -> User:
    scheme, _, credentials = (token or "").partition(" ")
    if scheme.lower() != "bearer" or not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    subject = decode_access_token(credentials)
    result = await session.execute(select(User).where(User.email == subject))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def _user_is_admin(user: User) -> bool:
    return bool(user.roles) and "ADMIN" in user.roles.upper().split(",")


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not _user_is_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return user


async def get_current_user_id(user: User = Depends(get_current_user)) -> int:
    return user.id


@router.post("/auth/register", status_code=201)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_db)):
    existing = (
        (await session.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=pwd_context.hash(payload.password),
        full_name=payload.full_name,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_access_token(user.email)
    return {"access_token": token, "token_type": "bearer", "user": {"email": user.email}}


@router.post("/auth/login")
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not user.password_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not pwd_context.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user.email)
    return {"access_token": token, "token_type": "bearer", "user": {"email": user.email}}


@router.get("/auth/me")
async def me(user: User = Depends(get_current_user)):
    return {"user": {"email": user.email, "full_name": user.full_name}}
