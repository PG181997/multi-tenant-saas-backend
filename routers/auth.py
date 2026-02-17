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


def authenticate_user(username: str, password:str, db):
    
    user = db.query(User).filter(User.user_name == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    
    encode = {'sub' : username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub') 
        user_id: int = payload.get('id')

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
        
        return {'username':username, 'user_id':user_id}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
    

class Create_user(BaseModel):
    first_name: str
    last_name: str
    email: str
    user_name: str
    role: str
    company_id: int
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
    
@router.post("/", status_code=status.HTTP_201_CREATED)
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
        hashed_password = bcrypt_context.hash(user.password),
    )
    # return new_user
    db.add(new_user)
    db.commit()
    
@router.post('/token', response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = create_access_token(user.user_name, user.id, timedelta(minutes=20))
    return {'access_token' : token, "token_type": 'bearer'}