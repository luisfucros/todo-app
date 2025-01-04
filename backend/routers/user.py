from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from backend import models, schemas, oauth2, utils
from backend.database import get_db

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.Token)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(
        models.User.email == user.email).first()

    if user_query:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"User already exists")

    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = oauth2.create_access_token(data={"user_email": user.email})

    return {"access_token": access_token, "token_type": "bearer"}
    # return new_user

@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db), ):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")

    return user
