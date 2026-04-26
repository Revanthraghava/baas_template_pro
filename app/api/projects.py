from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.project import Project as ProjectModel
from app.models.user import User as UserModel
from app.schemas.project import Project, ProjectCreate
from app.api.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=Project)
def create_project(
    project: ProjectCreate, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    # Single ProjectCreate object expected, returning single Project
    db_project = ProjectModel(**project.model_dump(), owner_id=current_user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/", response_model=List[Project])
def read_projects(
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    projects = db.query(ProjectModel).filter(ProjectModel.owner_id == current_user.id).all()
    return projects