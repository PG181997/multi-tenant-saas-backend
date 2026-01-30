from email.policy import HTTP
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import SessionLocal
from models import User, Company
from sqlalchemy.orm import Session


router = APIRouter(prefix="/users", tags=["Users"])


def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()


def get_all_users_from_db(db):

    return db.query(User).all()


class Create_user(BaseModel):
    first_name: str
    last_name: str
    email: str
    user_name: str
    role: str
    company_id: int


class Update_user(BaseModel):
    first_name: str
    last_name: str
    email: str
    user_name: str
    role: str
    company_id: int


@router.get("/get_all_users")
async def get_all_users(db: Session = Depends(get_db)):
    return get_all_users_from_db(db)


@router.put("/{user_id}")
async def update_user(user_id: int, user: Update_user, db: Session = Depends(get_db)):

    exisiting_user = db.query(User).filter(User.id == user_id).first()
    if not exisiting_user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_company = db.query(Company).filter(Company.id == user.company_id).first()
    if not existing_company:
        raise HTTPException(status_code=404, detail="Company not found")

    email_exists = (
        db.query(User)
        .filter(User.email == user.email)
        .filter(User.id != user_id)
        .first()
    )
    if email_exists:
        raise HTTPException(status_code=400, detail="Email already exists")

    exisiting_user.first_name = user.first_name
    exisiting_user.last_name = user.last_name
    exisiting_user.email = user.email
    exisiting_user.user_name = user.user_name
    exisiting_user.role = user.role
    exisiting_user.company_id = user.company_id

    db.commit()


@router.post("/")
async def create_new_user(user: Create_user, db: Session = Depends(get_db)):

    company = db.query(Company).filter(Company.id == user.company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exisits")

    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        user_name=user.user_name,
        role=user.role,
        company_id=user.company_id,
    )

    db.add(new_user)
    db.commit()
