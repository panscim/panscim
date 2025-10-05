#!/usr/bin/env python3
"""
Phase 4 Backend Testing Suite for Desideri di Puglia Club
Tests: Admin Prize Editor + Digital Club Card + Multilingual Support
"""

import requests
import json
import os
import sys
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
from io import BytesIO
from PIL import Image

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://puglia-loyalty.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class Phase4Tester:
    def __init__(self):
        self.admin_token = None
        self.regular_user_token = None
        self.test_results = []
        self.admin_user_id = None
        self.test_user_id = None
        
    def log_result(self, test_name: str, success: bool, message: str, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} - {test_name}: {message}")
        if details and not success:
            print(f"    Details: {details}")
    
    def setup_test_users(self):
        """Setup admin and regular user authentication"""
        print("\n🔧 Setting up test users...")
        
        # Admin credentials from review request
        admin_credentials = {"email": "admin@desideridipuglia.com", "password": "admin123"}
        
        try:
            response = requests.post(f"{API_BASE}/auth/login", json=admin_credentials)
            if response.status_code == 200:
                data = response.json()
                user_data = data.get("user", {})
                if user_data.get("is_admin", False):
                    self.admin_token = data["access_token"]
                    self.admin_user_id = user_data["id"]
                    print(f"✅ Admin login successful: {admin_credentials['email']}")
                else:
                    print(f"❌ User {admin_credentials['email']} exists but is not admin")
                    return False
            else:
                print(f"❌ Failed to login admin user: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error logging in admin user: {str(e)}")
            return False
        
        # Regular user credentials from review request
        user_credentials = {"email": "test@desideridipuglia.com", "password": "test123"}
        
        try:
            response = requests.post(f"{API_BASE}/auth/login", json=user_credentials)
            if response.status_code == 200:
                data = response.json()
                self.regular_user_token = data["access_token"]
                self.test_user_id = data["user"]["id"]
                print(f"✅ Regular user login successful: {user_credentials['email']}")
            else:
                print(f"❌ Failed to login regular user: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error logging in regular user: {str(e)}")
            return False
        
        return True
    
    # ===== ADMIN PRIZE EDITOR TESTS =====
    
    def test_get_admin_prizes(self):
        """Test GET /api/admin/prizes - Get default prizes with custom override capability"""
        print("\n🏆 Testing Admin Prize Editor - Get Prizes...")
        
        if not self.admin_token:
            self.log_result("Get Admin Prizes", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/admin/prizes", headers=headers)
            
            if response.status_code == 200:
                prizes = response.json()
                if isinstance(prizes, list) and len(prizes) >= 3:
                    # Check structure of prizes
                    required_fields = ["position", "title", "description", "month_year", "is_custom"]
                    all_valid = True
                    
                    for prize in prizes:
                        missing_fields = [field for field in required_fields if field not in prize]
                        if missing_fields:
                            all_valid = False
                            self.log_result(
                                "Get Admin Prizes", 
                                False, 
                                f"Prize missing fields: {missing_fields}",
                                f"Prize: {prize}"
                            )
                            break
                    
                    if all_valid:
                        positions = [p["position"] for p in prizes]
                        if 1 in positions and 2 in positions and 3 in positions:
                            self.log_result(
                                "Get Admin Prizes", 
                                True, 
                                f"Successfully retrieved {len(prizes)} prizes with correct structure (1st, 2nd, 3rd place)"
                            )
                        else:
                            self.log_result(
                                "Get Admin Prizes", 
                                False, 
                                f"Missing required prize positions. Found: {positions}"
                            )
                else:
                    self.log_result(
                        "Get Admin Prizes", 
                        False, 
                        f"Expected list of at least 3 prizes, got: {type(prizes)} with {len(prizes) if isinstance(prizes, list) else 'unknown'} items"
                    )
            elif response.status_code == 403:
                self.log_result(
                    "Get Admin Prizes", 
                    False, 
                    "Access denied - admin authentication failed",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Get Admin Prizes", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Get Admin Prizes", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_update_prize(self):
        """Test PUT /api/admin/prizes/{position} - Update prize"""
        print("\n✏️ Testing Admin Prize Editor - Update Prize...")
        
        if not self.admin_token:
            self.log_result("Update Prize", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        position = 1  # Update 1st place prize
        
        update_data = {
            "title": "🥇 Weekend Romantico per 2",
            "description": "Due notti nel nostro B&B con colazione, cena romantica e tour guidato della città",
            "image_url": None
        }
        
        try:
            response = requests.put(
                f"{API_BASE}/admin/prizes/{position}",
                json=update_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                if "aggiornato" in message or "updated" in message.lower():
                    self.log_result(
                        "Update Prize", 
                        True, 
                        f"Prize {position} updated successfully: {message}"
                    )
                    
                    # Verify the update by getting prizes again
                    self.verify_prize_update(position, update_data)
                else:
                    self.log_result(
                        "Update Prize", 
                        False, 
                        f"Unexpected response message: {message}"
                    )
            elif response.status_code == 400:
                self.log_result(
                    "Update Prize", 
                    False, 
                    "Bad request - invalid position or data",
                    f"Response: {response.text}"
                )
            elif response.status_code == 403:
                self.log_result(
                    "Update Prize", 
                    False, 
                    "Access denied - admin authentication failed",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Update Prize", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Update Prize", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def verify_prize_update(self, position: int, expected_data: dict):
        """Verify that prize was updated correctly"""
        print(f"\n🔍 Verifying Prize {position} Update...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/admin/prizes", headers=headers)
            
            if response.status_code == 200:
                prizes = response.json()
                updated_prize = next((p for p in prizes if p["position"] == position), None)
                
                if updated_prize:
                    if (updated_prize["title"] == expected_data["title"] and 
                        updated_prize["description"] == expected_data["description"] and
                        updated_prize.get("is_custom", False) == True):
                        self.log_result(
                            "Verify Prize Update", 
                            True, 
                            f"Prize {position} correctly updated and marked as custom"
                        )
                    else:
                        self.log_result(
                            "Verify Prize Update", 
                            False, 
                            f"Prize {position} not updated correctly",
                            f"Expected: {expected_data}, Got: {updated_prize}"
                        )
                else:
                    self.log_result(
                        "Verify Prize Update", 
                        False, 
                        f"Prize {position} not found after update"
                    )
            else:
                self.log_result(
                    "Verify Prize Update", 
                    False, 
                    f"Failed to retrieve prizes for verification: {response.status_code}"
                )
        except Exception as e:
            self.log_result(
                "Verify Prize Update", 
                False, 
                f"Verification request failed: {str(e)}"
            )
    
    def test_restore_default_prize(self):
        """Test DELETE /api/admin/prizes/{position} - Restore to defaults"""
        print("\n🔄 Testing Admin Prize Editor - Restore Default Prize...")
        
        if not self.admin_token:
            self.log_result("Restore Default Prize", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        position = 1  # Restore 1st place prize to default
        
        try:
            response = requests.delete(f"{API_BASE}/admin/prizes/{position}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                if "ripristinato" in message or "restored" in message.lower():
                    self.log_result(
                        "Restore Default Prize", 
                        True, 
                        f"Prize {position} restored to default: {message}"
                    )
                    
                    # Verify restoration
                    self.verify_prize_restoration(position)
                else:
                    self.log_result(
                        "Restore Default Prize", 
                        False, 
                        f"Unexpected response message: {message}"
                    )
            elif response.status_code == 400:
                self.log_result(
                    "Restore Default Prize", 
                    False, 
                    "Bad request - invalid position",
                    f"Response: {response.text}"
                )
            elif response.status_code == 403:
                self.log_result(
                    "Restore Default Prize", 
                    False, 
                    "Access denied - admin authentication failed",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Restore Default Prize", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Restore Default Prize", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def verify_prize_restoration(self, position: int):
        """Verify that prize was restored to default"""
        print(f"\n🔍 Verifying Prize {position} Restoration...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/admin/prizes", headers=headers)
            
            if response.status_code == 200:
                prizes = response.json()
                restored_prize = next((p for p in prizes if p["position"] == position), None)
                
                if restored_prize:
                    if restored_prize.get("is_custom", True) == False:
                        self.log_result(
                            "Verify Prize Restoration", 
                            True, 
                            f"Prize {position} correctly restored to default (is_custom: false)"
                        )
                    else:
                        self.log_result(
                            "Verify Prize Restoration", 
                            False, 
                            f"Prize {position} still marked as custom after restoration"
                        )
                else:
                    self.log_result(
                        "Verify Prize Restoration", 
                        False, 
                        f"Prize {position} not found after restoration"
                    )
            else:
                self.log_result(
                    "Verify Prize Restoration", 
                    False, 
                    f"Failed to retrieve prizes for verification: {response.status_code}"
                )
        except Exception as e:
            self.log_result(
                "Verify Prize Restoration", 
                False, 
                f"Verification request failed: {str(e)}"
            )
    
    def test_upload_prize_image(self):
        """Test POST /api/admin/prizes/upload-image - Upload image for prizes"""
        print("\n📸 Testing Admin Prize Editor - Upload Prize Image...")
        
        if not self.admin_token:
            self.log_result("Upload Prize Image", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create a test image
        try:
            img = Image.new('RGB', (400, 300), color='gold')
            img_buffer = BytesIO()
            img.save(img_buffer, format='JPEG')
            test_image_data = img_buffer.getvalue()
            
            files = {
                'photo': ('prize_image.jpg', BytesIO(test_image_data), 'image/jpeg')
            }
            
            response = requests.post(
                f"{API_BASE}/admin/prizes/upload-image",
                files=files,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                image_url = data.get("image_url")
                message = data.get("message", "")
                
                if image_url and image_url.startswith("data:image"):
                    self.log_result(
                        "Upload Prize Image", 
                        True, 
                        f"Prize image uploaded successfully: {message}"
                    )
                else:
                    self.log_result(
                        "Upload Prize Image", 
                        False, 
                        "Image uploaded but invalid image_url format",
                        f"Response: {data}"
                    )
            elif response.status_code == 400:
                self.log_result(
                    "Upload Prize Image", 
                    False, 
                    "Bad request - invalid image format",
                    f"Response: {response.text}"
                )
            elif response.status_code == 403:
                self.log_result(
                    "Upload Prize Image", 
                    False, 
                    "Access denied - admin authentication failed",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Upload Prize Image", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Upload Prize Image", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    # ===== DIGITAL CLUB CARD TESTS =====
    
    def test_get_club_card(self):
        """Test GET /api/club-card - Get personal club card data"""
        print("\n💳 Testing Digital Club Card - Get Personal Card...")
        
        if not self.regular_user_token:
            self.log_result("Get Club Card", False, "No regular user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.regular_user_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/club-card", headers=headers)
            
            if response.status_code == 200:
                card_data = response.json()
                required_fields = ["name", "username", "club_card_code", "club_card_qr_url", "level", "total_points"]
                missing_fields = [field for field in required_fields if field not in card_data]
                
                if not missing_fields:
                    club_code = card_data.get("club_card_code", "")
                    qr_url = card_data.get("club_card_qr_url", "")
                    
                    # Verify DP-XXXX format
                    if club_code.startswith("DP-") and len(club_code) == 7:
                        # Verify QR URL format
                        if "desideridipuglia.com/club/user/" in qr_url:
                            self.log_result(
                                "Get Club Card", 
                                True, 
                                f"Club card retrieved successfully: {club_code}, Level: {card_data['level']}, Points: {card_data['total_points']}"
                            )
                        else:
                            self.log_result(
                                "Get Club Card", 
                                False, 
                                f"Invalid QR URL format: {qr_url}"
                            )
                    else:
                        self.log_result(
                            "Get Club Card", 
                            False, 
                            f"Invalid club card code format: {club_code} (expected DP-XXXX)"
                        )
                else:
                    self.log_result(
                        "Get Club Card", 
                        False, 
                        f"Club card missing required fields: {missing_fields}",
                        f"Response: {card_data}"
                    )
            elif response.status_code == 401:
                self.log_result(
                    "Get Club Card", 
                    False, 
                    "Authentication failed - invalid user token",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Get Club Card", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Get Club Card", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_get_qr_public_access(self):
        """Test GET /api/club-card/qr/{user_id} - Public QR code access"""
        print("\n🔗 Testing Digital Club Card - Public QR Access...")
        
        if not self.test_user_id:
            self.log_result("Get QR Public Access", False, "No test user ID available")
            return
        
        try:
            # No authentication required for public QR endpoint
            response = requests.get(f"{API_BASE}/club-card/qr/{self.test_user_id}")
            
            if response.status_code == 200:
                qr_data = response.json()
                required_fields = ["name", "username", "level", "total_points", "club_member"]
                missing_fields = [field for field in required_fields if field not in qr_data]
                
                if not missing_fields:
                    if qr_data.get("club_member", False) == True:
                        self.log_result(
                            "Get QR Public Access", 
                            True, 
                            f"Public QR access working: {qr_data['name']} ({qr_data['username']}) - {qr_data['level']}"
                        )
                    else:
                        self.log_result(
                            "Get QR Public Access", 
                            False, 
                            "User not marked as club member in QR response"
                        )
                else:
                    self.log_result(
                        "Get QR Public Access", 
                        False, 
                        f"QR data missing required fields: {missing_fields}",
                        f"Response: {qr_data}"
                    )
            elif response.status_code == 404:
                self.log_result(
                    "Get QR Public Access", 
                    False, 
                    "User not found for QR access",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Get QR Public Access", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Get QR Public Access", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_club_card_initialization(self):
        """Test automatic club card initialization for new users"""
        print("\n🆕 Testing Digital Club Card - Auto Initialization...")
        
        # This test verifies that existing users have club card data
        # In a real scenario, this would test new user registration
        
        if not self.regular_user_token:
            self.log_result("Club Card Initialization", False, "No regular user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.regular_user_token}"}
        
        try:
            # Get user profile to check club card fields
            response = requests.get(f"{API_BASE}/user/profile", headers=headers)
            
            if response.status_code == 200:
                profile = response.json()
                
                # Check if user has club card data through club-card endpoint
                card_response = requests.get(f"{API_BASE}/club-card", headers=headers)
                
                if card_response.status_code == 200:
                    card_data = card_response.json()
                    
                    if (card_data.get("club_card_code") and 
                        card_data.get("club_card_qr_url") and 
                        card_data.get("join_date")):
                        self.log_result(
                            "Club Card Initialization", 
                            True, 
                            f"Club card properly initialized: {card_data['club_card_code']}"
                        )
                    else:
                        self.log_result(
                            "Club Card Initialization", 
                            False, 
                            "Club card data incomplete after initialization",
                            f"Card data: {card_data}"
                        )
                else:
                    self.log_result(
                        "Club Card Initialization", 
                        False, 
                        f"Failed to get club card data: {card_response.status_code}"
                    )
            else:
                self.log_result(
                    "Club Card Initialization", 
                    False, 
                    f"Failed to get user profile: {response.status_code}"
                )
        except Exception as e:
            self.log_result(
                "Club Card Initialization", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    # ===== MULTILINGUAL SUPPORT TESTS =====
    
    def test_get_translations_italian(self):
        """Test GET /api/translations?language=it - Italian translations"""
        print("\n🇮🇹 Testing Multilingual Support - Italian Translations...")
        
        try:
            response = requests.get(f"{API_BASE}/translations?language=it")
            
            if response.status_code == 200:
                translations = response.json()
                
                if isinstance(translations, dict) and len(translations) > 0:
                    # Check for some expected Italian translations
                    expected_keys = ["home", "leaderboard", "prizes", "missions", "profile"]
                    found_keys = [key for key in expected_keys if key in translations]
                    
                    if len(found_keys) >= 3:  # At least 3 expected keys found
                        # Check Italian content
                        italian_indicators = ["Classifica", "Premi", "Missioni", "Profilo"]
                        italian_found = any(indicator in str(translations.values()) for indicator in italian_indicators)
                        
                        if italian_found:
                            self.log_result(
                                "Get Italian Translations", 
                                True, 
                                f"Italian translations retrieved successfully: {len(translations)} keys, includes: {found_keys}"
                            )
                        else:
                            self.log_result(
                                "Get Italian Translations", 
                                False, 
                                "Translations retrieved but don't appear to be in Italian",
                                f"Sample translations: {dict(list(translations.items())[:3])}"
                            )
                    else:
                        self.log_result(
                            "Get Italian Translations", 
                            False, 
                            f"Missing expected translation keys. Found: {found_keys}, Expected: {expected_keys}"
                        )
                else:
                    self.log_result(
                        "Get Italian Translations", 
                        False, 
                        f"Invalid translations format. Expected dict, got: {type(translations)}"
                    )
            else:
                self.log_result(
                    "Get Italian Translations", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Get Italian Translations", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_get_translations_english(self):
        """Test GET /api/translations?language=en - English translations"""
        print("\n🇬🇧 Testing Multilingual Support - English Translations...")
        
        try:
            response = requests.get(f"{API_BASE}/translations?language=en")
            
            if response.status_code == 200:
                translations = response.json()
                
                if isinstance(translations, dict) and len(translations) > 0:
                    # Check for some expected English translations
                    expected_keys = ["home", "leaderboard", "prizes", "missions", "profile"]
                    found_keys = [key for key in expected_keys if key in translations]
                    
                    if len(found_keys) >= 3:  # At least 3 expected keys found
                        # Check English content
                        english_indicators = ["Leaderboard", "Prizes", "Missions", "Profile"]
                        english_found = any(indicator in str(translations.values()) for indicator in english_indicators)
                        
                        if english_found:
                            self.log_result(
                                "Get English Translations", 
                                True, 
                                f"English translations retrieved successfully: {len(translations)} keys, includes: {found_keys}"
                            )
                        else:
                            self.log_result(
                                "Get English Translations", 
                                False, 
                                "Translations retrieved but don't appear to be in English",
                                f"Sample translations: {dict(list(translations.items())[:3])}"
                            )
                    else:
                        self.log_result(
                            "Get English Translations", 
                            False, 
                            f"Missing expected translation keys. Found: {found_keys}, Expected: {expected_keys}"
                        )
                else:
                    self.log_result(
                        "Get English Translations", 
                        False, 
                        f"Invalid translations format. Expected dict, got: {type(translations)}"
                    )
            else:
                self.log_result(
                    "Get English Translations", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Get English Translations", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_update_user_language(self):
        """Test PUT /api/user/language - Update user language preference"""
        print("\n🔄 Testing Multilingual Support - Update User Language...")
        
        if not self.regular_user_token:
            self.log_result("Update User Language", False, "No regular user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.regular_user_token}"}
        
        # Test updating to English
        try:
            response = requests.put(
                f"{API_BASE}/user/language",
                json={"language": "en"},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                if "English" in message or "aggiornata" in message:
                    self.log_result(
                        "Update User Language to EN", 
                        True, 
                        f"Language updated to English: {message}"
                    )
                    
                    # Test updating back to Italian
                    self.test_update_language_italian(headers)
                else:
                    self.log_result(
                        "Update User Language to EN", 
                        False, 
                        f"Unexpected response message: {message}"
                    )
            elif response.status_code == 400:
                self.log_result(
                    "Update User Language to EN", 
                    False, 
                    "Bad request - invalid language parameter",
                    f"Response: {response.text}"
                )
            elif response.status_code == 401:
                self.log_result(
                    "Update User Language to EN", 
                    False, 
                    "Authentication failed - invalid user token",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Update User Language to EN", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Update User Language to EN", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_update_language_italian(self, headers):
        """Test updating language back to Italian"""
        print("\n🇮🇹 Testing Language Update - Back to Italian...")
        
        try:
            response = requests.put(
                f"{API_BASE}/user/language",
                json={"language": "it"},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                if "Italiano" in message or "aggiornata" in message:
                    self.log_result(
                        "Update User Language to IT", 
                        True, 
                        f"Language updated back to Italian: {message}"
                    )
                else:
                    self.log_result(
                        "Update User Language to IT", 
                        False, 
                        f"Unexpected response message: {message}"
                    )
            else:
                self.log_result(
                    "Update User Language to IT", 
                    False, 
                    f"Failed to update language back to Italian: {response.status_code}"
                )
        except Exception as e:
            self.log_result(
                "Update User Language to IT", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_get_admin_translations(self):
        """Test GET /api/admin/translations - Admin translation management"""
        print("\n⚙️ Testing Multilingual Support - Admin Translation Management...")
        
        if not self.admin_token:
            self.log_result("Get Admin Translations", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/admin/translations", headers=headers)
            
            if response.status_code == 200:
                translations = response.json()
                
                if isinstance(translations, list):
                    if len(translations) > 0:
                        # Check structure of translation objects
                        translation = translations[0]
                        required_fields = ["id", "key", "italian", "english", "category"]
                        missing_fields = [field for field in required_fields if field not in translation]
                        
                        if not missing_fields:
                            self.log_result(
                                "Get Admin Translations", 
                                True, 
                                f"Admin translations retrieved successfully: {len(translations)} translation entries"
                            )
                        else:
                            self.log_result(
                                "Get Admin Translations", 
                                False, 
                                f"Translation objects missing required fields: {missing_fields}",
                                f"Sample translation: {translation}"
                            )
                    else:
                        self.log_result(
                            "Get Admin Translations", 
                            True, 
                            "No translations found (this is normal if no custom translations exist)"
                        )
                else:
                    self.log_result(
                        "Get Admin Translations", 
                        False, 
                        f"Invalid response format. Expected list, got: {type(translations)}"
                    )
            elif response.status_code == 403:
                self.log_result(
                    "Get Admin Translations", 
                    False, 
                    "Access denied - admin authentication failed",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Get Admin Translations", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Get Admin Translations", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_create_admin_translation(self):
        """Test POST /api/admin/translations - Create/update translation"""
        print("\n➕ Testing Multilingual Support - Create Admin Translation...")
        
        if not self.admin_token:
            self.log_result("Create Admin Translation", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        translation_data = {
            "key": "test_phase4_message",
            "italian": "Fase 4 completata con successo!",
            "english": "Phase 4 completed successfully!",
            "category": "testing"
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/admin/translations",
                json=translation_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                if "salvata" in message or "saved" in message.lower():
                    self.log_result(
                        "Create Admin Translation", 
                        True, 
                        f"Translation created successfully: {message}"
                    )
                    
                    # Verify the translation was created
                    self.verify_translation_created(translation_data["key"])
                else:
                    self.log_result(
                        "Create Admin Translation", 
                        False, 
                        f"Unexpected response message: {message}"
                    )
            elif response.status_code == 400:
                self.log_result(
                    "Create Admin Translation", 
                    False, 
                    "Bad request - invalid translation data",
                    f"Response: {response.text}"
                )
            elif response.status_code == 403:
                self.log_result(
                    "Create Admin Translation", 
                    False, 
                    "Access denied - admin authentication failed",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Create Admin Translation", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Create Admin Translation", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def verify_translation_created(self, translation_key: str):
        """Verify that translation was created correctly"""
        print(f"\n🔍 Verifying Translation Creation: {translation_key}...")
        
        try:
            # Check Italian translation
            it_response = requests.get(f"{API_BASE}/translations?language=it")
            en_response = requests.get(f"{API_BASE}/translations?language=en")
            
            if it_response.status_code == 200 and en_response.status_code == 200:
                it_translations = it_response.json()
                en_translations = en_response.json()
                
                if (translation_key in it_translations and 
                    translation_key in en_translations and
                    it_translations[translation_key] == "Fase 4 completata con successo!" and
                    en_translations[translation_key] == "Phase 4 completed successfully!"):
                    self.log_result(
                        "Verify Translation Created", 
                        True, 
                        f"Translation '{translation_key}' correctly created and accessible in both languages"
                    )
                else:
                    self.log_result(
                        "Verify Translation Created", 
                        False, 
                        f"Translation '{translation_key}' not found or incorrect in language endpoints"
                    )
            else:
                self.log_result(
                    "Verify Translation Created", 
                    False, 
                    f"Failed to retrieve translations for verification: IT:{it_response.status_code}, EN:{en_response.status_code}"
                )
        except Exception as e:
            self.log_result(
                "Verify Translation Created", 
                False, 
                f"Verification request failed: {str(e)}"
            )
    
    # ===== AUTHENTICATION TESTS =====
    
    def test_authentication_enforcement(self):
        """Test authentication requirements for all endpoints"""
        print("\n🔒 Testing Authentication Enforcement...")
        
        # Test admin endpoints without authentication
        admin_endpoints = [
            "/admin/prizes",
            "/admin/translations"
        ]
        
        for endpoint in admin_endpoints:
            try:
                response = requests.get(f"{API_BASE}{endpoint}")
                if response.status_code in [401, 403]:
                    self.log_result(
                        f"Auth Test - {endpoint}", 
                        True, 
                        f"Correctly rejected unauthenticated request (HTTP {response.status_code})"
                    )
                else:
                    self.log_result(
                        f"Auth Test - {endpoint}", 
                        False, 
                        f"Should have returned 401/403, got {response.status_code}"
                    )
            except Exception as e:
                self.log_result(
                    f"Auth Test - {endpoint}", 
                    False, 
                    f"Request failed: {str(e)}"
                )
        
        # Test user endpoints without authentication
        user_endpoints = [
            "/club-card",
            "/user/language"
        ]
        
        for endpoint in user_endpoints:
            try:
                if endpoint == "/user/language":
                    response = requests.put(f"{API_BASE}{endpoint}", json={"language": "en"})
                else:
                    response = requests.get(f"{API_BASE}{endpoint}")
                
                if response.status_code in [401, 403]:
                    self.log_result(
                        f"Auth Test - {endpoint}", 
                        True, 
                        f"Correctly rejected unauthenticated request (HTTP {response.status_code})"
                    )
                else:
                    self.log_result(
                        f"Auth Test - {endpoint}", 
                        False, 
                        f"Should have returned 401/403, got {response.status_code}"
                    )
            except Exception as e:
                self.log_result(
                    f"Auth Test - {endpoint}", 
                    False, 
                    f"Request failed: {str(e)}"
                )
        
        # Test admin endpoints with regular user token
        if self.regular_user_token:
            headers = {"Authorization": f"Bearer {self.regular_user_token}"}
            
            for endpoint in admin_endpoints:
                try:
                    response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
                    if response.status_code == 403:
                        self.log_result(
                            f"Admin Access Test - {endpoint}", 
                            True, 
                            "Correctly rejected regular user access to admin endpoint"
                        )
                    else:
                        self.log_result(
                            f"Admin Access Test - {endpoint}", 
                            False, 
                            f"Should have returned 403, got {response.status_code}"
                        )
                except Exception as e:
                    self.log_result(
                        f"Admin Access Test - {endpoint}", 
                        False, 
                        f"Request failed: {str(e)}"
                    )
    
    def run_all_tests(self):
        """Run all Phase 4 tests"""
        print("🚀 Starting Phase 4 Backend Tests...")
        print("Testing: Admin Prize Editor + Digital Club Card + Multilingual Support")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users. Aborting tests.")
            return
        
        # Run tests in priority order
        print("\n🏆 ADMIN PRIZE EDITOR SYSTEM TESTS:")
        self.test_get_admin_prizes()
        self.test_update_prize()
        self.test_restore_default_prize()
        self.test_upload_prize_image()
        
        print("\n💳 DIGITAL CLUB CARD SYSTEM TESTS:")
        self.test_get_club_card()
        self.test_get_qr_public_access()
        self.test_club_card_initialization()
        
        print("\n🌐 MULTILINGUAL SUPPORT TESTS:")
        self.test_get_translations_italian()
        self.test_get_translations_english()
        self.test_update_user_language()
        self.test_get_admin_translations()
        self.test_create_admin_translation()
        
        print("\n🔒 AUTHENTICATION TESTS:")
        self.test_authentication_enforcement()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 PHASE 4 BACKEND TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if "✅ PASS" in result["status"])
        failed = sum(1 for result in self.test_results if "❌ FAIL" in result["status"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0%")
        
        # Categorize results
        prize_tests = [r for r in self.test_results if "Prize" in r["test"]]
        card_tests = [r for r in self.test_results if "Club Card" in r["test"] or "QR" in r["test"]]
        translation_tests = [r for r in self.test_results if "Translation" in r["test"] or "Language" in r["test"]]
        auth_tests = [r for r in self.test_results if "Auth" in r["test"]]
        
        print(f"\n📊 BY CATEGORY:")
        print(f"Prize Editor: {sum(1 for r in prize_tests if '✅' in r['status'])}/{len(prize_tests)} passed")
        print(f"Club Card: {sum(1 for r in card_tests if '✅' in r['status'])}/{len(card_tests)} passed")
        print(f"Multilingual: {sum(1 for r in translation_tests if '✅' in r['status'])}/{len(translation_tests)} passed")
        print(f"Authentication: {sum(1 for r in auth_tests if '✅' in r['status'])}/{len(auth_tests)} passed")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        # Overall assessment
        if failed == 0:
            print("\n🎉 ALL PHASE 4 TESTS PASSED!")
            print("✅ Admin Prize Editor System fully functional")
            print("✅ Digital Club Card System working correctly")
            print("✅ Multilingual Support operational")
            print("✅ Authentication properly enforced")
        elif passed > failed:
            print(f"\n⚠️  MOSTLY WORKING: {passed}/{total} tests passed. Some Phase 4 features need attention.")
        else:
            print(f"\n🚨 CRITICAL PHASE 4 ISSUES: {failed}/{total} tests failed. Phase 4 implementation needs fixes.")

if __name__ == "__main__":
    tester = Phase4Tester()
    tester.run_all_tests()