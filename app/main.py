# MARK: - main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.routers import auth, tasks, users, chat, payments, circles 

settings = get_settings()

# 1. Initialize the Rate Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(
    title="HABO MicroGigs API",
    description="Help a Brother Out — hyper-local micro-gig marketplace",
    version="2.0.0",
)

# 2. Register the Limiter state and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 3. Secure CORS Middleware (Restricted to ALLOWED_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(chat.router)
app.include_router(payments.router)
app.include_router(circles.router) 


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "HABO MicroGigs API"}