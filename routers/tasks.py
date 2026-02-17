from fastapi import APIRouter
from database import SessionLocal

router = APIRouter(prefix="/tasks", tags=["Tasks"])

def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()
        
@router.post("/")     
async def create_new_task():
    return {'response' : 'new project created'}

@router.put("/")     
async def update_task():
    return {'response' : 'project updated'}

@router.get("/")     
async def get_all_task():
    return {'response' : 'sucess'}

@router.delete("/delete")  
async def delete_task():
    return {'response' : 'project deleted'}