from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
from backend import models, schemas, oauth2
from backend.database import get_db


router = APIRouter(
    prefix="/todos",
    tags=['Tasks']
)

@router.get("", response_model=List[schemas.TaskOut])
def get_all_tasks(
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user)
):
    tasks = db.query(models.Task).all()
    return tasks

@router.post("", response_model=schemas.TaskOut)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user)
):
    db_task = models.Task(owner_id=current_user.id, **task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
