from fastapi import APIRouter
from database import SessionLocal
from routers.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/projects", tags=["Projects"])


def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()


class create_project(BaseModel):
    pass


@router.post("/")
async def create_new_project():
    return {"response": "new project created"}


@router.put("/")
async def update_project():
    return {"response": "project updated"}


@router.get("/")
async def get_all_project():
    return {"response": "sucess"}


@router.delete("/delete")
async def delete_project():
    return {"response": "project deleted"}
