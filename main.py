from fastapi import FastAPI
from routers import company, users
import models
from database import engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="Multi-tenant SaaS")


# include router
app.include_router(company.router)
app.include_router(users.router)
