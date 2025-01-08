from fastapi import Query, Response, status, HTTPException, Depends, APIRouter
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
def get_tasks(
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
    limit: int = Query(10, le=100),
    skip: int = Query(0, ge=0),
):
    tasks = db.query(models.Task).filter(models.Task.owner_id == current_user.id).limit(limit).offset(skip).all()
    return tasks

@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.TaskOut)
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

@router.put("/{id}", response_model=schemas.TaskOut)
def update_task(
    id: int,
    updated_task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user)
):
    task_query = db.query(models.Task).filter(models.Task.id == id)

    task = task_query.first()

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"task with id: {id} does not exist")

    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    task_query.update(updated_task.model_dump(), synchronize_session=False)

    db.commit()

    return task_query.first()

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user)
):

    task_query = db.query(models.Task).filter(models.Task.id == id)

    task = task_query.first()

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"task with id: {id} does not exist")

    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    task_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
