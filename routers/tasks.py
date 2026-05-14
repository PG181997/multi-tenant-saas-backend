import datetime
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from dependencies import get_db
from routers.auth import get_current_user
from sqlalchemy.orm import Session
from models import Projects, User, Tasks
from typing import Optional

router = APIRouter(prefix="/tasks", tags=["Tasks"])




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


class Update_task(BaseModel):
    task_name: Optional[str] = None
    assigned_to: Optional[int] = None
    task_status: Optional[Task_status] = None


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
        raise HTTPException(status_code=403, detail="Only admin can create new task.")

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
            status_code=403, detail="admin can create new task in their company."
        )

    if current_user_company != assigned_to_company:
        raise HTTPException(
            status_code=403, detail="admin can assign new task in their company users."
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
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to create new task.")
    return {"response": "task created"}


@router.patch("/{task_id}")
async def update_task(
    task_id: int,
    task: Update_task,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    task_obj = db.query(Tasks).filter(Tasks.id == task_id).first()

    if not task_obj:
        raise HTTPException(status_code=404, detail="Data not found")
    task_project_obj = get_project_object(db, task_obj.project_id)
    if not task_project_obj:
        raise HTTPException(status_code=404, detail="Data not found")
    task_company_id = task_project_obj.company_id

    if task_company_id != current_user.get("company_id"):
        raise HTTPException(status_code=403, detail="Request not allowed.")

    if (task.assigned_to != None or task.task_name != None) and current_user.get(
        "role"
    ) != "admin":
        raise HTTPException(
            status_code=403, detail="Only admin can update the task assigned to."
        )

    if task.task_status != None and (
        task_obj.assigned_to != current_user.get("user_id")
        and task_obj.created_by_id != current_user.get("user_id")
    ):

        raise HTTPException(
            status_code=403,
            detail="Only task creator or assigned user can update the status",
        )

    if task.task_name != None:
        task_obj.task_name = task.task_name

    if task.assigned_to != None:
        task_obj.assigned_to = task.assigned_to

    if task.task_status != None:
        task_obj.task_status = task.task_status

    task_obj.edited_at = datetime.datetime.utcnow()

    try:
        db.commit()
        db.refresh(task_obj)
        return {"response": "task updated"}

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update task.")


@router.get("/")
async def get_all_task(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    current_user_company_id = current_user.get("company_id")
    all_projects = (
        db.query(Projects).filter(Projects.company_id == current_user_company_id).all()
    )
    project_id = [i.id for i in all_projects]
    all_tasks = db.query(Tasks).filter(Tasks.project_id.in_(project_id)).all()

    return [
        {
            "task_id": i.id,
            "task_name": i.task_name,
            "task_status": i.task_status,
            "task_project_id": i.project_id,
            "assigned_to": i.assigned_to,
            "created_at": i.created_at,
            "updated_at": i.edited_at,
        }
        for i in all_tasks
    ]


@router.delete("/{task_id}")
async def delete_task(
    task_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):

    current_user_role = (current_user.get("role") or "").lower()
    if current_user_role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete the task.")
    current_user_company_id = current_user.get("company_id")

    task_obj = db.query(Tasks).filter(Tasks.id == task_id).first()
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found.")

    project_obj = get_project_object(db, task_obj.project_id)

    if not project_obj:
        raise HTTPException(status_code=404, detail="Project not found.")
    if project_obj.company_id != current_user_company_id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        db.delete(task_obj)
        db.commit()
        return {"message": "Task deleted successfully"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete Task")
    # return {"response": "project deleted"}
