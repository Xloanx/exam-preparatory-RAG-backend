from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from sqlalchemy import select

from app.api.auth import router as auth_router
from app.api.categories import router as categories_router
from app.api.documents import router as documents_router
from app.api.eval import router as eval_router
from app.api.exams import router as exams_router
from app.api.health import router as health_router
from app.api.questions import router as questions_router
from app.api.users import router as users_router
from app.config import settings
from app.db import AsyncSessionLocal, Base, engine
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.email == settings.ADMIN_EMAIL))
            admin_user = result.scalars().first()
            if not admin_user:
                session.add(
                    User(
                        email=settings.ADMIN_EMAIL,
                        password_hash=pwd_context.hash(settings.ADMIN_PASSWORD),
                        full_name="System Admin",
                        roles="ADMIN",
                    )
                )
                await session.commit()

    yield


app = FastAPI(title=settings.APP_NAME, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(categories_router, prefix=settings.API_V1_STR)
app.include_router(documents_router, prefix=settings.API_V1_STR)
app.include_router(questions_router, prefix=settings.API_V1_STR)
app.include_router(exams_router, prefix=settings.API_V1_STR)
app.include_router(eval_router, prefix=settings.API_V1_STR)
