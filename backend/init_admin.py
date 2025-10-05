#!/usr/bin/env python3
"""
Script to initialize admin user and sample data for Desideri di Puglia Club
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import uuid
from datetime import datetime

# Configuration
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def init_admin():
    """Initialize admin user and sample data"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🚀 Initializing Desideri di Puglia Club...")
    
    # Check if admin already exists
    existing_admin = await db.users.find_one({"email": "admin@desideridipuglia.com"})
    if existing_admin:
        print("✅ Admin user already exists!")
        return
    
    # Create admin user
    admin_user = {
        "id": str(uuid.uuid4()),
        "name": "Admin Desideri di Puglia",
        "username": "admin_dp",
        "email": "admin@desideridipuglia.com",
        "password_hash": pwd_context.hash("admin123"),
        "country": "IT",
        "avatar_url": None,
        "current_points": 0,
        "total_points": 0,
        "level": "Legend",
        "badges": ["Founder", "Admin"],
        "position": 0,
        "created_at": datetime.utcnow(),
        "last_reset": datetime.utcnow(),
        "is_admin": True
    }
    
    await db.users.insert_one(admin_user)
    print("✅ Admin user created!")
    print(f"   Email: admin@desideridipuglia.com")
    print(f"   Password: admin123")
    
    # Create sample test user
    test_user = {
        "id": str(uuid.uuid4()),
        "name": "Marco Pugliese",
        "username": "marco_explorer",
        "email": "test@desideridipuglia.com",
        "password_hash": pwd_context.hash("test123"),
        "country": "IT",
        "avatar_url": None,
        "current_points": 150,
        "total_points": 350,
        "level": "Explorer",
        "badges": [],
        "position": 1,
        "created_at": datetime.utcnow(),
        "last_reset": datetime.utcnow(),
        "is_admin": False
    }
    
    await db.users.insert_one(test_user)
    print("✅ Test user created!")
    print(f"   Email: test@desideridipuglia.com")
    print(f"   Password: test123")
    
    # Create sample mission
    mission = {
        "id": str(uuid.uuid4()),
        "title": "Tramonto Pugliese",
        "description": "Condividi una foto del tramonto pugliese per guadagnare punti extra!",
        "points": 50,
        "month_year": datetime.now().strftime("%Y-%m"),
        "is_active": True,
        "requirements": ["Foto del tramonto", "Tag @desideridipuglia", "Hashtag #TramontoInPuglia"],
        "created_at": datetime.utcnow()
    }
    
    await db.missions.insert_one(mission)
    print("✅ Sample mission created!")
    
    client.close()
    print("\n🎉 Initialization complete! You can now:")
    print("   1. Login as admin: admin@desideridipuglia.com / admin123")
    print("   2. Login as test user: test@desideridipuglia.com / test123")
    print("   3. Start using the Desideri di Puglia Club! 🌿")

if __name__ == "__main__":
    asyncio.run(init_admin())