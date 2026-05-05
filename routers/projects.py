from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from routers.auth import get_current_user
from pydantic import BaseModel
import logging
from models import Projects
from typing import Optional

router = APIRouter(prefix="/projects", tags=["Projects"])


def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()


def get_all_company_projects(db, companid: int):

    return db.query(Projects).filter(company_id=companid)


class create_project(BaseModel):
    project_name: str
    duration: Optional[int] = None


@router.post("/")
async def create_new_project(
    project: create_project,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user_role = (current_user.get("role") or "").lower()
    current_user_id = current_user.get("id")
    current_user_company_id = current_user.get("company_id")

    logging.info(f"current_user {current_user}")
    logging.info(f"current project {project}")
    logging.info(f"current current_user_id {current_user_id}")
    if current_user_role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create a project")

    new_project = Projects(
        project_name=project.project_name,
        duration=project.duration,
        company_id=current_user_company_id,
        created_by_id=current_user_id,
    )

    try:
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        return {"response": "sucess"}
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create new project")


@router.put("/")
async def update_project():
    return {"response": "project updated"}


# @router.get("/")
# async def get_all_project(
#     db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
# ):
#     current_user_company_id = current_user.get("company_id")
#     return get_all_company_projects(db, current_user_company_id)


@router.delete("/delete")
async def delete_project():
    return {"response": "project deleted"}
