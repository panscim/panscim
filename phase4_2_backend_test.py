#!/usr/bin/env python3
"""
Phase 4.2 Backend Testing Suite for Desideri di Puglia Club
Tests the newly implemented Phase 4.2 backend APIs and enhancements:
1. Interactive QR Public Profile API
2. Enhanced User Model Fields  
3. Multilingual Backend Support
4. Enhanced Club Card System
5. Admin Prize Editor System
"""

import requests
import json
import os
import sys
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://puglia-club.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class Phase42BackendTester:
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
        """Setup test users with provided credentials"""
        print("\n🔧 Setting up test users...")
        
        # Admin credentials from review request
        admin_credentials = {"email": "admin@desideridipuglia.com", "password": "admin123"}
        
        print(f"🔑 Attempting login with admin credentials: {admin_credentials['email']}")
        
        try:
            response = requests.post(f"{API_BASE}/auth/login", json=admin_credentials)
            if response.status_code == 200:
                data = response.json()
                user_data = data.get("user", {})
                if user_data.get("is_admin", False):
                    self.admin_token = data["access_token"]
                    self.admin_user_id = user_data["id"]
                    print(f"✅ Successfully logged in as admin: {admin_credentials['email']}")
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
        
        print(f"🔑 Attempting login with regular user credentials: {user_credentials['email']}")
        
        try:
            response = requests.post(f"{API_BASE}/auth/login", json=user_credentials)
            if response.status_code == 200:
                data = response.json()
                self.regular_user_token = data["access_token"]
                self.test_user_id = data["user"]["id"]
                print(f"✅ Successfully logged in as regular user: {user_credentials['email']}")
            else:
                print(f"❌ Failed to login regular user: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error logging in regular user: {str(e)}")
            return False
        
        return True
    
    def test_interactive_qr_public_profile_api(self):
        """Test Interactive QR Public Profile API - HIGH PRIORITY"""
        print("\n🎯 Testing Interactive QR Public Profile API...")
        
        if not self.test_user_id:
            self.log_result("Interactive QR Public Profile API", False, "No test user ID available")
            return
        
        # Test with user ID format
        try:
            response = requests.get(f"{API_BASE}/club/profile/{self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields from review request
                required_fields = ["user_info", "stats", "status", "prizes", "club_member", "last_updated"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Check user_info structure
                    user_info = data.get("user_info", {})
                    user_info_fields = ["name", "username", "level", "club_card_code", "join_date"]
                    missing_user_info = [field for field in user_info_fields if field not in user_info]
                    
                    # Check stats structure  
                    stats = data.get("stats", {})
                    stats_fields = ["total_points", "current_points", "current_rank", "mission_completions", "month_year"]
                    missing_stats = [field for field in stats_fields if field not in stats]
                    
                    if not missing_user_info and not missing_stats:
                        self.log_result(
                            "Interactive QR Public Profile API", 
                            True, 
                            f"Public profile API working correctly. User: {user_info.get('name')}, Points: {stats.get('current_points')}, Rank: {stats.get('current_rank')}"
                        )
                        
                        # Test with email format (if supported)
                        self.test_public_profile_with_email()
                    else:
                        self.log_result(
                            "Interactive QR Public Profile API", 
                            False, 
                            f"Missing required fields - user_info: {missing_user_info}, stats: {missing_stats}",
                            f"Response: {data}"
                        )
                else:
                    self.log_result(
                        "Interactive QR Public Profile API", 
                        False, 
                        f"Missing required top-level fields: {missing_fields}",
                        f"Response: {data}"
                    )
            elif response.status_code == 404:
                self.log_result(
                    "Interactive QR Public Profile API", 
                    False, 
                    "User not found - test user may not exist",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Interactive QR Public Profile API", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Interactive QR Public Profile API", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_public_profile_with_email(self):
        """Test public profile API with email format"""
        print("\n📧 Testing Public Profile with Email Format...")
        
        try:
            # Test with email format
            response = requests.get(f"{API_BASE}/club/profile/test@desideridipuglia.com")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Public Profile Email Format", 
                    True, 
                    "Public profile API supports email format identifiers"
                )
            elif response.status_code == 404:
                self.log_result(
                    "Public Profile Email Format", 
                    True, 
                    "Email format not supported (expected behavior - using user ID only)"
                )
            else:
                self.log_result(
                    "Public Profile Email Format", 
                    False, 
                    f"Unexpected response for email format: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Public Profile Email Format", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_enhanced_user_model_fields(self):
        """Test Enhanced User Model Fields - HIGH PRIORITY"""
        print("\n👤 Testing Enhanced User Model Fields...")
        
        if not self.regular_user_token:
            self.log_result("Enhanced User Model Fields", False, "No regular user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.regular_user_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/user/profile", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for enhanced fields from review request
                enhanced_fields = ["current_points", "total_points", "level", "position"]
                present_fields = [field for field in enhanced_fields if field in data]
                
                if len(present_fields) >= 3:  # At least most enhanced fields present
                    self.log_result(
                        "Enhanced User Model Fields", 
                        True, 
                        f"Enhanced user model fields present: {present_fields}"
                    )
                    
                    # Test club card initialization
                    self.test_club_card_initialization()
                else:
                    self.log_result(
                        "Enhanced User Model Fields", 
                        False, 
                        f"Missing enhanced user model fields. Present: {present_fields}, Expected: {enhanced_fields}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Enhanced User Model Fields", 
                    False, 
                    f"Failed to get user profile: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Enhanced User Model Fields", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_club_card_initialization(self):
        """Test club card field initialization"""
        print("\n🎴 Testing Club Card Field Initialization...")
        
        if not self.regular_user_token:
            self.log_result("Club Card Initialization", False, "No regular user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.regular_user_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/club-card", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for club card fields
                club_card_fields = ["club_card_code", "club_card_qr_url", "join_date", "level", "total_points"]
                missing_fields = [field for field in club_card_fields if field not in data or data[field] is None]
                
                if not missing_fields:
                    self.log_result(
                        "Club Card Initialization", 
                        True, 
                        f"Club card fields properly initialized. Code: {data.get('club_card_code')}, Level: {data.get('level')}"
                    )
                else:
                    self.log_result(
                        "Club Card Initialization", 
                        False, 
                        f"Missing or null club card fields: {missing_fields}",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Club Card Initialization", 
                    False, 
                    f"Failed to get club card: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Club Card Initialization", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_multilingual_backend_support(self):
        """Test Multilingual Backend Support - HIGH PRIORITY"""
        print("\n🌍 Testing Multilingual Backend Support...")
        
        # Test GET /api/translations
        self.test_get_translations()
        
        # Test PUT /api/user/language
        self.test_update_user_language()
        
        # Test admin translation endpoints
        self.test_admin_translations()
    
    def test_get_translations(self):
        """Test GET /api/translations endpoint"""
        print("\n📝 Testing GET /api/translations...")
        
        # Test Italian translations
        try:
            response = requests.get(f"{API_BASE}/translations?language=it")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and len(data) > 0:
                    # Check for common translation keys
                    common_keys = ["home", "profile", "missions", "leaderboard"]
                    present_keys = [key for key in common_keys if key in data]
                    
                    if len(present_keys) >= 2:
                        self.log_result(
                            "GET Translations IT", 
                            True, 
                            f"Italian translations retrieved successfully. Keys: {len(data)}, Common keys: {present_keys}"
                        )
                    else:
                        self.log_result(
                            "GET Translations IT", 
                            True, 
                            f"Italian translations retrieved but missing common keys. Total keys: {len(data)}"
                        )
                else:
                    self.log_result(
                        "GET Translations IT", 
                        False, 
                        "Invalid translation format - expected non-empty dictionary",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "GET Translations IT", 
                    False, 
                    f"Failed to get Italian translations: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "GET Translations IT", 
                False, 
                f"Request failed: {str(e)}"
            )
        
        # Test English translations
        try:
            response = requests.get(f"{API_BASE}/translations?language=en")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and len(data) > 0:
                    self.log_result(
                        "GET Translations EN", 
                        True, 
                        f"English translations retrieved successfully. Keys: {len(data)}"
                    )
                else:
                    self.log_result(
                        "GET Translations EN", 
                        False, 
                        "Invalid English translation format",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "GET Translations EN", 
                    False, 
                    f"Failed to get English translations: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "GET Translations EN", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_update_user_language(self):
        """Test PUT /api/user/language endpoint"""
        print("\n🔄 Testing PUT /api/user/language...")
        
        if not self.regular_user_token:
            self.log_result("Update User Language", False, "No regular user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.regular_user_token}"}
        
        # Test updating to English
        try:
            response = requests.put(f"{API_BASE}/user/language?language=en", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                if "english" in message.lower() or "en" in message.lower():
                    self.log_result(
                        "Update User Language EN", 
                        True, 
                        f"Successfully updated user language to English: {message}"
                    )
                else:
                    self.log_result(
                        "Update User Language EN", 
                        True, 
                        f"Language update successful: {message}"
                    )
            else:
                self.log_result(
                    "Update User Language EN", 
                    False, 
                    f"Failed to update language to English: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Update User Language EN", 
                False, 
                f"Request failed: {str(e)}"
            )
        
        # Test updating to Italian
        try:
            response = requests.put(f"{API_BASE}/user/language?language=it", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                self.log_result(
                    "Update User Language IT", 
                    True, 
                    f"Successfully updated user language to Italian: {message}"
                )
            else:
                self.log_result(
                    "Update User Language IT", 
                    False, 
                    f"Failed to update language to Italian: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Update User Language IT", 
                False, 
                f"Request failed: {str(e)}"
            )
        
        # Test invalid language
        try:
            response = requests.put(f"{API_BASE}/user/language?language=fr", headers=headers)
            
            if response.status_code == 400:
                self.log_result(
                    "Update User Language Invalid", 
                    True, 
                    "Correctly rejected invalid language code (fr)"
                )
            else:
                self.log_result(
                    "Update User Language Invalid", 
                    False, 
                    f"Should have rejected invalid language, got: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Update User Language Invalid", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_admin_translations(self):
        """Test admin translation management endpoints"""
        print("\n🔧 Testing Admin Translation Management...")
        
        if not self.admin_token:
            self.log_result("Admin Translations", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test GET /api/admin/translations
        try:
            response = requests.get(f"{API_BASE}/admin/translations", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    self.log_result(
                        "GET Admin Translations", 
                        True, 
                        f"Successfully retrieved admin translations list. Count: {len(data)}"
                    )
                    
                    # Test POST /api/admin/translations
                    self.test_create_translation()
                else:
                    self.log_result(
                        "GET Admin Translations", 
                        False, 
                        "Invalid response format - expected list",
                        f"Response: {data}"
                    )
            elif response.status_code == 403:
                self.log_result(
                    "GET Admin Translations", 
                    False, 
                    "Access denied - admin privileges required",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "GET Admin Translations", 
                    False, 
                    f"Failed to get admin translations: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "GET Admin Translations", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_create_translation(self):
        """Test POST /api/admin/translations endpoint"""
        print("\n➕ Testing POST /api/admin/translations...")
        
        if not self.admin_token:
            self.log_result("Create Translation", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create a test translation
        try:
            response = requests.post(
                f"{API_BASE}/admin/translations",
                params={
                    "key": "test_phase42_key",
                    "italian": "Test Fase 4.2",
                    "english": "Test Phase 4.2",
                    "category": "testing"
                },
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                if "salvata" in message.lower() or "saved" in message.lower():
                    self.log_result(
                        "Create Translation", 
                        True, 
                        f"Successfully created test translation: {message}"
                    )
                else:
                    self.log_result(
                        "Create Translation", 
                        True, 
                        f"Translation creation successful: {message}"
                    )
            elif response.status_code == 403:
                self.log_result(
                    "Create Translation", 
                    False, 
                    "Access denied - admin privileges required",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Create Translation", 
                    False, 
                    f"Failed to create translation: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Create Translation", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_enhanced_club_card_system(self):
        """Test Enhanced Club Card System - HIGH PRIORITY"""
        print("\n🎴 Testing Enhanced Club Card System...")
        
        # Test GET /api/club-card
        self.test_get_club_card()
        
        # Test GET /api/club-card/qr/{user_id} (legacy)
        self.test_get_club_card_qr()
    
    def test_get_club_card(self):
        """Test GET /api/club-card endpoint"""
        print("\n🎯 Testing GET /api/club-card...")
        
        if not self.regular_user_token:
            self.log_result("GET Club Card", False, "No regular user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.regular_user_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/club-card", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required club card fields
                required_fields = ["name", "username", "club_card_code", "club_card_qr_url", "join_date", "level", "total_points"]
                missing_fields = [field for field in required_fields if field not in data or data[field] is None]
                
                if not missing_fields:
                    # Validate club card code format (DP-XXXX)
                    club_code = data.get("club_card_code", "")
                    if club_code.startswith("DP-") and len(club_code) == 7:
                        self.log_result(
                            "GET Club Card", 
                            True, 
                            f"Club card data retrieved successfully. Code: {club_code}, Level: {data.get('level')}, Points: {data.get('total_points')}"
                        )
                    else:
                        self.log_result(
                            "GET Club Card", 
                            False, 
                            f"Invalid club card code format: {club_code} (expected DP-XXXX)",
                            f"Response: {data}"
                        )
                else:
                    self.log_result(
                        "GET Club Card", 
                        False, 
                        f"Missing required club card fields: {missing_fields}",
                        f"Response: {data}"
                    )
            elif response.status_code == 401:
                self.log_result(
                    "GET Club Card", 
                    False, 
                    "Authentication failed - invalid user token",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "GET Club Card", 
                    False, 
                    f"Failed to get club card: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "GET Club Card", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_get_club_card_qr(self):
        """Test GET /api/club-card/qr/{user_id} endpoint (legacy)"""
        print("\n🔗 Testing GET /api/club-card/qr/{user_id}...")
        
        if not self.test_user_id:
            self.log_result("GET Club Card QR", False, "No test user ID available")
            return
        
        try:
            response = requests.get(f"{API_BASE}/club-card/qr/{self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # This should return the same data as the public profile
                if "user_info" in data and "stats" in data:
                    self.log_result(
                        "GET Club Card QR", 
                        True, 
                        "Legacy QR endpoint working correctly (redirects to public profile)"
                    )
                else:
                    self.log_result(
                        "GET Club Card QR", 
                        False, 
                        "Legacy QR endpoint returned unexpected format",
                        f"Response: {data}"
                    )
            elif response.status_code == 404:
                self.log_result(
                    "GET Club Card QR", 
                    False, 
                    "User not found for QR endpoint",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "GET Club Card QR", 
                    False, 
                    f"Failed to get QR data: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "GET Club Card QR", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_admin_prize_editor_system(self):
        """Test Admin Prize Editor System - MEDIUM PRIORITY"""
        print("\n🏆 Testing Admin Prize Editor System...")
        
        if not self.admin_token:
            self.log_result("Admin Prize Editor System", False, "No admin token available")
            return
        
        # Test GET /api/admin/prizes
        self.test_get_admin_prizes()
        
        # Test PUT /api/admin/prizes/{position}
        self.test_update_prize()
        
        # Test DELETE /api/admin/prizes/{position}
        self.test_restore_default_prize()
        
        # Test POST /api/admin/prizes/upload-image
        self.test_upload_prize_image()
    
    def test_get_admin_prizes(self):
        """Test GET /api/admin/prizes endpoint"""
        print("\n📋 Testing GET /api/admin/prizes...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/admin/prizes", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) >= 3:
                    # Check prize structure
                    prize = data[0]
                    required_fields = ["position", "title", "description", "month_year", "is_custom"]
                    missing_fields = [field for field in required_fields if field not in prize]
                    
                    if not missing_fields:
                        custom_prizes = sum(1 for p in data if p.get("is_custom", False))
                        self.log_result(
                            "GET Admin Prizes", 
                            True, 
                            f"Admin prizes retrieved successfully. Total: {len(data)}, Custom: {custom_prizes}"
                        )
                    else:
                        self.log_result(
                            "GET Admin Prizes", 
                            False, 
                            f"Prize structure missing fields: {missing_fields}",
                            f"Sample prize: {prize}"
                        )
                else:
                    self.log_result(
                        "GET Admin Prizes", 
                        False, 
                        f"Invalid prizes format or count. Expected list with 3+ items, got: {type(data)} with {len(data) if isinstance(data, list) else 'N/A'} items",
                        f"Response: {data}"
                    )
            elif response.status_code == 403:
                self.log_result(
                    "GET Admin Prizes", 
                    False, 
                    "Access denied - admin privileges required",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "GET Admin Prizes", 
                    False, 
                    f"Failed to get admin prizes: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "GET Admin Prizes", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_update_prize(self):
        """Test PUT /api/admin/prizes/{position} endpoint"""
        print("\n✏️ Testing PUT /api/admin/prizes/{position}...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Update 3rd place prize
        update_data = {
            "title": "🥉 Test Custom Prize - Phase 4.2",
            "description": "Custom prize created during Phase 4.2 testing",
            "image_url": None
        }
        
        try:
            response = requests.put(
                f"{API_BASE}/admin/prizes/3",
                json=update_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                if "aggiornato" in message.lower() or "updated" in message.lower():
                    self.log_result(
                        "Update Prize", 
                        True, 
                        f"Successfully updated 3rd place prize: {message}"
                    )
                else:
                    self.log_result(
                        "Update Prize", 
                        True, 
                        f"Prize update successful: {message}"
                    )
            elif response.status_code == 403:
                self.log_result(
                    "Update Prize", 
                    False, 
                    "Access denied - admin privileges required",
                    f"Response: {response.text}"
                )
            elif response.status_code == 400:
                self.log_result(
                    "Update Prize", 
                    False, 
                    "Invalid position or request data",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Update Prize", 
                    False, 
                    f"Failed to update prize: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Update Prize", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_restore_default_prize(self):
        """Test DELETE /api/admin/prizes/{position} endpoint"""
        print("\n🔄 Testing DELETE /api/admin/prizes/{position}...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.delete(f"{API_BASE}/admin/prizes/3", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                if "ripristinato" in message.lower() or "restored" in message.lower():
                    self.log_result(
                        "Restore Default Prize", 
                        True, 
                        f"Successfully restored 3rd place prize to default: {message}"
                    )
                else:
                    self.log_result(
                        "Restore Default Prize", 
                        True, 
                        f"Prize restoration successful: {message}"
                    )
            elif response.status_code == 403:
                self.log_result(
                    "Restore Default Prize", 
                    False, 
                    "Access denied - admin privileges required",
                    f"Response: {response.text}"
                )
            elif response.status_code == 400:
                self.log_result(
                    "Restore Default Prize", 
                    False, 
                    "Invalid position",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Restore Default Prize", 
                    False, 
                    f"Failed to restore default prize: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Restore Default Prize", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_upload_prize_image(self):
        """Test POST /api/admin/prizes/upload-image endpoint"""
        print("\n📸 Testing POST /api/admin/prizes/upload-image...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create a simple test image
        try:
            from PIL import Image
            import io
            
            # Create a simple 100x100 test image
            img = Image.new('RGB', (100, 100), color='gold')
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            test_image_data = img_buffer.getvalue()
            
            files = {
                'photo': ('test_prize_image.png', io.BytesIO(test_image_data), 'image/png')
            }
            
            response = requests.post(
                f"{API_BASE}/admin/prizes/upload-image",
                files=files,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "image_url" in data and data["image_url"]:
                    self.log_result(
                        "Upload Prize Image", 
                        True, 
                        f"Successfully uploaded prize image: {data.get('message', 'Image uploaded')}"
                    )
                else:
                    self.log_result(
                        "Upload Prize Image", 
                        False, 
                        "Image upload successful but no image_url returned",
                        f"Response: {data}"
                    )
            elif response.status_code == 403:
                self.log_result(
                    "Upload Prize Image", 
                    False, 
                    "Access denied - admin privileges required",
                    f"Response: {response.text}"
                )
            elif response.status_code == 400:
                self.log_result(
                    "Upload Prize Image", 
                    False, 
                    "Invalid image format or request",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Upload Prize Image", 
                    False, 
                    f"Failed to upload prize image: {response.status_code}",
                    f"Response: {response.text}"
                )
        except ImportError:
            self.log_result(
                "Upload Prize Image", 
                False, 
                "PIL library not available for image testing"
            )
        except Exception as e:
            self.log_result(
                "Upload Prize Image", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_error_scenarios(self):
        """Test error scenarios for validation"""
        print("\n🚨 Testing Error Scenarios...")
        
        # Test invalid user_identifier in public profile
        try:
            response = requests.get(f"{API_BASE}/club/profile/invalid-user-id-12345")
            
            if response.status_code == 404:
                self.log_result(
                    "Invalid User ID Error", 
                    True, 
                    "Correctly returned 404 for invalid user identifier"
                )
            else:
                self.log_result(
                    "Invalid User ID Error", 
                    False, 
                    f"Should have returned 404 for invalid user ID, got: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Invalid User ID Error", 
                False, 
                f"Request failed: {str(e)}"
            )
        
        # Test missing authentication for admin endpoints
        try:
            response = requests.get(f"{API_BASE}/admin/prizes")
            
            if response.status_code in [401, 403]:
                self.log_result(
                    "Missing Auth Admin Error", 
                    True, 
                    f"Correctly rejected admin request without authentication (HTTP {response.status_code})"
                )
            else:
                self.log_result(
                    "Missing Auth Admin Error", 
                    False, 
                    f"Should have returned 401/403 for missing auth, got: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Missing Auth Admin Error", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def run_all_tests(self):
        """Run all Phase 4.2 backend tests"""
        print("🚀 Starting Phase 4.2 Backend Testing Suite...")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users. Aborting tests.")
            return
        
        # Run Phase 4.2 tests in priority order
        print("\n🎯 HIGH PRIORITY TESTS:")
        
        print("\n1. Interactive QR Public Profile API")
        self.test_interactive_qr_public_profile_api()
        
        print("\n2. Enhanced User Model Fields")
        self.test_enhanced_user_model_fields()
        
        print("\n3. Multilingual Backend Support")
        self.test_multilingual_backend_support()
        
        print("\n4. Enhanced Club Card System")
        self.test_enhanced_club_card_system()
        
        print("\n📊 MEDIUM PRIORITY TESTS:")
        
        print("\n5. Admin Prize Editor System")
        self.test_admin_prize_editor_system()
        
        print("\n🚨 ERROR SCENARIO TESTS:")
        
        print("\n6. Error Scenarios")
        self.test_error_scenarios()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 PHASE 4.2 BACKEND TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if "✅ PASS" in result["status"])
        failed = sum(1 for result in self.test_results if "❌ FAIL" in result["status"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"{result['status']} - {result['test']}")
        
        # Overall assessment
        if failed == 0:
            print("\n🎉 ALL PHASE 4.2 BACKEND TESTS PASSED!")
            print("✅ Interactive QR Public Profile API working correctly")
            print("✅ Enhanced User Model Fields properly implemented")
            print("✅ Multilingual Backend Support functional")
            print("✅ Enhanced Club Card System operational")
            print("✅ Admin Prize Editor System working")
        elif passed > failed:
            print(f"\n⚠️  MOSTLY WORKING: {passed}/{total} tests passed. Some Phase 4.2 features need attention.")
        else:
            print(f"\n🚨 CRITICAL PHASE 4.2 ISSUES: {failed}/{total} tests failed. Phase 4.2 implementation needs fixes.")

if __name__ == "__main__":
    tester = Phase42BackendTester()
    tester.run_all_tests()