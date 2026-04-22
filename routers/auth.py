from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from passlib.context import CryptContext
from database import SessionLocal
from models import Company, User
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
from jose import jwt, JWTError

router = APIRouter(prefix="/auth", tags=["Authentication"])

SECRET_KEY = "G7kP2zX9mQ4vB8rC1Yt6Lw0eS3H5JdUa"
ALGORITHM = "HS256"

def get_db():
	db = SessionLocal()
	try:
		yield db

	finally:
		db.close()
		
bcrypt_context = CryptContext(schemes=['bcrypt'])
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def authenticate_user(email: str, password:str, db):
	
	user = db.query(User).filter(User.email == email).first()
	if not user:
		return False
	if not bcrypt_context.verify(password, user.hashed_password):
		return False
	return user

def create_access_token(username: str, user_id: int, role:str, company_id:str, expires_delta: timedelta):
	
	encode = {'sub' : username, 'id': user_id, 'role':role, 'company_id':company_id}
	expires = datetime.now(timezone.utc) + expires_delta
	encode.update({'exp':expires})
	return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		username: str = payload.get('sub') 
		user_id: int = payload.get('id')
		role:str = payload.get('role')
		company_id:int = payload.get('company_id')

		if username is None or user_id is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
		
		return {'username':username, 'user_id':user_id, 'role':role, 'company_id':company_id}

	except JWTError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
	


	
class Token(BaseModel):
	access_token: str
	token_type: str
	
	

	
@router.post('/token', response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
	user = authenticate_user(form_data.username, form_data.password, db)
	
	if not user:
		raise HTTPException(status_code=401, detail="Invalid username or password")
	
	token = create_access_token(user.email, user.id,user.role, user.company_id,timedelta(minutes=20))
	return {'access_token' : token, "token_type": 'bearer'}