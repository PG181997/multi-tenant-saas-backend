from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from dependencies import get_db
from sqlalchemy.orm import Session
import models
from routers.auth import get_current_user

router = APIRouter(prefix="/companies", tags=["Companies"])


class Create_company(BaseModel):
    name: str = Field(min_length=1)


def get_all_companies(db):

    return db.query(models.Company).all()


@router.post("/")
def create_company(
    company: Create_company,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    if current_user["role"] != "super_admin":
        raise HTTPException(
            status_code=304, detail="only super admin can creatge company"
        )

    existing_company = get_all_companies(db)

    for echCompany in existing_company:
        if echCompany.name.lower() == company.name.lower():
            raise HTTPException(status_code=400, detail="Company already exists")

    company = models.Company(name=company.name)
    db.add(company)
    db.commit()
    return {"id": company.id, "name": company.name}


@router.get("/get_all_company")
def get_all_company(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    if (current_user.get("role") or "").lower() != "super_admin":
        raise HTTPException(
            status_code=401, detail="Only super admin can get all the company."
        )
    return get_all_companies(db)


@router.delete("/{company_id}")
def delete_company(
    company_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    if current_user["role"] != "super_admin":
        raise HTTPException(
            status_code=304, detail="only super admin can creatge company"
        )

    company = db.query(models.Company).filter(models.Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    db.delete(company)
    db.commit()
    return {"status": "Deleted successfully"}
