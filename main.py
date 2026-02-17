from fastapi import FastAPI
from routers import company, users, auth, projects, tasks
import models
from database import engine
from database import SessionLocal

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="Multi-tenant SaaS")


# include router
app.include_router(company.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(auth.router)
app.include_router(tasks.router)

def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()