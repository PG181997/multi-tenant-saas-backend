from email.policy import HTTP
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from database import SessionLocal
from models import User, Company
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from routers.auth import get_current_user


router = APIRouter(prefix="/users", tags=["Users"])
bcrypt_context = CryptContext(schemes=['bcrypt'])

def get_db():
	db = SessionLocal()
	try:
		yield db

	finally:
		db.close()


def get_all_users_from_db(db):

	return db.query(User).all()

class Update_user(BaseModel):
	first_name: str
	last_name: str
	email: str
	user_name: str
	role: str
	company_id: int

class Create_user(BaseModel):
	first_name: str
	last_name: str
	email: str
	user_name: str
	role: str
	company_id: int
	password: str

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


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_user(user: Create_user, db: Session = Depends(get_db), current_user:dict = Depends(get_current_user)):

	print("current_user:", current_user)
	print("user:", user)

	if user.role.lower() == "admin" and current_user.get("role").lower() != "super_admin":
		return HTTPException(status_code=400, detail="Admin can be created only by super admin.")
	
	if user.role.lower() == "user" and current_user.get("role").lower() not in ["super_admin", "admin"]:
		return HTTPException(status_code=400, detail="user can be created only by super-admin or admin.")

	company = db.query(Company).filter(Company.id == user.company_id).first()

	if not company:
		raise HTTPException(status_code=404, detail="Company not found")

	existing_user = db.query(User).filter(User.email == user.email).first()

	if existing_user:
		raise HTTPException(status_code=400, detail="User already exisits")
	
	print("CHECK HERE", current_user.get("company_id"), user.company_id)
	if current_user.get("role").lower() == "admin" and current_user.get("company_id") != user.company_id:
		raise HTTPException(status_code=400, detail="Admin can create user only in his/her company.")
	

	new_user = User(
		first_name=user.first_name,
		last_name=user.last_name,
		email=user.email,
		user_name=user.user_name,
		role=user.role,
		company_id=user.company_id,
		hashed_password = bcrypt_context.hash(user.password),
	)
	# return new_user
	db.add(new_user)
	db.commit()

	return {"status":"user created successfully"}
	
@router.delete("/{user_id}")
async def delete_user(user_id:int, db: Session = Depends(get_db)):
	exisiting_user = db.query(User).filter(User.id == user_id).first()
	if not exisiting_user:
		raise HTTPException(status_code=404, detail="User not found")
	print("exisiting_user: ", exisiting_user)
	db.query(User).filter(User.id == user_id).delete()
	db.commit()


