


from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from dependencies import get_db
from models import User, Company
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from routers.auth import get_current_user
import logging

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/users", tags=["Users"])
bcrypt_context = CryptContext(schemes=["bcrypt"])



def get_all_users_from_db(db):

    return db.query(User).all()


def get_all_user_from_company(db, company_id):

    return db.query(User).filter(User.company_id == company_id).all()


class Update_user(BaseModel):

    role: str | None = None
    password: str | None = None


class Create_user(BaseModel):
    first_name: str
    last_name: str
    email: str
    user_name: str
    role: str
    company_id: int
    password: str


@router.get("/get_all_users")
async def get_all_users(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):

    current_user_role = current_user.get("role") or ""
    current_user_company = current_user.get("company_id")

    if current_user_role == "super_admin":
        return get_all_users_from_db(db)

    elif current_user_role == "admin":
        return get_all_user_from_company(db, current_user_company)


@router.patch("/{user_id}")
async def update_user(
    user_id: int,
    user: Update_user,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user_role = (current_user.get("role") or "").lower()
    current_user_company_id = current_user.get("company_id")
    current_user_id = current_user.get("user_id")

    if current_user_role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=403, detail="Only super admin and admin can update."
        )

    user_to_update_data = (
        db.query(User).filter(User.id == user_id).first()
    )  # Data form DB

    if not user_to_update_data:
        raise HTTPException(status_code=404, detail="User not found.")

    # updating super admin.
    if current_user_role == "super_admin":
        if user_to_update_data.id == current_user_id:  # type: ignore

            if user.role is not None:
                raise HTTPException(
                    status_code=403,
                    detail="super admin cannot change their role.",
                )

    if current_user_role == "admin":

        # role updating
        if current_user_company_id != user_to_update_data.company_id:
            raise HTTPException(
                status_code=403, detail="admin can make changes only in their company."
            )

        if user_to_update_data.role == "super_admin":  # type: ignore

            raise HTTPException(
                status_code=403,
                detail="Admin can make changes in super admin.",
            )

        if user_to_update_data.role == "admin":  # type: ignore

            raise HTTPException(
                status_code=403,
                detail="Admin can make changes only for users role.",
            )

    if current_user_role == "user":

        if user.password != None:
            raise HTTPException(
                status_code=403, detail="user can only change their passowrd."
            )

    if user.role != None:
        user_to_update_data.role = user.role.lower()

    if user.password != None:
        user_to_update_data.hashed_password = bcrypt_context.hash(user.password)

    db.commit()
    db.refresh(user_to_update_data)

    return {"message": "user updated successfully"}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user: Create_user,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    logger.info(f"current_user: {current_user}")
    logger.info(f"user to create: {user}")

    # Logged in user
    current_user_role_lower = (current_user.get("role") or "").lower()
    current_user_company_id = current_user.get("company_id")

    # User that needs to be created
    user_role_lower = (user.role or "").lower()

    if user_role_lower == "super_admin":
        raise HTTPException(status_code=403, detail="Super admin cannot be created.")

    # Admin creation
    if user_role_lower == "admin":

        if current_user_role_lower not in ["admin", "super_admin"]:
            raise HTTPException(
                status_code=403,
                detail="Only admin and super admin can create an admin.",
            )

        if current_user_role_lower == "admin":
            if user.company_id != current_user_company_id:
                raise HTTPException(
                    status_code=403,
                    detail="Admin and super admin can create another admin only in their  company.",
                )

    if user_role_lower == "user":

        if current_user_role_lower not in ["admin", "super_admin"]:
            raise HTTPException(
                status_code=403, detail="Only admin and super admin can create a user."
            )

        if (
            current_user_role_lower == "admin"
            and current_user_company_id != user.company_id
        ):
            raise HTTPException(
                status_code=403, detail="Admin can create user only in their  company."
            )

    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        logger.warning("User already exists")
        raise HTTPException(status_code=409, detail="User already exists")

    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        user_name=user.user_name,
        role=user_role_lower,
        company_id=user.company_id,
        hashed_password=bcrypt_context.hash(user.password),
    )

    # return new_user
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception:
        db.rollback()

        raise HTTPException(status_code=500, detail="User creation failed")

    return {"id": new_user.id, "status": "user created successfully"}


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    current_user_role = (current_user.get("role") or "").lower()
    current_user_company_id = current_user.get("company_id")
    current_user_user_id = current_user.get("user_id")

    if current_user_role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=403, detail="only admin and super admin can delete user."
        )

    user_id_data = db.query(User).filter(User.id == user_id).first()
    if not user_id_data:
        raise HTTPException(status_code=404, detail="User not found")

    to_del_user_role = (user_id_data.role or "").lower()
    to_del_user_company_id = user_id_data.company_id

    logger.info(f"to_del_user_role: {to_del_user_role}")
    logger.info(f"to_del_user_company_id: {to_del_user_company_id}")

    if current_user_user_id == user_id:
        raise HTTPException(
            status_code=403, detail="You are not allowed to self deletion."
        )

    if to_del_user_role == "super_admin":
        raise HTTPException(status_code=403, detail="super admin cannot be deleted.")

    # Deleting admin and only super admin can delete it
    if to_del_user_role == "admin":
        if current_user_role != "super_admin":
            raise HTTPException(
                status_code=403, detail="Admin can be deleted only by super admin."
            )

    # Deleting user
    if to_del_user_role == "user":
        if current_user_role == "admin":
            if current_user_company_id != to_del_user_company_id:
                raise HTTPException(
                    status_code=403,
                    detail="Admin can delete user only in their company.",
                )

        elif current_user_role != "super_admin":
            raise HTTPException(
                status_code=403,
                detail="User can be deleted only by superadmin or admin",
            )

    # db.query(User).filter(User.id == user_id).delete()
    db.delete(user_id_data)
    db.commit()
    return {"message": "User deleted successfully"}
