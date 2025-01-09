from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import user, auth, task
from backend import models
from backend.database import engine
from backend.rate_limit import lifespan
from fastapi_limiter.depends import RateLimiter
import os


models.Base.metadata.create_all(bind=engine)

env = os.getenv("ENVIRONMENT", "test")
dependencies = []

if env != "test":
    dependencies.append(
        Depends(
            RateLimiter(times=2, seconds=5)
        )
    )

app = FastAPI(lifespan=lifespan, dependencies=dependencies)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(task.router)
app.include_router(auth.router)


@app.get("/")
def health_check():
    return {"status": "ok"}
