from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, candidates, applications, interviews, feedbacks, files, vacancies
from app.routers import users, chat, livekit

app = FastAPI(title="HR Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:80", "http://frontend:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/api/health")
async def health():
    return {"status": "ok"}
