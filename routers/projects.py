import datetime

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

    return [
        {
            "project_id": i.id,
            "project_name": i.project_name,
            "created_at": i.created_at,
            "created_by": i.created_by_id,
            "duration": i.duration,
            "edited_at": i.edited_at,
        }
        for i in db.query(Projects).filter(Projects.company_id == companid).all()
    ]


class Create_project(BaseModel):
    project_name: str
    duration: Optional[int] = None


class Update_project(BaseModel):
    project_name: Optional[str] = None
    duration: Optional[int] = None


@router.post("/")
async def create_new_project(
    project: Create_project,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user_role = (current_user.get("role") or "").lower()
    current_user_id = current_user.get("user_id")
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


@router.patch("/{project_id}")
async def update_project(
    project_id: int,
    project: Update_project,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    project_obj = db.query(Projects).filter(Projects.id == project_id).first()
    if not project_obj:
        raise HTTPException(status_code=404, detail="Project not found")

    project_company_id = project_obj.company_id

    current_user_role = (current_user.get("role") or "").lower()
    current_user_company_id = current_user.get("company_id")

    if project_company_id != current_user_company_id or current_user_role != "admin":
        raise HTTPException(status_code=401, detail="wrong role or company")

    if project.project_name != None:
        project_obj.project_name = project.project_name  # type: ignore

    if project.duration != None:
        project_obj.duration = project.duration  # type: ignore

    project_obj.edited_at = datetime.datetime.utcnow()  # type: ignore

    try:
        db.commit()
        db.refresh(project_obj)
        return {"response": "project updated"}

    except:
        db.rollback()

        raise HTTPException(status_code=500, detail="Project update failed")


@router.get("/")
async def get_all_project(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    current_user_company_id = current_user.get("company_id")
    all_project = get_all_company_projects(
        db, current_user_company_id  # type: ignore
    )  # pyright: ignore[reportArgumentType]
    logging.info(f"all_company_obj: {all_project}")
    return all_project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    project_obj = db.query(Projects).filter(Projects.id == project_id).first()

    if not project_obj:
        raise HTTPException(status_code=404, detail="Project not found")
    project_company_id = project_obj.company_id

    current_user_role = (current_user.get("role") or "").lower()
    current_user_company_id = current_user.get("company_id")

    if project_company_id != current_user_company_id or current_user_role != "admin":
        raise HTTPException(status_code=401, detail="wrong role or company")
    logging.info(f"project_data: {project_obj}")

    try:
        db.delete(project_obj)
        db.commit()
        return {"message": "Project deleted successfully"}
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete project")
    # return {"response": "project deleted"}
