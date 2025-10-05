from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Depends, Query
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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

# === EMAIL FUNCTIONS ===

def generate_club_card_code() -> str:
    """Generate unique DP-XXXX club card code"""
    import random
    code_number = random.randint(1000, 9999)
    return f"DP-{code_number}"

def generate_club_card_qr_url(user_id: str) -> str:
    """Generate QR code URL for club card"""
    return f"https://desideridipuglia.com/club/user/{user_id}"

async def initialize_club_card(user_id: str):
    """Initialize club card data for new user"""
    # Check if user already has club card data
    user_doc = await db.users.find_one({"id": user_id})
    if not user_doc:
        return
    
    update_data = {}
    
    # Generate club card code if not exists
    if not user_doc.get("club_card_code"):
        # Generate unique code
        while True:
            code = generate_club_card_code()
            existing = await db.users.find_one({"club_card_code": code})
            if not existing:
                update_data["club_card_code"] = code
                break
    
    # Generate QR URL if not exists
    if not user_doc.get("club_card_qr_url"):
        update_data["club_card_qr_url"] = generate_club_card_qr_url(user_id)
    
    # Set join date if not exists (use created_at as fallback)
    if not user_doc.get("join_date"):
        join_date = user_doc.get("created_at", datetime.utcnow())
        update_data["join_date"] = join_date
    
    # Update user if needed
    if update_data:
        await db.users.update_one({"id": user_id}, {"$set": update_data})

async def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send email using Gmail SMTP"""
    try:
        # Get SMTP settings from environment
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', 465))
        smtp_email = os.environ.get('SMTP_EMAIL', 'desideridipuglia@gmail.com')
        smtp_password = os.environ.get('SMTP_PASSWORD', '')
        
        if not smtp_password:
            logging.warning(f"SMTP password not configured for {smtp_email}")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'html'))
        
        # Gmail SMTP server setup
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(smtp_email, smtp_password)
        
        # Send email
        server.sendmail(smtp_email, to_email, msg.as_string())
        server.quit()
        
        logging.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

# === MODELS ===

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    username: str
    email: EmailStr
    password_hash: str
    country: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    current_points: int = 0
    total_points: int = 0
    level: str = "Explorer"  # Explorer, Local Friend, Ambassador, Legend
    badges: List[str] = Field(default_factory=list)
    position: int = 0
    preferred_lang: str = "IT"  # IT, EN
    club_card_code: Optional[str] = None
    club_card_qr_url: Optional[str] = None
    otp_method: str = "email"  # email, sms
    email_verified: bool = False
    phone_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_reset: datetime = Field(default_factory=datetime.utcnow)
    is_admin: bool = False
    # Digital Club Card fields
    join_date: Optional[datetime] = None
    preferred_language: str = "it"  # it or en

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
    frequency: str = "one-time"  # daily, weekly, one-time
    month_year: str
    is_active: bool = True
    requirements: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    daily_limit: int = 0  # 0 means no limit
    weekly_limit: int = 0  # 0 means no limit
    # Verification settings
    requires_description: bool = True
    requires_photo: bool = False
    photo_source: str = "both"  # none, gallery, camera, both
    requires_link: bool = False
    requires_approval: bool = True

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
    delivered: bool = False
    delivered_at: Optional[datetime] = None

class EmailRequest(BaseModel):
    recipients: List[str]
    subject: str
    body: str

class MissionRequest(BaseModel):
    title: str
    description: str
    points: int
    frequency: str = "one-time"  # daily, weekly, one-time
    daily_limit: int = 0
    weekly_limit: int = 0
    is_active: bool = True
    # Verification requirements
    requires_description: bool = True
    requires_photo: bool = False
    photo_source: str = "both"  # none, gallery, camera, both
    requires_link: bool = False
    requires_approval: bool = True

class MissionUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    points: Optional[int] = None
    frequency: Optional[str] = None
    daily_limit: Optional[int] = None
    weekly_limit: Optional[int] = None
    is_active: Optional[bool] = None
    requires_description: Optional[bool] = None
    requires_photo: Optional[bool] = None
    photo_source: Optional[str] = None
    requires_link: Optional[bool] = None
    requires_approval: Optional[bool] = None

class PrizeUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class Translation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str  # Translation key (e.g., "mission_completed")
    italian: str
    english: str
    category: str = "general"  # general, admin, missions, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EmailLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = "desideridipuglia@gmail.com"
    recipients: List[str]
    subject: str
    body: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "sent"  # sent, partial, failed
    admin_id: str

class MissionSubmission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    mission_id: str
    mission_title: str
    description: str
    photo_url: Optional[str] = None
    submission_url: Optional[str] = None
    verification_status: str = "pending"  # pending, approved, rejected
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    points_earned: int
    month_year: str

class UserMission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    mission_id: str
    mission_title: str
    points_earned: int
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    month_year: str
    submission_id: Optional[str] = None  # Link to submission if verification was required

class WeeklyQuiz(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    questions: List[Dict] = []  # [{"question": "...", "options": ["a", "b", "c"], "correct": 0}]
    quiz_start_date: datetime = Field(default_factory=datetime.utcnow)
    quiz_end_date: Optional[datetime] = None
    is_active: bool = True
    created_by: str  # admin_id

class QuizCompletion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    quiz_id: str
    answers: List[int]  # [0, 1, 2] indices of selected answers
    score: int  # number of correct answers
    points_earned: int
    completed_at: datetime = Field(default_factory=datetime.utcnow)

class WinnersArchive(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    username: str
    user_name: str
    position: int  # 1, 2, 3
    prize_title: str
    prize_description: str
    month_year: str
    points: int
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    delivered: bool = False
    delivered_at: Optional[datetime] = None

class Badge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    icon: str  # emoji or icon name
    condition_type: str  # first_mission, first_review, months_active, top3_month
    condition_value: Optional[int] = None  # for numeric conditions
    created_by: str  # admin_id
    is_active: bool = True

class UserBadge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    badge_id: str
    badge_name: str
    badge_icon: str
    earned_at: datetime = Field(default_factory=datetime.utcnow)

class SecurityEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    event_type: str  # login_attempt, suspicious_activity, rate_limit
    ip_address: str
    user_agent: str
    details: Dict = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

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

class SystemConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str  # month_status, welcome_bonus, quiz_points
    value: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = None

class MultiLanguageText(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str  # welcome_message, mission_complete, etc.
    italian: str
    english: str
    updated_by: str  # admin_id
    updated_at: datetime = Field(default_factory=datetime.utcnow)

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

def generate_club_card_code() -> str:
    """Generate unique club card code DP-XXXX"""
    import random
    import string
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"DP-{suffix}"

def generate_qr_code(data: str) -> str:
    """Generate QR code for club card"""
    import qrcode
    import base64
    from io import BytesIO
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

async def check_and_award_badges(user_id: str, action_type: str):
    """Check and award badges based on user actions"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        return
    
    # Check for badge conditions
    badges_to_award = []
    
    # First mission badge
    if action_type == "first_mission":
        existing_badge = await db.user_badges.find_one({
            "user_id": user_id, 
            "badge_name": "Prima Missione"
        })
        if not existing_badge:
            badges_to_award.append({
                "name": "Prima Missione",
                "icon": "🎯",
                "description": "Hai completato la tua prima missione!"
            })
    
    # Award badges
    for badge_info in badges_to_award:
        user_badge = UserBadge(
            user_id=user_id,
            badge_id=str(uuid.uuid4()),
            badge_name=badge_info["name"],
            badge_icon=badge_info["icon"]
        )
        await db.user_badges.insert_one(user_badge.dict())
        
        # Send notification
        notification = Notification(
            user_id=user_id,
            title=f"🏆 Nuovo Badge Sbloccato!",
            message=f"Hai guadagnato il badge '{badge_info['name']}' {badge_info['icon']}",
            type="achievement"
        )
        await db.notifications.insert_one(notification.dict())

async def get_system_config(key: str, default_value: str = "") -> str:
    """Get system configuration value"""
    config = await db.system_config.find_one({"key": key})
    return config["value"] if config else default_value

async def set_system_config(key: str, value: str, admin_id: str = None):
    """Set system configuration value"""
    await db.system_config.update_one(
        {"key": key},
        {"$set": {
            "value": value,
            "updated_at": datetime.utcnow(),
            "updated_by": admin_id
        }},
        upsert=True
    )

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
        img = img.resize((400, 400), Image.LANCZOS)
        
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
    
    # Initialize club card for new user
    await initialize_club_card(user.id)
    
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
    
    # Clean actions to avoid ObjectId issues
    clean_actions = []
    for action in actions:
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
            "verified_at": action["verified_at"].isoformat() if action.get("verified_at") else None,
            "month_year": action["month_year"]
        }
        clean_actions.append(clean_action)
    
    return clean_actions

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
async def get_missions(
    month_year: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = await get_current_user(credentials)
    
    if not month_year:
        month_year = get_current_month_year()
    
    missions = await db.missions.find(
        {"month_year": month_year, "is_active": True}
    ).to_list(100)
    
    # Get user's mission completions for this month
    user_completions = await db.user_missions.find({
        "user_id": current_user.id,
        "month_year": month_year
    }).to_list(None)
    
    completed_mission_ids = {completion["mission_id"]: completion for completion in user_completions}
    
    # Get user's mission submissions (including pending) for this month
    user_submissions = await db.mission_submissions.find({
        "user_id": current_user.id,
        "month_year": month_year
    }).to_list(None)
    
    submitted_mission_ids = {sub["mission_id"]: sub for sub in user_submissions}
    
    # Get today's date for daily limit checking
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    enhanced_missions = []
    for mission in missions:
        mission_data = {
            "id": mission["id"],
            "title": mission["title"],
            "description": mission["description"],
            "points": mission["points"],
            "frequency": mission.get("frequency", "one-time"),
            "daily_limit": mission.get("daily_limit", 0),
            "weekly_limit": mission.get("weekly_limit", 0),
            "requirements": mission.get("requirements", []),
            "requires_description": mission.get("requires_description", True),
            "requires_photo": mission.get("requires_photo", False),
            "photo_source": mission.get("photo_source", "both"),
            "requires_link": mission.get("requires_link", False),
            "requires_approval": mission.get("requires_approval", True)
        }
        
        # Check completion status and availability
        mission_id = mission["id"]
        frequency = mission.get("frequency", "one-time")
        
        # Check submission status
        has_submission = mission_id in submitted_mission_ids
        submission_info = submitted_mission_ids.get(mission_id)
        submission_status = submission_info["verification_status"] if submission_info else None
        
        if frequency == "one-time":
            mission_data["completed"] = mission_id in completed_mission_ids
            mission_data["pending_approval"] = has_submission and submission_status == "pending"
            mission_data["available"] = not has_submission and mission_id not in completed_mission_ids
            mission_data["completions_today"] = 0
            mission_data["completions_this_week"] = 0
        else:
            # Count submissions for frequency-based missions (including pending and approved)
            if frequency == "daily":
                submissions_today = await db.mission_submissions.count_documents({
                    "user_id": current_user.id,
                    "mission_id": mission_id,
                    "submitted_at": {
                        "$gte": datetime.combine(today, datetime.min.time()),
                        "$lt": datetime.combine(today + timedelta(days=1), datetime.min.time())
                    }
                })
                daily_limit = mission.get("daily_limit", 0)
                mission_data["completions_today"] = submissions_today
                mission_data["available"] = daily_limit == 0 or submissions_today < daily_limit
                mission_data["completed"] = False  # Daily missions are never "completed"
                mission_data["pending_approval"] = False
                mission_data["completions_this_week"] = 0
                
            elif frequency == "weekly":
                submissions_this_week = await db.mission_submissions.count_documents({
                    "user_id": current_user.id,
                    "mission_id": mission_id,
                    "submitted_at": {
                        "$gte": datetime.combine(week_start, datetime.min.time()),
                        "$lt": datetime.combine(week_start + timedelta(days=7), datetime.min.time())
                    }
                })
                weekly_limit = mission.get("weekly_limit", 0)
                mission_data["completions_this_week"] = submissions_this_week
                mission_data["available"] = weekly_limit == 0 or submissions_this_week < weekly_limit
                mission_data["completed"] = False  # Weekly missions are never "completed"
                mission_data["pending_approval"] = False
                mission_data["completions_today"] = 0
        
        enhanced_missions.append(mission_data)
    
    return enhanced_missions

@api_router.post("/missions/{mission_id}/submit")
async def submit_mission(
    mission_id: str,
    description: str = Form(...),
    submission_url: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = await get_current_user(credentials)
    
    # Get mission details
    mission = await db.missions.find_one({"id": mission_id, "is_active": True})
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found or inactive")
    
    frequency = mission.get("frequency", "one-time")
    month_year = get_current_month_year()
    
    # Check if user can submit this mission based on frequency and limits
    today = datetime.now().date()
    
    if frequency == "one-time":
        # Check if already submitted/completed
        existing_submission = await db.mission_submissions.find_one({
            "user_id": current_user.id,
            "mission_id": mission_id
        })
        if existing_submission:
            raise HTTPException(status_code=400, detail="Mission already submitted")
    
    elif frequency == "daily":
        daily_limit = mission.get("daily_limit", 0)
        if daily_limit > 0:
            submissions_today = await db.mission_submissions.count_documents({
                "user_id": current_user.id,
                "mission_id": mission_id,
                "submitted_at": {
                    "$gte": datetime.combine(today, datetime.min.time()),
                    "$lt": datetime.combine(today + timedelta(days=1), datetime.min.time())
                }
            })
            if submissions_today >= daily_limit:
                raise HTTPException(status_code=400, detail="Daily limit reached for this mission")
    
    elif frequency == "weekly":
        weekly_limit = mission.get("weekly_limit", 0)
        if weekly_limit > 0:
            week_start = today - timedelta(days=today.weekday())
            submissions_this_week = await db.mission_submissions.count_documents({
                "user_id": current_user.id,
                "mission_id": mission_id,
                "submitted_at": {
                    "$gte": datetime.combine(week_start, datetime.min.time()),
                    "$lt": datetime.combine(week_start + timedelta(days=7), datetime.min.time())
                }
            })
            if submissions_this_week >= weekly_limit:
                raise HTTPException(status_code=400, detail="Weekly limit reached for this mission")
    
    # Validate required fields based on mission settings
    if mission.get("requires_description", True) and not description.strip():
        raise HTTPException(status_code=400, detail="Description is required for this mission")
    
    if mission.get("requires_photo", False) and not photo:
        raise HTTPException(status_code=400, detail="Photo is required for this mission")
    
    if mission.get("requires_link", False) and not submission_url:
        raise HTTPException(status_code=400, detail="Link is required for this mission")
    
    # Handle photo upload if provided
    photo_url = None
    if photo:
        try:
            # Resize and save photo (reusing existing logic)
            image_data = await photo.read()
            image = Image.open(BytesIO(image_data))
            
            # Resize to reasonable size
            max_size = (800, 600)
            image.thumbnail(max_size, Image.LANCZOS)
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Save as base64
            output = BytesIO()
            image.save(output, format='JPEG', quality=85)
            photo_url = base64.b64encode(output.getvalue()).decode()
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid photo format: {str(e)}")
    
    # Create mission submission
    submission = MissionSubmission(
        user_id=current_user.id,
        mission_id=mission_id,
        mission_title=mission["title"],
        description=description,
        photo_url=photo_url,
        submission_url=submission_url,
        points_earned=mission["points"],
        month_year=month_year,
        verification_status="pending" if mission.get("requires_approval", True) else "approved"
    )
    
    await db.mission_submissions.insert_one(submission.dict())
    
    # If no approval required, automatically complete the mission
    if not mission.get("requires_approval", True):
        user_mission = UserMission(
            user_id=current_user.id,
            mission_id=mission_id,
            mission_title=mission["title"],
            points_earned=mission["points"],
            month_year=month_year,
            submission_id=submission.id
        )
        
        await db.user_missions.insert_one(user_mission.dict())
        
        # Update user's total points
        await db.users.update_one(
            {"id": current_user.id},
            {"$inc": {"total_points": mission["points"], "current_points": mission["points"]}}
        )
        
        # Create notification
        notification = Notification(
            user_id=current_user.id,
            title="🎯 Missione Completata!",
            message=f"Missione completata: '{mission['title']}' (+{mission['points']} punti)",
            type="success"
        )
        await db.notifications.insert_one(notification.dict())
        
        return {
            "message": f"Missione completata automaticamente! +{mission['points']} punti 🌿",
            "points_earned": mission["points"],
            "requires_approval": False
        }
    else:
        # Create notification for pending approval
        notification = Notification(
            user_id=current_user.id,
            title="📝 Missione Inviata",
            message=f"Missione '{mission['title']}' inviata per verifica. Riceverai i punti dopo l'approvazione.",
            type="info"
        )
        await db.notifications.insert_one(notification.dict())
        
        return {
            "message": f"Missione inviata per verifica! 📝",
            "requires_approval": True,
            "points_earned": mission["points"]
        }

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

@api_router.get("/admin/prizes")
async def get_admin_prizes(
    month_year: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get prizes with admin info for current month"""
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not month_year:
        month_year = get_current_month_year()
    
    # Default prizes template
    default_prizes = [
        {
            "position": 1,
            "title": "🥇 Notte per 2 persone",
            "description": "Una notte gratuita nel nostro B&B per 2 persone con colazione inclusa",
            "image_url": None,
            "month_year": month_year,
            "is_custom": False
        },
        {
            "position": 2,
            "title": "🥈 Cena o degustazione per 2",
            "description": "Esperienza culinaria presso un partner selezionato per 2 persone",
            "image_url": None,
            "month_year": month_year,
            "is_custom": False
        },
        {
            "position": 3,
            "title": "🥉 Drink Experience per 2",
            "description": "Aperitivo o drink speciale presso un partner per 2 persone",
            "image_url": None,
            "month_year": month_year,
            "is_custom": False
        }
    ]
    
    # Get custom prizes from database
    custom_prizes = await db.prizes.find({"month_year": month_year}).to_list(10)
    
    # Create a map of custom prizes by position
    custom_prize_map = {prize["position"]: prize for prize in custom_prizes}
    
    # Merge custom prizes with defaults
    result_prizes = []
    for default_prize in default_prizes:
        position = default_prize["position"]
        if position in custom_prize_map:
            custom_prize = custom_prize_map[position]
            result_prizes.append({
                "id": custom_prize.get("id"),
                "position": position,
                "title": custom_prize["title"],
                "description": custom_prize["description"],
                "image_url": custom_prize.get("image_url"),
                "month_year": month_year,
                "is_custom": True
            })
        else:
            result_prizes.append(default_prize)
    
    return result_prizes

@api_router.put("/admin/prizes/{position}")
async def update_prize(
    position: int,
    update_request: PrizeUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update or create custom prize for specific position"""
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if position not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="Position must be 1, 2, or 3")
    
    month_year = get_current_month_year()
    
    # Check if custom prize already exists
    existing_prize = await db.prizes.find_one({
        "position": position,
        "month_year": month_year
    })
    
    if existing_prize:
        # Update existing custom prize
        update_data = {}
        if update_request.title: update_data["title"] = update_request.title
        if update_request.description: update_data["description"] = update_request.description  
        if update_request.image_url is not None: update_data["image_url"] = update_request.image_url
        
        await db.prizes.update_one(
            {"id": existing_prize["id"]},
            {"$set": update_data}
        )
    else:
        # Create new custom prize
        prize = Prize(
            position=position,
            title=update_request.title or f"Premio {position}° posto",
            description=update_request.description or "Descrizione premio personalizzato",
            image_url=update_request.image_url,
            month_year=month_year
        )
        await db.prizes.insert_one(prize.dict())
    
    return {"message": f"🌿 Premio {position}° posto aggiornato con successo!"}

@api_router.delete("/admin/prizes/{position}")
async def restore_default_prize(
    position: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Restore prize to default values"""
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if position not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="Position must be 1, 2, or 3")
    
    month_year = get_current_month_year()
    
    # Remove custom prize to fall back to default
    await db.prizes.delete_one({
        "position": position,
        "month_year": month_year
    })
    
    return {"message": f"⚙️ Premio {position}° posto ripristinato ai valori predefiniti!"}

@api_router.post("/admin/prizes/upload-image")
async def upload_prize_image(
    photo: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Upload image for prize"""
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Process image similar to avatar upload
        image_data = await photo.read()
        image = Image.open(BytesIO(image_data))
        
        # Resize to appropriate size for prizes
        max_size = (400, 300)
        image.thumbnail(max_size, Image.LANCZOS)
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Save as base64
        output = BytesIO()
        image.save(output, format='JPEG', quality=90)
        image_url = base64.b64encode(output.getvalue()).decode()
        
        return {"image_url": image_url, "message": "Immagine caricata con successo!"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Errore nel caricamento dell'immagine: {str(e)}")

# === CLUB CARD ENDPOINTS ===

@api_router.get("/club-card")
async def get_club_card(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get user's digital club card data"""
    current_user = await get_current_user(credentials)
    
    # Initialize club card if not exists
    await initialize_club_card(current_user.id)
    
    # Refresh user data
    user_doc = await db.users.find_one({"id": current_user.id})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = User(**user_doc)
    
    return {
        "name": user.name,
        "username": user.username,
        "club_card_code": user.club_card_code,
        "club_card_qr_url": user.club_card_qr_url,
        "join_date": user.join_date.isoformat() if user.join_date else None,
        "level": get_user_level(user.total_points),
        "total_points": user.total_points,
        "avatar_url": user.avatar_url
    }

@api_router.get("/club-card/qr/{user_id}")
async def get_user_profile_by_qr(user_id: str):
    """Public endpoint for QR code access"""
    user_doc = await db.users.find_one({"id": user_id})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = User(**user_doc)
    
    return {
        "name": user.name,
        "username": user.username,
        "level": get_user_level(user.total_points),
        "total_points": user.total_points,
        "join_date": user.join_date.isoformat() if user.join_date else None,
        "avatar_url": user.avatar_url,
        "club_member": True
    }

# === TRANSLATION ENDPOINTS ===

@api_router.get("/translations")
async def get_translations(language: str = "it"):
    """Get all translations for specified language"""
    if language not in ["it", "en"]:
        language = "it"
    
    translations = await db.translations.find({}).to_list(None)
    
    result = {}
    for translation in translations:
        key = translation["key"]
        if language == "it":
            result[key] = translation["italian"]
        else:
            result[key] = translation["english"]
    
    # If no translations found, return default Italian translations
    if not result:
        result = get_default_translations(language)
    
    return result

@api_router.put("/user/language")
async def update_user_language(
    language: str = Query(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update user's preferred language"""
    current_user = await get_current_user(credentials)
    
    if language not in ["it", "en"]:
        raise HTTPException(status_code=400, detail="Language must be 'it' or 'en'")
    
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"preferred_language": language}}
    )
    
    return {"message": f"🌿 Lingua aggiornata: {'Italiano' if language == 'it' else 'English'}"}

@api_router.get("/admin/translations")
async def get_admin_translations(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all translations for admin management"""
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    translations = await db.translations.find({}).to_list(None)
    
    return translations

@api_router.post("/admin/translations")
async def create_translation(
    key: str = Query(...),
    italian: str = Query(...),
    english: str = Query(...),
    category: str = Query("general"),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create or update translation"""
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if translation key already exists
    existing = await db.translations.find_one({"key": key})
    
    if existing:
        # Update existing translation
        await db.translations.update_one(
            {"key": key},
            {"$set": {
                "italian": italian,
                "english": english,
                "category": category
            }}
        )
    else:
        # Create new translation
        translation = Translation(
            key=key,
            italian=italian,
            english=english,
            category=category
        )
        await db.translations.insert_one(translation.dict())
    
    return {"message": "Traduzione salvata con successo!"}

def get_default_translations(language: str = "it") -> dict:
    """Get default translations"""
    if language == "en":
        return {
            # Navigation
            "home": "Home",
            "leaderboard": "Leaderboard", 
            "prizes": "Prizes",
            "missions": "Missions",
            "profile": "Profile",
            "admin_panel": "Admin Panel",
            
            # Common
            "welcome": "Welcome",
            "points": "points",
            "level": "Level",
            "loading": "Loading...",
            "save": "Save",
            "cancel": "Cancel",
            "confirm": "Confirm",
            "delete": "Delete",
            
            # Missions
            "mission_completed": "Mission accomplished 🌿",
            "monthly_rewards": "Monthly Rewards",
            "my_club_card": "My Club Card",
            "join_club": "Join the Club",
            
            # Messages
            "language_updated_en": "🌿 Language updated: English",
            "language_updated_it": "🌿 Lingua aggiornata: Italiano"
        }
    else:
        return {
            # Navigation
            "home": "Home",
            "leaderboard": "Classifica",
            "prizes": "Premi", 
            "missions": "Missioni",
            "profile": "Profilo",
            "admin_panel": "Pannello Admin",
            
            # Common
            "welcome": "Benvenuto",
            "points": "punti",
            "level": "Livello",
            "loading": "Caricamento...",
            "save": "Salva",
            "cancel": "Annulla", 
            "confirm": "Conferma",
            "delete": "Elimina",
            
            # Missions
            "mission_completed": "Missione completata 🌿",
            "monthly_rewards": "Premi del mese",
            "my_club_card": "La mia Card",
            "join_club": "Accedi al Club",
            
            # Messages
            "language_updated_en": "🌿 Language updated: English", 
            "language_updated_it": "🌿 Lingua aggiornata: Italiano"
        }

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
    
    # Clean notifications to avoid ObjectId issues
    clean_notifications = []
    for notif in notifications:
        clean_notif = {
            "id": notif["id"],
            "user_id": notif["user_id"],
            "title": notif["title"],
            "message": notif["message"],
            "type": notif["type"],
            "read": notif["read"],
            "created_at": notif["created_at"].isoformat() if "created_at" in notif else None
        }
        clean_notifications.append(clean_notif)
    
    return clean_notifications

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

# === ADMIN PANEL APIs ===

@api_router.post("/admin/email/send")
async def send_admin_email(
    email_request: EmailRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Process template variables
    processed_recipients = []
    for recipient_id in email_request.recipients:
        user_doc = await db.users.find_one({"id": recipient_id})
        if user_doc:
            # Replace variables in email body
            user_body = email_request.body
            user_body = user_body.replace("{{user_name}}", user_doc["name"])
            user_body = user_body.replace("{{user_points}}", str(user_doc["current_points"]))
            user_body = user_body.replace("{{user_level}}", user_doc["level"])
            user_body = user_body.replace("{{month_theme}}", "Live Puglia Challenge")
            
            # Calculate points to top 3
            leaderboard = await db.user_actions.aggregate([
                {"$match": {"month_year": get_current_month_year(), "verification_status": "approved"}},
                {"$group": {"_id": "$user_id", "total_points": {"$sum": "$points_earned"}}},
                {"$sort": {"total_points": -1}},
                {"$limit": 3}
            ]).to_list(3)
            
            points_to_top3 = 0
            if len(leaderboard) >= 3:
                points_to_top3 = max(0, leaderboard[2]["total_points"] - user_doc["current_points"] + 1)
            
            user_body = user_body.replace("{{points_to_top3}}", str(points_to_top3))
            
            processed_recipients.append({
                "email": user_doc["email"],
                "body": user_body
            })
    
    # Send emails to all recipients
    sent_count = 0
    failed_count = 0
    failed_emails = []
    
    for recipient in processed_recipients:
        success = await send_email(recipient["email"], email_request.subject, recipient["body"])
        if success:
            sent_count += 1
        else:
            failed_count += 1
            failed_emails.append(recipient["email"])
    
    # Determine status based on results
    email_status = "sent" if failed_count == 0 else ("partial" if sent_count > 0 else "failed")
    
    # Log email
    email_log = EmailLog(
        recipients=[r["email"] for r in processed_recipients],
        subject=email_request.subject,
        body=email_request.body,
        admin_id=current_user.id,
        status=email_status
    )
    await db.email_log.insert_one(email_log.dict())
    
    # Prepare response message
    if failed_count == 0:
        return {"message": f"📩 Email inviata con successo a {sent_count} utenti 🌿"}
    elif sent_count > 0:
        return {"message": f"📩 Email inviata a {sent_count} utenti, {failed_count} fallite. Controlla la configurazione SMTP."}
    else:
        return {"message": f"❌ Invio email fallito per tutti i {failed_count} destinatari. Controlla la configurazione SMTP."}

@api_router.get("/admin/email/logs")
async def get_email_logs(
    limit: int = 50,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    logs = await db.email_log.find().sort("sent_at", -1).limit(limit).to_list(limit)
    
    clean_logs = []
    for log in logs:
        clean_log = {
            "id": log["id"],
            "recipients": log["recipients"],
            "subject": log["subject"],
            "sent_at": log["sent_at"].isoformat() if "sent_at" in log else None,
            "status": log["status"],
            "recipient_count": len(log["recipients"])
        }
        clean_logs.append(clean_log)
    
    return clean_logs

@api_router.post("/admin/email/test")
async def test_email_config(
    test_email: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Test email configuration by sending a test email"""
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    subject = "🌿 Test Email - Desideri di Puglia Club"
    body = """
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #d4af37;">Desideri di Puglia Club</h2>
        <p>Questo è un test di configurazione email.</p>
        <p>Se ricevi questo messaggio, l'integrazione SMTP è funzionante! 🌿</p>
        <p style="color: #8b7355; font-style: italic;">- Team Desideri di Puglia</p>
    </body>
    </html>
    """
    
    success = await send_email(test_email, subject, body)
    
    if success:
        return {"message": f"📩 Email di test inviata con successo a {test_email}"}
    else:
        raise HTTPException(status_code=500, detail="Invio email fallito. Controlla la configurazione SMTP.")

@api_router.get("/admin/users/list")
async def get_users_for_email(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get list of users for email selection"""
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = await db.users.find(
        {}, 
        {"id": 1, "name": 1, "email": 1, "current_points": 1, "level": 1}
    ).to_list(length=None)
    
    user_list = []
    for user in users:
        user_list.append({
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "current_points": user.get("current_points", 0),
            "level": user.get("level", "Novizio")
        })
    
    return user_list

# === MISSIONS API ===

@api_router.post("/admin/missions")
async def create_mission(
    mission_request: MissionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Build requirements based on frequency and limits
    requirements = []
    if mission_request.frequency == "daily" and mission_request.daily_limit > 0:
        requirements.append(f"Limite giornaliero: {mission_request.daily_limit}")
    elif mission_request.frequency == "weekly" and mission_request.weekly_limit > 0:
        requirements.append(f"Limite settimanale: {mission_request.weekly_limit}")
    elif mission_request.frequency == "one-time":
        requirements.append("Completabile una volta sola")
    
    if not requirements:
        requirements.append("Nessun limite")
    
    mission = Mission(
        title=mission_request.title,
        description=mission_request.description,
        points=mission_request.points,
        frequency=mission_request.frequency,
        month_year=get_current_month_year(),
        is_active=mission_request.is_active,
        daily_limit=mission_request.daily_limit,
        weekly_limit=mission_request.weekly_limit,
        requirements=requirements,
        requires_description=mission_request.requires_description,
        requires_photo=mission_request.requires_photo,
        photo_source=mission_request.photo_source,
        requires_link=mission_request.requires_link,
        requires_approval=mission_request.requires_approval
    )
    
    await db.missions.insert_one(mission.dict())
    return {"message": "Missione creata con successo!", "mission_id": mission.id}

@api_router.get("/admin/missions")
async def get_admin_missions(credentials: HTTPAuthorizationCredentials = Depends(security)):
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    missions = await db.missions.find().sort("created_at", -1).to_list(100)
    
    clean_missions = []
    for mission in missions:
        # Count completions for statistics
        completion_count = await db.user_missions.count_documents({"mission_id": mission["id"]})
        
        clean_mission = {
            "id": mission["id"],
            "title": mission["title"],
            "description": mission["description"],
            "points": mission["points"],
            "frequency": mission.get("frequency", "one-time"),
            "daily_limit": mission.get("daily_limit", 0),
            "weekly_limit": mission.get("weekly_limit", 0),
            "month_year": mission["month_year"],
            "is_active": mission["is_active"],
            "requirements": mission.get("requirements", []),
            "requires_description": mission.get("requires_description", True),
            "requires_photo": mission.get("requires_photo", False),
            "photo_source": mission.get("photo_source", "both"),
            "requires_link": mission.get("requires_link", False),
            "requires_approval": mission.get("requires_approval", True),
            "completion_count": completion_count,
            "created_at": mission["created_at"].isoformat() if "created_at" in mission else None
        }
        clean_missions.append(clean_mission)
    
    return clean_missions

# Models moved to top of file

@api_router.put("/admin/missions/{mission_id}")
async def update_mission(
    mission_id: str,
    update_request: MissionUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if mission exists
    mission = await db.missions.find_one({"id": mission_id})
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    update_data = {}
    if update_request.title: update_data["title"] = update_request.title
    if update_request.description: update_data["description"] = update_request.description
    if update_request.points: update_data["points"] = update_request.points
    if update_request.frequency: update_data["frequency"] = update_request.frequency
    if update_request.daily_limit is not None: update_data["daily_limit"] = update_request.daily_limit
    if update_request.weekly_limit is not None: update_data["weekly_limit"] = update_request.weekly_limit
    if update_request.is_active is not None: update_data["is_active"] = update_request.is_active
    if update_request.requires_description is not None: update_data["requires_description"] = update_request.requires_description
    if update_request.requires_photo is not None: update_data["requires_photo"] = update_request.requires_photo
    if update_request.photo_source: update_data["photo_source"] = update_request.photo_source
    if update_request.requires_link is not None: update_data["requires_link"] = update_request.requires_link
    if update_request.requires_approval is not None: update_data["requires_approval"] = update_request.requires_approval
    
    # Update requirements based on frequency changes
    if update_request.frequency or update_request.daily_limit is not None or update_request.weekly_limit is not None:
        frequency = update_request.frequency or mission.get("frequency", "one-time")
        daily_limit = update_request.daily_limit if update_request.daily_limit is not None else mission.get("daily_limit", 0)
        weekly_limit = update_request.weekly_limit if update_request.weekly_limit is not None else mission.get("weekly_limit", 0)
        
        requirements = []
        if frequency == "daily" and daily_limit > 0:
            requirements.append(f"Limite giornaliero: {daily_limit}")
        elif frequency == "weekly" and weekly_limit > 0:
            requirements.append(f"Limite settimanale: {weekly_limit}")
        elif frequency == "one-time":
            requirements.append("Completabile una volta sola")
        
        if not requirements:
            requirements.append("Nessun limite")
        
        update_data["requirements"] = requirements
    
    await db.missions.update_one({"id": mission_id}, {"$set": update_data})
    return {"message": "Missione aggiornata con successo!"}

@api_router.get("/admin/missions/statistics")
async def get_mission_statistics(
    month_year: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get detailed mission statistics for admin dashboard"""
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not month_year:
        month_year = get_current_month_year()
    
    # Get all missions for the specified month
    missions = await db.missions.find({"month_year": month_year}).to_list(None)
    
    statistics = []
    total_completions = 0
    total_points_awarded = 0
    
    for mission in missions:
        mission_id = mission["id"]
        
        # Count total completions for this mission
        completions = await db.user_missions.count_documents({"mission_id": mission_id})
        
        # Count unique users who completed this mission
        unique_completers = len(await db.user_missions.distinct("user_id", {"mission_id": mission_id}))
        
        # Calculate total points awarded for this mission
        points_awarded = completions * mission["points"]
        
        # Get recent completions (last 7 days)
        recent_completions = await db.user_missions.count_documents({
            "mission_id": mission_id,
            "completed_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
        })
        
        total_completions += completions
        total_points_awarded += points_awarded
        
        mission_stats = {
            "mission_id": mission_id,
            "title": mission["title"],
            "description": mission["description"],
            "points": mission["points"],
            "frequency": mission.get("frequency", "one-time"),
            "is_active": mission["is_active"],
            "total_completions": completions,
            "unique_completers": unique_completers,
            "points_awarded": points_awarded,
            "recent_completions": recent_completions,
            "created_at": mission["created_at"].isoformat() if "created_at" in mission else None
        }
        
        statistics.append(mission_stats)
    
    # Sort by total completions (most popular first)
    statistics.sort(key=lambda x: x["total_completions"], reverse=True)
    
    # Get overall statistics
    total_missions = len(missions)
    active_missions = len([m for m in missions if m["is_active"]])
    
    return {
        "month_year": month_year,
        "overview": {
            "total_missions": total_missions,
            "active_missions": active_missions,
            "total_completions": total_completions,
            "total_points_awarded": total_points_awarded,
            "average_completions_per_mission": round(total_completions / total_missions, 2) if total_missions > 0 else 0
        },
        "missions": statistics
    }

@api_router.get("/admin/missions/submissions/pending")
async def get_pending_mission_submissions(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get pending mission submissions for admin review"""
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    submissions = await db.mission_submissions.find(
        {"verification_status": "pending"}
    ).sort("submitted_at", -1).to_list(100)
    
    clean_submissions = []
    for submission in submissions:
        # Get user info
        user_doc = await db.users.find_one({"id": submission["user_id"]})
        user_name = user_doc["name"] if user_doc else "Unknown User"
        username = user_doc["username"] if user_doc else "unknown"
        
        clean_submission = {
            "id": submission["id"],
            "user_id": submission["user_id"],
            "user_name": user_name,
            "username": username,
            "mission_id": submission["mission_id"],
            "mission_title": submission["mission_title"],
            "description": submission["description"],
            "photo_url": submission.get("photo_url"),
            "submission_url": submission.get("submission_url"),
            "points_earned": submission["points_earned"],
            "submitted_at": submission["submitted_at"].isoformat() if "submitted_at" in submission else None,
            "verification_status": submission["verification_status"]
        }
        clean_submissions.append(clean_submission)
    
    return clean_submissions

@api_router.put("/admin/missions/submissions/{submission_id}/verify")
async def verify_mission_submission(
    submission_id: str,
    status: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Approve or reject mission submission"""
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Status must be 'approved' or 'rejected'")
    
    # Get submission
    submission = await db.mission_submissions.find_one({"id": submission_id})
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if submission["verification_status"] != "pending":
        raise HTTPException(status_code=400, detail="Submission already processed")
    
    # Update submission status
    await db.mission_submissions.update_one(
        {"id": submission_id},
        {"$set": {
            "verification_status": status,
            "verified_at": datetime.utcnow(),
            "verified_by": current_user.id
        }}
    )
    
    if status == "approved":
        # Create user mission record and award points
        user_mission = UserMission(
            user_id=submission["user_id"],
            mission_id=submission["mission_id"],
            mission_title=submission["mission_title"],
            points_earned=submission["points_earned"],
            month_year=submission["month_year"],
            submission_id=submission_id
        )
        
        await db.user_missions.insert_one(user_mission.dict())
        
        # Update user points
        await db.users.update_one(
            {"id": submission["user_id"]},
            {"$inc": {"total_points": submission["points_earned"], "current_points": submission["points_earned"]}}
        )
        
        # Create success notification
        notification = Notification(
            user_id=submission["user_id"],
            title="🎉 Missione Approvata!",
            message=f"Missione '{submission['mission_title']}' approvata! +{submission['points_earned']} punti",
            type="success"
        )
    else:
        # Create rejection notification
        notification = Notification(
            user_id=submission["user_id"],
            title="❌ Missione Non Approvata",
            message=f"La missione '{submission['mission_title']}' non è stata approvata. Riprova seguendo meglio le istruzioni.",
            type="warning"
        )
    
    await db.notifications.insert_one(notification.dict())
    
    return {"message": f"Mission submission {status} successfully"}

# === WEEKLY QUIZ API ===

@api_router.post("/admin/quiz")
async def create_weekly_quiz(
    title: str,
    description: str,
    questions: List[Dict],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Set end date to 7 days from now
    end_date = datetime.utcnow() + timedelta(days=7)
    
    quiz = WeeklyQuiz(
        title=title,
        description=description,
        questions=questions,
        quiz_end_date=end_date,
        created_by=current_user.id
    )
    
    await db.weekly_quiz.insert_one(quiz.dict())
    return {"message": "Quiz settimanale creato con successo!", "quiz_id": quiz.id}

@api_router.get("/admin/quiz")
async def get_admin_quizzes(credentials: HTTPAuthorizationCredentials = Depends(security)):
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    quizzes = await db.weekly_quiz.find().sort("quiz_start_date", -1).to_list(50)
    
    clean_quizzes = []
    for quiz in quizzes:
        # Count completions
        completions = await db.quiz_completions.count_documents({"quiz_id": quiz["id"]})
        
        clean_quiz = {
            "id": quiz["id"],
            "title": quiz["title"],
            "description": quiz["description"],
            "quiz_start_date": quiz["quiz_start_date"].isoformat() if "quiz_start_date" in quiz else None,
            "quiz_end_date": quiz["quiz_end_date"].isoformat() if quiz.get("quiz_end_date") else None,
            "is_active": quiz["is_active"],
            "completions_count": completions
        }
        clean_quizzes.append(clean_quiz)
    
    return clean_quizzes

@api_router.put("/admin/quiz/{quiz_id}/close")
async def close_quiz(
    quiz_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = await get_current_user(credentials)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    await db.weekly_quiz.update_one(
        {"id": quiz_id},
        {"$set": {"is_active": False, "quiz_end_date": datetime.utcnow()}}
    )
    
    return {"message": "Quiz chiuso con successo!"}

# === USER QUIZ API ===

@api_router.get("/quiz/active")
async def get_active_quiz(credentials: HTTPAuthorizationCredentials = Depends(security)):
    current_user = await get_current_user(credentials)
    
    # Get active quiz
    quiz = await db.weekly_quiz.find_one({
        "is_active": True,
        "quiz_end_date": {"$gt": datetime.utcnow()}
    })
    
    if not quiz:
        return {"quiz": None, "message": "Nessun quiz attivo al momento"}
    
    # Check if user already completed it
    completion = await db.quiz_completions.find_one({
        "user_id": current_user.id,
        "quiz_id": quiz["id"]
    })
    
    if completion:
        return {"quiz": None, "message": "Hai già completato il quiz di questa settimana!"}
    
    # Return quiz without correct answers
    clean_quiz = {
        "id": quiz["id"],
        "title": quiz["title"],
        "description": quiz["description"],
        "questions": [{
            "question": q["question"],
            "options": q["options"]
        } for q in quiz["questions"]],
        "quiz_end_date": quiz["quiz_end_date"].isoformat() if quiz.get("quiz_end_date") else None
    }
    
    return {"quiz": clean_quiz}

@api_router.post("/quiz/{quiz_id}/submit")
async def submit_quiz(
    quiz_id: str,
    answers: List[int],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    current_user = await get_current_user(credentials)
    
    quiz = await db.weekly_quiz.find_one({"id": quiz_id})
    if not quiz or not quiz["is_active"]:
        raise HTTPException(status_code=404, detail="Quiz non trovato o non attivo")
    
    # Check if already completed
    existing = await db.quiz_completions.find_one({
        "user_id": current_user.id,
        "quiz_id": quiz_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="Quiz già completato")
    
    # Calculate score
    score = 0
    for i, answer in enumerate(answers):
        if i < len(quiz["questions"]) and answer == quiz["questions"][i]["correct"]:
            score += 1
    
    points_earned = 30 if score == len(quiz["questions"]) else 0
    
    # Save completion
    completion = QuizCompletion(
        user_id=current_user.id,
        quiz_id=quiz_id,
        answers=answers,
        score=score,
        points_earned=points_earned
    )
    await db.quiz_completions.insert_one(completion.dict())
    
    # Award points if perfect score
    if points_earned > 0:
        await db.users.update_one(
            {"id": current_user.id},
            {
                "$inc": {
                    "current_points": points_earned,
                    "total_points": points_earned
                }
            }
        )
        
        # Check for badges
        await check_and_award_badges(current_user.id, "quiz_complete")
        
        # Send notification
        notification = Notification(
            user_id=current_user.id,
            title="🎯 Quiz Completato!",
            message=f"Ottimo lavoro! Hai completato il quiz settimanale e guadagnato {points_earned} punti 🌿",
            type="success"
        )
        await db.notifications.insert_one(notification.dict())
    
    return {
        "score": score,
        "total_questions": len(quiz["questions"]),
        "points_earned": points_earned,
        "message": "🎯 Ottimo lavoro! Hai completato il quiz settimanale e guadagnato 30 punti 🌿" if points_earned > 0 else "Quiz completato! Riprova la prossima settimana per guadagnare punti."
    }

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
