from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    users = relationship("User", back_populates="company")


class Projects(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="projects")
    company_id = Column(Integer, ForeignKey("companies.id"))
    duration = Column(Integer, nullable=True)
    edited_at = Column(DateTime, nullable=True)
    tasks = relationship("Tasks", back_populates="project")


class Tasks(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))

    creator = relationship("User", back_populates="tasks")
    project = relationship("Projects", back_populates="tasks")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    user_name = Column(String, nullable=False)
    role = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    hashed_password = Column(String)

    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="users")

    projects = relationship("Projects", back_populates="creator")
    tasks = relationship("Tasks", back_populates="creator")
