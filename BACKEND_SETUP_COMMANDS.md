# Backend Scaffold — Step-by-Step Commands (Phase 1)

Project: ITF Exam Preparation RAG Platform — Backend (`exam-prep-rag-backend`)

## 1. Create backend source directory structure

```powershell
New-Item -ItemType Directory -Force -Path "exam-prep-rag-backend/app/api"
New-Item -ItemType Directory -Force -Path "exam-prep-rag-backend/app/services"
New-Item -ItemType Directory -Force -Path "exam-prep-rag-backend/app/models"
New-Item -ItemType Directory -Force -Path "exam-prep-rag-backend/app/db"
New-Item -ItemType Directory -Force -Path "exam-prep-rag-backend/app/core"
New-Item -ItemType Directory -Force -Path "exam-prep-rag-backend/tests"
```

## 2. Create virtual environment + install backend dependencies

```powershell
cd exam-prep-rag-backend
python -m venv .venv
.\.venv\Scripts/python.exe -m pip install fastapi "uvicorn[standard]" sqlalchemy aiosqlite alembic pydantic pydantic-settings python-multipart python-jose passlib[bcrypt] bcrypt python-dotenv pytest pytest-asyncio httpx
```

## 3. Write backend source files

- `exam-prep-rag-backend/requirements.txt`
- `exam-prep-rag-backend/app/__init__.py`
- `exam-prep-rag-backend/app/main.py`
- `exam-prep-rag-backend/app/config.py`
- `exam-prep-rag-backend/app/db.py`
- `exam-prep-rag-backend/app/models/*.py`
- `exam-prep-rag-backend/app/api/*.py`
- `exam-prep-rag-backend/app/services/*.py`
- `exam-prep-rag-backend/tests/test_health.py`

## 4. Run backend

```powershell
cd exam-prep-rag-backend
.\.venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 5. Test backend

```powershell
# Option A — direct HTTP check (server must be running on :8000)
curl.exe http://127.0.0.1:8000/api/v1/health
# or
Invoke-WebRequest -Uri http://127.0.0.1:8000/api/v1/health

# Option B — pytest
cd exam-prep-rag-backend
.\.venv/Scripts/python.exe -m pytest tests/ -v
```
