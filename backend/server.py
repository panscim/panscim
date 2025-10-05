from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Depends
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
    except Exception:
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
    credentials: HTTPAuthorizationCredentials = Depends(security)
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

# === USER ENDPOINTS ===

@api_router.get("/user/profile")
async def get_user_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    current_user = await get_current_user(credentials)
    
    # Get user's position in current leaderboard
    leaderboard = await db.leaderboards.find(
        {"month_year": get_current_month_year()}
    ).sort("points", -1).to_list(1000)
    
    position = 0
    for i, entry in enumerate(leaderboard, 1):
        if entry["user_id"] == current_user.id:
            position = i
            break
    
    # Get user notifications
    notifications = await db.notifications.find(
        {"user_id": current_user.id, "read": False}
    ).sort("created_at", -1).limit(5).to_list(5)
    
    return {
        "id": current_user.id,
        "name": current_user.name,
        "username": current_user.username,
        "email": current_user.email,
        "country": current_user.country,
        "current_points": current_user.current_points,
        "total_points": current_user.total_points,
        "level": current_user.level,
        "avatar_url": current_user.avatar_url,
        "position": position,
        "badges": current_user.badges,
        "unread_notifications": len(notifications),
        "is_admin": current_user.is_admin
    }

@api_router.put("/user/profile")
async def update_user_profile(
    name: Optional[str] = None,
    username: Optional[str] = None,
    country: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = await get_current_user(credentials)
    update_data = {}
    
    if name:
        update_data["name"] = name
    if username:
        # Check if username is taken
        existing = await db.users.find_one({"username": username, "id": {"$ne": current_user.id}})
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        update_data["username"] = username
    if country:
        update_data["country"] = country
    
    if update_data:
        await db.users.update_one({"id": current_user.id}, {"$set": update_data})
    
    return {"message": "Profile updated successfully"}

# === ACTIONS & POINTS ENDPOINTS ===

@api_router.get("/actions/types")
async def get_action_types():
    """Get available action types with points and limits"""
    action_types = [
        {
            "id": "like_post",
            "name": "Mi piace a post IG",
            "points": 5,
            "max_per_day": 3,
            "max_per_week": 0,
            "max_per_month": 0,
            "description": "Metti mi piace a un post di @desideridipuglia"
        },
        {
            "id": "comment_post",
            "name": "Commenta post",
            "points": 10,
            "max_per_day": 2,
            "max_per_week": 0,
            "max_per_month": 0,
            "description": "Commenta in modo autentico un post"
        },
        {
            "id": "share_story",
            "name": "Condividi storia",
            "points": 25,
            "max_per_day": 1,
            "max_per_week": 0,
            "max_per_month": 0,
            "description": "Condividi storia taggando @desideridipuglia"
        },
        {
            "id": "post_hashtag",
            "name": "Post con hashtag",
            "points": 30,
            "max_per_day": 0,
            "max_per_week": 1,
            "max_per_month": 0,
            "description": "Pubblica post con #DesideridiPugliaClub"
        },
        {
            "id": "google_review",
            "name": "Recensione Google/Booking",
            "points": 50,
            "max_per_day": 0,
            "max_per_week": 0,
            "max_per_month": 1,
            "description": "Lascia recensione su Google o Booking"
        },
        {
            "id": "visit_partner",
            "name": "Visita partner (QR)",
            "points": 40,
            "max_per_day": 1,
            "max_per_week": 0,
            "max_per_month": 0,
            "description": "Scansiona QR code di un partner"
        },
        {
            "id": "tag_bnb_photo",
            "name": "Tagga foto B&B",
            "points": 20,
            "max_per_day": 1,
            "max_per_week": 0,
            "max_per_month": 0,
            "description": "Tagga foto scattata al B&B"
        },
        {
            "id": "invite_friend",
            "name": "Invita amico",
            "points": 60,
            "max_per_day": 0,
            "max_per_week": 0,
            "max_per_month": 0,
            "description": "Invita un amico che si iscrive"
        }
    ]
    return action_types

@api_router.post("/actions/submit")
async def submit_action(
    action_type_id: str = Form(...),
    description: str = Form(...),
    submission_url: Optional[str] = Form(None),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = await get_current_user(credentials)
    month_year = get_current_month_year()
    
    # Get action type info
    action_types = await get_action_types()
    action_type = next((a for a in action_types if a["id"] == action_type_id), None)
    if not action_type:
        raise HTTPException(status_code=404, detail="Action type not found")
    
    # Check daily/weekly/monthly limits
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # Count existing actions for this period
    if action_type["max_per_day"] > 0:
        daily_count = await db.user_actions.count_documents({
            "user_id": current_user.id,
            "action_type_id": action_type_id,
            "created_at": {"$gte": today}
        })
        if daily_count >= action_type["max_per_day"]:
            raise HTTPException(status_code=400, detail=f"Daily limit reached for this action ({action_type['max_per_day']}/day)")
    
    if action_type["max_per_week"] > 0:
        weekly_count = await db.user_actions.count_documents({
            "user_id": current_user.id,
            "action_type_id": action_type_id,
            "created_at": {"$gte": week_start}
        })
        if weekly_count >= action_type["max_per_week"]:
            raise HTTPException(status_code=400, detail=f"Weekly limit reached for this action ({action_type['max_per_week']}/week)")
    
    if action_type["max_per_month"] > 0:
        monthly_count = await db.user_actions.count_documents({
            "user_id": current_user.id,
            "action_type_id": action_type_id,
            "created_at": {"$gte": month_start}
        })
        if monthly_count >= action_type["max_per_month"]:
            raise HTTPException(status_code=400, detail=f"Monthly limit reached for this action ({action_type['max_per_month']}/month)")
    
    # Create action record
    action = UserAction(
        user_id=current_user.id,
        action_type_id=action_type_id,
        action_name=action_type["name"],
        points_earned=action_type["points"],
        description=description,
        submission_url=submission_url,
        month_year=month_year
    )
    
    await db.user_actions.insert_one(action.dict())
    
    # Create notification
    notification = Notification(
        user_id=current_user.id,
        title="Azione inviata! 🌿",
        message=f"La tua azione '{action_type['name']}' è in verifica. Riceverai {action_type['points']} punti una volta approvata!",
        type="info"
    )
    await db.notifications.insert_one(notification.dict())
    
    return {"message": "Action submitted for verification", "action_id": action.id}

@api_router.get("/actions/history")
async def get_action_history(
    limit: int = 20,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = await get_current_user(credentials)
    
    actions = await db.user_actions.find(
        {"user_id": current_user.id}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return actions

# === LEADERBOARD ENDPOINTS ===

@api_router.get("/leaderboard")
async def get_leaderboard(month_year: Optional[str] = None):
    if not month_year:
        month_year = get_current_month_year()
    
    # Get top users for the month
    pipeline = [
        {
            "$match": {
                "month_year": month_year,
                "verification_status": "approved"
            }
        },
        {
            "$group": {
                "_id": "$user_id",
                "total_points": {"$sum": "$points_earned"}
            }
        },
        {
            "$sort": {"total_points": -1}
        },
        {
            "$limit": 50
        }
    ]
    
    leaderboard_data = await db.user_actions.aggregate(pipeline).to_list(50)
    
    # Get user details and create leaderboard
    leaderboard = []
    for i, entry in enumerate(leaderboard_data, 1):
        user_doc = await db.users.find_one({"id": entry["_id"]})
        if user_doc:
            user = User(**user_doc)
            leaderboard.append({
                "position": i,
                "user_id": user.id,
                "username": user.username,
                "name": user.name,
                "avatar_url": user.avatar_url,
                "country": user.country,
                "points": entry["total_points"],
                "level": get_user_level(user.total_points)
            })
    
    return {
        "month_year": month_year,
        "leaderboard": leaderboard,
        "total_participants": len(leaderboard)
    }

# === MISSIONS ENDPOINTS ===

@api_router.get("/missions")
async def get_missions(month_year: Optional[str] = None):
    if not month_year:
        month_year = get_current_month_year()
    
    missions = await db.missions.find(
        {"month_year": month_year, "is_active": True}
    ).to_list(100)
    
    return missions

# === PRIZES ENDPOINTS ===

@api_router.get("/prizes")
async def get_prizes(month_year: Optional[str] = None):
    if not month_year:
        month_year = get_current_month_year()
    
    # Default prizes for each month
    default_prizes = [
        {
            "position": 1,
            "title": "🥇 Notte per 2 persone",
            "description": "Una notte gratuita nel nostro B&B per 2 persone con colazione inclusa",
            "month_year": month_year
        },
        {
            "position": 2,
            "title": "🥈 Cena o degustazione per 2",
            "description": "Esperienza culinaria presso un partner selezionato per 2 persone",
            "month_year": month_year
        },
        {
            "position": 3,
            "title": "🥉 Drink Experience per 2",
            "description": "Aperitivo o drink speciale presso un partner per 2 persone",
            "month_year": month_year
        }
    ]
    
    # Try to get custom prizes first
    prizes = await db.prizes.find({"month_year": month_year}).to_list(10)
    
    # If no custom prizes, return defaults
    if not prizes:
        prizes = default_prizes
    
    return prizes

# === NOTIFICATIONS ENDPOINTS ===

@api_router.get("/notifications")
async def get_notifications(
    limit: int = 20,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = await get_current_user(credentials)
    
    notifications = await db.notifications.find(
        {"user_id": current_user.id}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return notifications

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = await get_current_user(credentials)
    
    await db.notifications.update_one(
        {"id": notification_id, "user_id": current_user.id},
        {"$set": {"read": True}}
    )
    
    return {"message": "Notification marked as read"}

# === ADMIN ENDPOINTS ===

@api_router.get("/admin/actions/pending")
async def get_pending_actions(credentials: HTTPAuthorizationCredentials = Depends(security)):
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    actions = await db.user_actions.find(
        {"verification_status": "pending"}
    ).sort("created_at", -1).to_list(100)
    
    # Convert to proper format and get user details
    result = []
    for action in actions:
        # Convert ObjectId to string and clean up the action
        clean_action = {
            "id": action["id"],
            "user_id": action["user_id"],
            "action_type_id": action["action_type_id"],
            "action_name": action["action_name"],
            "points_earned": action["points_earned"],
            "description": action["description"],
            "verification_status": action["verification_status"],
            "submission_url": action.get("submission_url"),
            "created_at": action["created_at"].isoformat() if "created_at" in action else None,
            "month_year": action["month_year"]
        }
        
        # Get user details
        user_doc = await db.users.find_one({"id": action["user_id"]})
        if user_doc:
            clean_action["user_name"] = user_doc["name"]
            clean_action["username"] = user_doc["username"]
        
        result.append(clean_action)
    
    return result

@api_router.put("/admin/actions/{action_id}/verify")
async def verify_action(
    action_id: str,
    status: str,  # approved or rejected
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Status must be 'approved' or 'rejected'")
    
    action_doc = await db.user_actions.find_one({"id": action_id})
    if not action_doc:
        raise HTTPException(status_code=404, detail="Action not found")
    
    # Update action status
    await db.user_actions.update_one(
        {"id": action_id},
        {
            "$set": {
                "verification_status": status,
                "verified_at": datetime.utcnow()
            }
        }
    )
    
    # If approved, add points to user
    if status == "approved":
        await db.users.update_one(
            {"id": action_doc["user_id"]},
            {
                "$inc": {
                    "current_points": action_doc["points_earned"],
                    "total_points": action_doc["points_earned"]
                }
            }
        )
        
        # Update user level
        user_doc = await db.users.find_one({"id": action_doc["user_id"]})
        if user_doc:
            new_level = get_user_level(user_doc["total_points"] + action_doc["points_earned"])
            await db.users.update_one(
                {"id": action_doc["user_id"]},
                {"$set": {"level": new_level}}
            )
        
        # Create success notification
        notification = Notification(
            user_id=action_doc["user_id"],
            title="🎉 Punti guadagnati!",
            message=f"Hai guadagnato {action_doc['points_earned']} punti per '{action_doc['action_name']}'. Continua così!",
            type="success"
        )
    else:
        # Create rejection notification
        notification = Notification(
            user_id=action_doc["user_id"],
            title="❌ Azione rifiutata",
            message=f"La tua azione '{action_doc['action_name']}' non è stata approvata. Riprova seguendo le linee guida.",
            type="warning"
        )
    
    await db.notifications.insert_one(notification.dict())
    
    return {"message": f"Action {status} successfully"}

# === SYSTEM ENDPOINTS ===

@api_router.get("/")
async def root():
    return {"message": "Desideri di Puglia Club API - Live Puglia Challenge 🌿"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

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
