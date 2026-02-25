from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import auth, tasks, users, chat, payments

settings = get_settings()

app = FastAPI(
    title="HABO MicroGigs API",
    description="Help a Brother Out — hyper-local micro-gig marketplace",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(chat.router)
app.include_router(payments.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "HABO MicroGigs API"}