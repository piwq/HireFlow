import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, candidates, applications, interviews, feedbacks, files, vacancies
from app.routers import users, chat, livekit, documents, interview_requests
from app.routers import admin, notes, profile_items


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.services.telegram_bot import start_bot
    task = asyncio.create_task(start_bot())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="HR Platform", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # Basic CSP - allow all from self and some trusted external domains if needed
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' ws: wss: https:;"
    return response

app.include_router(auth.router, prefix="/api")
app.include_router(candidates.router, prefix="/api")
app.include_router(applications.router, prefix="/api")
app.include_router(interviews.router, prefix="/api")
app.include_router(feedbacks.router, prefix="/api")
app.include_router(files.router, prefix="/api")
app.include_router(vacancies.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(livekit.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(interview_requests.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(notes.router, prefix="/api")
app.include_router(profile_items.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
