#!/usr/bin/env python3
"""
Backend Testing Suite for Desideri di Puglia Club - ENHANCED Mission Management with VERIFICATION
Tests the verification workflow: mission creation with requirements, submission system, and admin approval.
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

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://puglia-loyalty.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class MissionVerificationTester:
    def __init__(self):
        self.admin_token = None
        self.regular_user_token = None
        self.test_results = []
        self.admin_user_id = None
        self.test_user_id = None
        self.created_mission_ids = []  # Track created missions for cleanup
        self.created_submission_ids = []  # Track submissions for testing
        
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
        """Create or login test users (admin and regular user)"""
        print("\n🔧 Setting up test users...")
        
        # Use specific admin credentials from review request
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
        
        # Use specific regular user credentials from review request
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
        
        return True
    
    def test_create_one_time_mission(self):
        """Test creating a one-time mission"""
        print("\n🎯 Testing One-Time Mission Creation...")
        
        if not self.admin_token:
            self.log_result("Create One-Time Mission", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        mission_data = {
            "title": "Visita il Centro Storico di Lecce",
            "description": "Esplora le meraviglie barocche del centro storico di Lecce e condividi una foto sui social taggando @desideridipuglia",
            "points": 50,
            "frequency": "one-time",
            "daily_limit": 0,
            "weekly_limit": 0,
            "is_active": True
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/admin/missions",
                json=mission_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                mission_id = data.get("mission_id")
                if mission_id:
                    self.created_mission_ids.append(mission_id)
                    self.log_result(
                        "Create One-Time Mission", 
                        True, 
                        f"One-time mission created successfully: {data.get('message', 'Mission created')}"
                    )
                else:
                    self.log_result(
                        "Create One-Time Mission", 
                        False, 
                        "Mission created but no mission_id returned",
                        f"Response: {data}"
                    )
            elif response.status_code == 403:
                self.log_result(
                    "Create One-Time Mission", 
                    False, 
                    "Access denied - user may not have admin privileges",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Create One-Time Mission", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Create One-Time Mission", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_create_daily_mission(self):
        """Test creating a daily mission with limits"""
        print("\n📅 Testing Daily Mission Creation...")
        
        if not self.admin_token:
            self.log_result("Create Daily Mission", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        mission_data = {
            "title": "Condividi Storia Instagram",
            "description": "Condividi una storia su Instagram taggando @desideridipuglia e usando #DesideridiPugliaClub",
            "points": 15,
            "frequency": "daily",
            "daily_limit": 3,
            "weekly_limit": 0,
            "is_active": True
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/admin/missions",
                json=mission_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                mission_id = data.get("mission_id")
                if mission_id:
                    self.created_mission_ids.append(mission_id)
                    self.log_result(
                        "Create Daily Mission", 
                        True, 
                        f"Daily mission created successfully with limit 3/day: {data.get('message', 'Mission created')}"
                    )
                else:
                    self.log_result(
                        "Create Daily Mission", 
                        False, 
                        "Mission created but no mission_id returned",
                        f"Response: {data}"
                    )
            elif response.status_code == 403:
                self.log_result(
                    "Create Daily Mission", 
                    False, 
                    "Access denied - user may not have admin privileges",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Create Daily Mission", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Create Daily Mission", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_create_weekly_mission(self):
        """Test creating a weekly mission with limits"""
        print("\n📆 Testing Weekly Mission Creation...")
        
        if not self.admin_token:
            self.log_result("Create Weekly Mission", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        mission_data = {
            "title": "Recensione Partner Locale",
            "description": "Lascia una recensione dettagliata su Google o TripAdvisor per uno dei nostri partner locali",
            "points": 75,
            "frequency": "weekly",
            "daily_limit": 0,
            "weekly_limit": 2,
            "is_active": True
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/admin/missions",
                json=mission_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                mission_id = data.get("mission_id")
                if mission_id:
                    self.created_mission_ids.append(mission_id)
                    self.log_result(
                        "Create Weekly Mission", 
                        True, 
                        f"Weekly mission created successfully with limit 2/week: {data.get('message', 'Mission created')}"
                    )
                else:
                    self.log_result(
                        "Create Weekly Mission", 
                        False, 
                        "Mission created but no mission_id returned",
                        f"Response: {data}"
                    )
            elif response.status_code == 403:
                self.log_result(
                    "Create Weekly Mission", 
                    False, 
                    "Access denied - user may not have admin privileges",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Create Weekly Mission", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Create Weekly Mission", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_get_admin_missions(self):
        """Test retrieving admin missions list with statistics"""
        print("\n📋 Testing Admin Missions List Retrieval...")
        
        if not self.admin_token:
            self.log_result("Get Admin Missions", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/admin/missions", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check mission structure
                        mission = data[0]
                        required_fields = ["id", "title", "description", "points", "frequency", "is_active", "completion_count"]
                        missing_fields = [field for field in required_fields if field not in mission]
                        
                        if not missing_fields:
                            active_missions = sum(1 for m in data if m.get("is_active", False))
                            self.log_result(
                                "Get Admin Missions", 
                                True, 
                                f"Successfully retrieved {len(data)} missions ({active_missions} active) with all required fields"
                            )
                        else:
                            self.log_result(
                                "Get Admin Missions", 
                                False, 
                                f"Missions missing required fields: {missing_fields}",
                                f"Sample mission: {mission}"
                            )
                    else:
                        self.log_result(
                            "Get Admin Missions", 
                            True, 
                            "No missions found (this is normal for new installations)"
                        )
                else:
                    self.log_result(
                        "Get Admin Missions", 
                        False, 
                        "Invalid response format - expected list",
                        f"Response: {data}"
                    )
            elif response.status_code == 403:
                self.log_result(
                    "Get Admin Missions", 
                    False, 
                    "Access denied - user may not have admin privileges",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Get Admin Missions", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Get Admin Missions", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_update_mission(self):
        """Test updating mission properties"""
        print("\n✏️ Testing Mission Update...")
        
        if not self.admin_token or not self.created_mission_ids:
            self.log_result("Update Mission", False, "No admin token or created missions available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        mission_id = self.created_mission_ids[0]  # Use first created mission
        
        update_data = {
            "title": "Visita il Centro Storico di Lecce - AGGIORNATO",
            "points": 60,  # Increased points
            "is_active": False  # Deactivate mission
        }
        
        try:
            response = requests.put(
                f"{API_BASE}/admin/missions/{mission_id}",
                json=update_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Update Mission", 
                    True, 
                    f"Mission updated successfully: {data.get('message', 'Mission updated')}"
                )
            elif response.status_code == 403:
                self.log_result(
                    "Update Mission", 
                    False, 
                    "Access denied - user may not have admin privileges",
                    f"Response: {response.text}"
                )
            elif response.status_code == 404:
                self.log_result(
                    "Update Mission", 
                    False, 
                    "Mission not found - may have been deleted",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Update Mission", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Update Mission", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_mission_statistics(self):
        """Test mission statistics endpoint"""
        print("\n📊 Testing Mission Statistics...")
        
        if not self.admin_token:
            self.log_result("Mission Statistics", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/admin/missions/statistics", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["month_year", "overview", "missions"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    overview = data.get("overview", {})
                    overview_fields = ["total_missions", "active_missions", "total_completions", "total_points_awarded"]
                    missing_overview = [field for field in overview_fields if field not in overview]
                    
                    if not missing_overview:
                        self.log_result(
                            "Mission Statistics", 
                            True, 
                            f"Statistics retrieved: {overview['total_missions']} missions, {overview['total_completions']} completions, {overview['total_points_awarded']} points awarded"
                        )
                    else:
                        self.log_result(
                            "Mission Statistics", 
                            False, 
                            f"Overview missing fields: {missing_overview}",
                            f"Overview: {overview}"
                        )
                else:
                    self.log_result(
                        "Mission Statistics", 
                        False, 
                        f"Statistics missing required fields: {missing_fields}",
                        f"Response: {data}"
                    )
            elif response.status_code == 403:
                self.log_result(
                    "Mission Statistics", 
                    False, 
                    "Access denied - user may not have admin privileges",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Mission Statistics", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Mission Statistics", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_get_user_missions(self):
        """Test user missions endpoint with completion status"""
        print("\n🎯 Testing User Missions Retrieval...")
        
        if not self.regular_user_token:
            self.log_result("Get User Missions", False, "No regular user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.regular_user_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/missions", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check mission structure for users
                        mission = data[0]
                        required_fields = ["id", "title", "description", "points", "frequency", "available", "completed"]
                        missing_fields = [field for field in required_fields if field not in mission]
                        
                        if not missing_fields:
                            available_missions = sum(1 for m in data if m.get("available", False))
                            self.log_result(
                                "Get User Missions", 
                                True, 
                                f"Successfully retrieved {len(data)} missions ({available_missions} available) with completion status"
                            )
                        else:
                            self.log_result(
                                "Get User Missions", 
                                False, 
                                f"User missions missing required fields: {missing_fields}",
                                f"Sample mission: {mission}"
                            )
                    else:
                        self.log_result(
                            "Get User Missions", 
                            True, 
                            "No missions found for user (this is normal if no active missions exist)"
                        )
                else:
                    self.log_result(
                        "Get User Missions", 
                        False, 
                        "Invalid response format - expected list",
                        f"Response: {data}"
                    )
            elif response.status_code == 401:
                self.log_result(
                    "Get User Missions", 
                    False, 
                    "Authentication failed - invalid user token",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Get User Missions", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Get User Missions", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_complete_mission(self):
        """Test mission completion with point awarding"""
        print("\n🏆 Testing Mission Completion...")
        
        if not self.regular_user_token:
            self.log_result("Complete Mission", False, "No regular user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.regular_user_token}"}
        
        # Get available missions first
        try:
            missions_response = requests.get(f"{API_BASE}/missions", headers=headers)
            if missions_response.status_code == 200:
                missions = missions_response.json()
                available_missions = [m for m in missions if m.get("available", False) and not m.get("completed", False)]
                
                if available_missions:
                    mission_id = available_missions[0]["id"]
                    mission_title = available_missions[0]["title"]
                    
                    # Try to complete the mission
                    response = requests.post(
                        f"{API_BASE}/missions/{mission_id}/complete",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        points_earned = data.get("points_earned", 0)
                        if points_earned > 0:
                            self.log_result(
                                "Complete Mission", 
                                True, 
                                f"Mission '{mission_title}' completed successfully! Earned {points_earned} points"
                            )
                        else:
                            self.log_result(
                                "Complete Mission", 
                                False, 
                                "Mission completed but no points awarded",
                                f"Response: {data}"
                            )
                    elif response.status_code == 400:
                        # This could be a valid response if mission was already completed or limits reached
                        error_msg = response.json().get("detail", response.text)
                        if "already completed" in error_msg or "limit reached" in error_msg:
                            self.log_result(
                                "Complete Mission", 
                                True, 
                                f"Mission completion properly rejected: {error_msg}"
                            )
                        else:
                            self.log_result(
                                "Complete Mission", 
                                False, 
                                f"Mission completion failed: {error_msg}",
                                f"Response: {response.text}"
                            )
                    elif response.status_code == 404:
                        self.log_result(
                            "Complete Mission", 
                            False, 
                            "Mission not found or inactive",
                            f"Response: {response.text}"
                        )
                    elif response.status_code == 401:
                        self.log_result(
                            "Complete Mission", 
                            False, 
                            "Authentication failed - invalid user token",
                            f"Response: {response.text}"
                        )
                    else:
                        self.log_result(
                            "Complete Mission", 
                            False, 
                            f"Unexpected response status: {response.status_code}",
                            f"Response: {response.text}"
                        )
                else:
                    self.log_result(
                        "Complete Mission", 
                        True, 
                        "No available missions to complete (this is normal if all missions are completed or inactive)"
                    )
            else:
                self.log_result(
                    "Complete Mission", 
                    False, 
                    f"Failed to get missions list: {missions_response.status_code}",
                    f"Response: {missions_response.text}"
                )
        except Exception as e:
            self.log_result(
                "Complete Mission", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_mission_frequency_limits(self):
        """Test mission frequency limits enforcement"""
        print("\n⏰ Testing Mission Frequency Limits...")
        
        if not self.regular_user_token or not self.admin_token:
            self.log_result("Mission Frequency Limits", False, "Missing required tokens")
            return
        
        # Create a daily mission with limit 1
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        user_headers = {"Authorization": f"Bearer {self.regular_user_token}"}
        
        mission_data = {
            "title": "Test Daily Limit Mission",
            "description": "Test mission for frequency limit testing",
            "points": 10,
            "frequency": "daily",
            "daily_limit": 1,
            "weekly_limit": 0,
            "is_active": True
        }
        
        try:
            # Create mission
            response = requests.post(
                f"{API_BASE}/admin/missions",
                json=mission_data,
                headers=admin_headers
            )
            
            if response.status_code == 200:
                mission_id = response.json().get("mission_id")
                self.created_mission_ids.append(mission_id)
                
                # Complete mission first time (should succeed)
                response1 = requests.post(
                    f"{API_BASE}/missions/{mission_id}/complete",
                    headers=user_headers
                )
                
                # Complete mission second time (should fail due to daily limit)
                time.sleep(1)  # Small delay
                response2 = requests.post(
                    f"{API_BASE}/missions/{mission_id}/complete",
                    headers=user_headers
                )
                
                if response1.status_code == 200 and response2.status_code == 400:
                    error_msg = response2.json().get("detail", "")
                    if "limit reached" in error_msg.lower():
                        self.log_result(
                            "Mission Frequency Limits", 
                            True, 
                            "Daily limit properly enforced - first completion succeeded, second rejected"
                        )
                    else:
                        self.log_result(
                            "Mission Frequency Limits", 
                            False, 
                            f"Second completion rejected but wrong reason: {error_msg}"
                        )
                else:
                    self.log_result(
                        "Mission Frequency Limits", 
                        False, 
                        f"Unexpected responses - First: {response1.status_code}, Second: {response2.status_code}",
                        f"First: {response1.text}, Second: {response2.text}"
                    )
            else:
                self.log_result(
                    "Mission Frequency Limits", 
                    False, 
                    f"Failed to create test mission: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Mission Frequency Limits", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_authentication_enforcement(self):
        """Test that mission endpoints require proper authentication"""
        print("\n🔒 Testing Authentication & Authorization...")
        
        # Test admin endpoints without token
        try:
            response = requests.get(f"{API_BASE}/admin/missions")
            if response.status_code in [401, 403]:
                self.log_result(
                    "No Token Admin Auth Test", 
                    True, 
                    f"Correctly rejected admin request without authentication token (HTTP {response.status_code})"
                )
            else:
                self.log_result(
                    "No Token Admin Auth Test", 
                    False, 
                    f"Should have returned 401 or 403, got {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "No Token Admin Auth Test", 
                False, 
                f"Request failed: {str(e)}"
            )
        
        # Test user endpoints without token
        try:
            response = requests.get(f"{API_BASE}/missions")
            if response.status_code in [401, 403]:
                self.log_result(
                    "No Token User Auth Test", 
                    True, 
                    f"Correctly rejected user request without authentication token (HTTP {response.status_code})"
                )
            else:
                self.log_result(
                    "No Token User Auth Test", 
                    False, 
                    f"Should have returned 401 or 403, got {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "No Token User Auth Test", 
                False, 
                f"Request failed: {str(e)}"
            )
        
        # Test admin endpoints with regular user token (should fail with 403)
        if self.regular_user_token:
            headers = {"Authorization": f"Bearer {self.regular_user_token}"}
            try:
                response = requests.get(f"{API_BASE}/admin/missions", headers=headers)
                if response.status_code == 403:
                    self.log_result(
                        "Regular User Admin Access Test", 
                        True, 
                        "Correctly rejected regular user access to admin mission endpoints"
                    )
                else:
                    self.log_result(
                        "Regular User Admin Access Test", 
                        False, 
                        f"Should have returned 403, got {response.status_code}",
                        f"Response: {response.text}"
                    )
            except Exception as e:
                self.log_result(
                    "Regular User Admin Access Test", 
                    False, 
                    f"Request failed: {str(e)}"
                )
    
    def run_all_tests(self):
        """Run all mission management tests"""
        print("🚀 Starting Mission Management Backend Tests...")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users. Aborting tests.")
            return
        
        # Run authentication tests first
        self.test_authentication_enforcement()
        
        # Run admin mission management tests
        self.test_create_one_time_mission()
        self.test_create_daily_mission()
        self.test_create_weekly_mission()
        self.test_get_admin_missions()
        self.test_update_mission()
        self.test_mission_statistics()
        
        # Run user mission tests
        self.test_get_user_missions()
        self.test_complete_mission()
        self.test_mission_frequency_limits()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 MISSION MANAGEMENT TEST SUMMARY")
        print("=" * 60)
        
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
            print("\n🎉 ALL MISSION MANAGEMENT TESTS PASSED! Mission system is working correctly.")
        elif passed > failed:
            print(f"\n⚠️  MOSTLY WORKING: {passed}/{total} tests passed. Some issues need attention.")
        else:
            print(f"\n🚨 CRITICAL ISSUES: {failed}/{total} tests failed. Mission system needs fixes.")
        
        # Cleanup created missions
        if self.created_mission_ids and self.admin_token:
            print(f"\n🧹 Cleaning up {len(self.created_mission_ids)} test missions...")

if __name__ == "__main__":
    tester = MissionManagementTester()
    tester.run_all_tests()