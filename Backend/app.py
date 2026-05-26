import asyncio
from contextlib import asynccontextmanager
from datetime import datetime


from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from core.background import sync_all_active_users
from core.security import limiter
from database import ALLOWED_ORIGIN
from routers import analytics, assignments, attendance, auth, notes, submissions, system, users



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Run user-session background sync
    background_task = asyncio.create_task(sync_all_active_users())
    yield
    # Shutdown: Clean up background tasks
    background_task.cancel()
    try:
        await background_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Internship Portal API Backend",
    description="Constructed utilizing FastAPI natively paired with Supabase HTTP clients.",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

allowed_origins = {
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8888",
    "http://127.0.0.1:8888",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://v2v-internship-portal-frontend.vercel.app/"
}
if ALLOWED_ORIGIN:
    origin = ALLOWED_ORIGIN.rstrip("/")
    allowed_origins.add(origin)
    # Add common variations if user provided a specific one
    if "127.0.0.1" in origin:
        allowed_origins.add(origin.replace("127.0.0.1", "localhost"))
    elif "localhost" in origin:
        allowed_origins.add(origin.replace("localhost", "127.0.0.1"))
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(assignments.router)
app.include_router(notes.router)
app.include_router(submissions.router)
app.include_router(attendance.router)
app.include_router(analytics.router)
app.include_router(system.router)


@app.get("/")
@limiter.limit("5/minute")
async def health_check(request: Request):
    return {"status": "Active", "environment": "Production-Ready", "framework": "FastAPI + Supabase"}

@app.get("/health")
async def health(request:Request):
    return {"status": 200, "message": "OK", "timestamp": datetime.now().isoformat()}

