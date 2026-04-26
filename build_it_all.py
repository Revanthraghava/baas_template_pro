import os
import sys
from pathlib import Path

# Set working directory to the script's location
os.chdir(Path(__file__).parent)
sys.path.append(os.getcwd())

def check_dependencies():
    deps = ["sqlalchemy", "fastapi", "pydantic", "dotenv", "psycopg2", "passlib", "jose", "multipart"]
    missing = []
    for dep in deps:
        try:
            if dep == "dotenv":
                import dotenv
            elif dep == "psycopg2":
                import psycopg2
            elif dep == "jose":
                import jose
            elif dep == "multipart":
                import multipart
            else:
                __import__(dep)
        except ImportError:
            missing.append(dep)
    
    if missing:
        print(f"--- Warning: Missing dependencies: {', '.join(missing)} ---")
        print("Please run: pip install sqlalchemy fastapi[all] python-dotenv psycopg2-binary passlib[bcrypt] python-jose[cryptography] python-multipart")
        print("------------------------------------------------------------\n")

def create_file(path, content):
    full_path = Path(path)
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content.strip())
    print(f"Created/Updated: {path}")

check_dependencies()

# --- File Contents ---

DATABASE_PY = """
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv(override=True)

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""

SECURITY_PY = """
import os
import bcrypt
from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    # Ensure password is not longer than 72 bytes for bcrypt
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        import hashlib
        password_bytes = hashlib.sha256(password_bytes).hexdigest().encode('utf-8')
    
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
"""

USER_MODEL_PY = """
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    projects = relationship("Project", back_populates="owner")
"""

PROJECT_MODEL_PY = """
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    link = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="projects")
"""

USER_SCHEMA_PY = """
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True
"""

PROJECT_SCHEMA_PY = """
from pydantic import BaseModel
from typing import Optional

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    link: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
"""

AUTH_API_PY = """
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.user import User, UserCreate
from app.core.security import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/signup", response_model=User)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = UserModel(email=user.email, name=user.name, password=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    
    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=db_user.email)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
"""

PROJECT_API_PY = """
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
"""

MAIN_PY = """
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
import traceback

app = FastAPI(title="BaaS Pro API")

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"message": str(exc), "detail": traceback.format_exc()},
        )

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(projects_router, prefix="/projects", tags=["Projects"])

@app.get("/")
def read_root():
    return {"message": "Welcome to BaaS Pro"}
"""

# --- Execution ---

files = {
    "app/__init__.py": "",
    "app/core/__init__.py": "",
    "app/models/__init__.py": "",
    "app/schemas/__init__.py": "",
    "app/api/__init__.py": "",
    "app/core/database.py": DATABASE_PY,
    "app/core/security.py": SECURITY_PY,
    "app/models/user.py": USER_MODEL_PY,
    "app/models/project.py": PROJECT_MODEL_PY,
    "app/schemas/user.py": USER_SCHEMA_PY,
    "app/schemas/project.py": PROJECT_SCHEMA_PY,
    "app/api/auth.py": AUTH_API_PY,
    "app/api/projects.py": PROJECT_API_PY,
    "app/main.py": MAIN_PY,
}

for path, content in files.items():
    create_file(path, content)

print("\\nAttempting database sync...")
try:
    import importlib
    # Force reload of core modules
    modules_to_reload = ['app.core.database', 'app.models.user', 'app.core.security']
    for mod in modules_to_reload:
        if mod in sys.modules:
            importlib.reload(sys.modules[mod])
        
    from app.core.database import Base, engine
    from app.models.user import User
    
    Base.metadata.create_all(bind=engine)
    print("Database sync successful!")
except Exception as e:
    print(f"Database sync failed: {e}")
    print("Check your .env and database connection.")
