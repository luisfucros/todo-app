from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import user, auth, task
from backend import models
from backend.database import engine
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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