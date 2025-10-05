from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import base64
from io import BytesIO
from PIL import Image
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
JWT_SECRET = "desideri-di-puglia-secret-key"
JWT_ALGORITHM = "HS256"

# Create the main app without a prefix
app = FastAPI(title="Desideri di Puglia Club API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# === MODELS ===

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    username: str
    email: EmailStr
    password_hash: str
    country: str
    avatar_url: Optional[str] = None
    current_points: int = 0
    total_points: int = 0
    level: str = "Explorer"  # Explorer, Local Friend, Ambassador, Legend
    badges: List[str] = Field(default_factory=list)
    position: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_reset: datetime = Field(default_factory=datetime.utcnow)
    is_admin: bool = False

class UserCreate(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str
    country: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ActionType(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    points: int
    max_per_day: int
    max_per_week: int
    max_per_month: int
    description: str

class UserAction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    action_type_id: str
    action_name: str
    points_earned: int
    description: str
    verification_status: str = "pending"  # pending, approved, rejected
    submission_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    verified_at: Optional[datetime] = None
    month_year: str  # "2025-01" format

class Mission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    points: int
    month_year: str
    is_active: bool = True
    requirements: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Prize(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    position: int  # 1, 2, 3
    title: str
    description: str
    image_url: Optional[str] = None
    month_year: str
    winner_id: Optional[str] = None
    claimed: bool = False
    claimed_at: Optional[datetime] = None

class Leaderboard(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    username: str
    avatar_url: Optional[str] = None
    country: str
    points: int
    position: int
    month_year: str
    level: str

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    message: str
    type: str  # info, success, warning, achievement
    read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

# === HELPER FUNCTIONS ===

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_current_month_year() -> str:
    return datetime.now().strftime("%Y-%m")

def get_user_level(total_points: int) -> str:
    if total_points >= 2000:
        return "Legend"
    elif total_points >= 1000:
        return "Ambassador"
    elif total_points >= 500:
        return "Local Friend"
    else:
        return "Explorer"

async def get_current_user(credentials: HTTPAuthorizationCredentials):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_data = await db.users.find_one({"id": user_id})
        if user_data is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return User(**user_data)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def process_avatar_image(image_data: bytes) -> str:
    """Process and resize avatar image to 400x400px"""
    try:
        img = Image.open(BytesIO(image_data))
        img = img.convert('RGB')
        img = img.resize((400, 400), Image.Resampling.LANCZOS)
        
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid image format")

# === AUTHENTICATION ENDPOINTS ===

@api_router.post("/auth/register")
async def register_user(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = await db.users.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user
    password_hash = get_password_hash(user_data.password)
    user = User(
        name=user_data.name,
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash,
        country=user_data.country,
        last_reset=datetime.utcnow()
    )
    
    await db.users.insert_one(user.dict())
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "email": user.email,
            "country": user.country,
            "current_points": user.current_points,
            "level": user.level,
            "avatar_url": user.avatar_url
        }
    }

@api_router.post("/auth/login")
async def login_user(user_data: UserLogin):
    user_doc = await db.users.find_one({"email": user_data.email})
    if not user_doc or not verify_password(user_data.password, user_doc["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user = User(**user_doc)
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "email": user.email,
            "country": user.country,
            "current_points": user.current_points,
            "total_points": user.total_points,
            "level": user.level,
            "avatar_url": user.avatar_url,
            "is_admin": user.is_admin
        }
    }

@api_router.post("/auth/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = security
):
    current_user = await get_current_user(credentials)
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Process image
    file_content = await file.read()
    avatar_url = process_avatar_image(file_content)
    
    # Update user
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"avatar_url": avatar_url}}
    )
    
    return {"avatar_url": avatar_url}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
