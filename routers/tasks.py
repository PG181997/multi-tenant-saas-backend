from enum import Enum


from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import SessionLocal
from routers.auth import get_current_user
from sqlalchemy.orm import Session
from models import Projects, User, Tasks

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()


def get_project_object(db, project_id: int):
    return db.query(Projects).filter(Projects.id == project_id).first()


def get_user(db, user_id):
    return db.query(User).filter(User.id == user_id).first()


class Task_status(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class Create_new_task(BaseModel):

    task_name: str
    assigned_to: int
    task_status: Task_status = Task_status.todo
    project_id: int


@router.post("/")
async def create_new_task(
    task: Create_new_task,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    task_name = task.task_name
    assigned_to = task.assigned_to
    task_status = task.task_status
    task_project_id = task.project_id

    current_user_company = current_user.get("company_id")
    current_user_role = (current_user.get("role") or "").lower()
    current_user_id = current_user.get("user_id")

    if current_user_role != "admin":
        raise HTTPException(status_code=401, detail="Only admin can create new task.")

    project_obj = get_project_object(db, task_project_id)

    if not project_obj:
        raise HTTPException(status_code=404, detail="Project not found.")

    project_company = project_obj.company_id  # type: ignore
    assigned_to_data = get_user(db, assigned_to)

    if not assigned_to_data:
        raise HTTPException(status_code=404, detail="User not found.")
    assigned_to_company = assigned_to_data.company_id  # type: ignore

    if current_user_company != project_company:
        raise HTTPException(
            status_code=401, detail="admin can create new task in their company."
        )

    if current_user_company != assigned_to_company:
        raise HTTPException(
            status_code=401, detail="admin can assign new task in their company users."
        )
    new_task = Tasks(
        task_name=task_name,
        assigned_to=assigned_to,
        task_status=task_status,
        project_id=task_project_id,
        created_by_id=current_user_id,
    )

    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to create new task.")
    return {"response": "task created"}


@router.put("/")
async def update_task():
    return {"response": "project updated"}


@router.get("/")
async def get_all_task():
    return {"response": "sucess"}


@router.delete("/delete")
async def delete_task():
    return {"response": "project deleted"}
