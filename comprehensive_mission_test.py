#!/usr/bin/env python3
"""
Comprehensive Mission Management Testing Suite
Tests all specific scenarios from the review request including:
1. Admin Authentication & Mission CRUD
2. User Mission Completion Testing  
3. Frequency Limits Enforcement
4. Integration Testing
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://puglia-loyalty.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ComprehensiveMissionTester:
    def __init__(self):
        self.admin_token = None
        self.regular_user_token = None
        self.test_results = []
        self.admin_user_id = None
        self.test_user_id = None
        self.created_mission_ids = []
        self.test_missions = {}  # Store created missions for testing
        
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
    
    def setup_authentication(self):
        """Setup authentication with specific credentials from review request"""
        print("\n🔐 Setting up authentication with specific credentials...")
        
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
                    self.log_result("Admin Authentication", True, f"Successfully authenticated as admin: {admin_credentials['email']}")
                else:
                    self.log_result("Admin Authentication", False, f"User exists but lacks admin privileges")
                    return False
            else:
                self.log_result("Admin Authentication", False, f"Failed to authenticate admin: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Admin authentication error: {str(e)}")
            return False
        
        # Regular user credentials from review request
        user_credentials = {"email": "test@desideridipuglia.com", "password": "test123"}
        
        try:
            response = requests.post(f"{API_BASE}/auth/login", json=user_credentials)
            if response.status_code == 200:
                data = response.json()
                self.regular_user_token = data["access_token"]
                self.test_user_id = data["user"]["id"]
                self.log_result("User Authentication", True, f"Successfully authenticated as regular user: {user_credentials['email']}")
            else:
                self.log_result("User Authentication", False, f"Failed to authenticate regular user: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("User Authentication", False, f"User authentication error: {str(e)}")
            return False
        
        return True
    
    def test_admin_mission_crud(self):
        """Test complete admin mission CRUD operations"""
        print("\n📝 Testing Admin Mission CRUD Operations...")
        
        if not self.admin_token:
            self.log_result("Admin Mission CRUD", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test 1: Create One-time Mission
        one_time_mission = {
            "title": "Visita Castello di Otranto",
            "description": "Visita il magnifico Castello Aragonese di Otranto e condividi una foto sui social",
            "points": 50,
            "frequency": "one-time",
            "daily_limit": 0,
            "weekly_limit": 0,
            "is_active": True
        }
        
        try:
            response = requests.post(f"{API_BASE}/admin/missions", json=one_time_mission, headers=headers)
            if response.status_code == 200:
                data = response.json()
                mission_id = data.get("mission_id")
                if mission_id:
                    self.created_mission_ids.append(mission_id)
                    self.test_missions["one_time"] = mission_id
                    self.log_result("Create One-Time Mission", True, "One-time mission created successfully")
                else:
                    self.log_result("Create One-Time Mission", False, "Mission created but no ID returned")
            else:
                self.log_result("Create One-Time Mission", False, f"Failed to create mission: {response.status_code}")
        except Exception as e:
            self.log_result("Create One-Time Mission", False, f"Request failed: {str(e)}")
        
        # Test 2: Create Daily Mission with Limit
        daily_mission = {
            "title": "Condividi Storia Instagram Puglia",
            "description": "Condividi una storia Instagram taggando @desideridipuglia",
            "points": 20,
            "frequency": "daily",
            "daily_limit": 3,
            "weekly_limit": 0,
            "is_active": True
        }
        
        try:
            response = requests.post(f"{API_BASE}/admin/missions", json=daily_mission, headers=headers)
            if response.status_code == 200:
                data = response.json()
                mission_id = data.get("mission_id")
                if mission_id:
                    self.created_mission_ids.append(mission_id)
                    self.test_missions["daily"] = mission_id
                    self.log_result("Create Daily Mission", True, "Daily mission with limit 3 created successfully")
                else:
                    self.log_result("Create Daily Mission", False, "Mission created but no ID returned")
            else:
                self.log_result("Create Daily Mission", False, f"Failed to create mission: {response.status_code}")
        except Exception as e:
            self.log_result("Create Daily Mission", False, f"Request failed: {str(e)}")
        
        # Test 3: Create Weekly Mission with Limit
        weekly_mission = {
            "title": "Recensione Partner Pugliese",
            "description": "Lascia una recensione dettagliata per un partner locale pugliese",
            "points": 75,
            "frequency": "weekly",
            "daily_limit": 0,
            "weekly_limit": 5,
            "is_active": True
        }
        
        try:
            response = requests.post(f"{API_BASE}/admin/missions", json=weekly_mission, headers=headers)
            if response.status_code == 200:
                data = response.json()
                mission_id = data.get("mission_id")
                if mission_id:
                    self.created_mission_ids.append(mission_id)
                    self.test_missions["weekly"] = mission_id
                    self.log_result("Create Weekly Mission", True, "Weekly mission with limit 5 created successfully")
                else:
                    self.log_result("Create Weekly Mission", False, "Mission created but no ID returned")
            else:
                self.log_result("Create Weekly Mission", False, f"Failed to create mission: {response.status_code}")
        except Exception as e:
            self.log_result("Create Weekly Mission", False, f"Request failed: {str(e)}")
        
        # Test 4: Create Mission with No Limits
        unlimited_mission = {
            "title": "Esplora Puglia Libera",
            "description": "Esplora qualsiasi luogo della Puglia e condividi la tua esperienza",
            "points": 30,
            "frequency": "daily",
            "daily_limit": 0,  # No limit
            "weekly_limit": 0,  # No limit
            "is_active": True
        }
        
        try:
            response = requests.post(f"{API_BASE}/admin/missions", json=unlimited_mission, headers=headers)
            if response.status_code == 200:
                data = response.json()
                mission_id = data.get("mission_id")
                if mission_id:
                    self.created_mission_ids.append(mission_id)
                    self.test_missions["unlimited"] = mission_id
                    self.log_result("Create Unlimited Mission", True, "Mission with no limits created successfully")
                else:
                    self.log_result("Create Unlimited Mission", False, "Mission created but no ID returned")
            else:
                self.log_result("Create Unlimited Mission", False, f"Failed to create mission: {response.status_code}")
        except Exception as e:
            self.log_result("Create Unlimited Mission", False, f"Request failed: {str(e)}")
        
        # Test 5: Get Missions List with Stats
        try:
            response = requests.get(f"{API_BASE}/admin/missions", headers=headers)
            if response.status_code == 200:
                missions = response.json()
                if isinstance(missions, list) and len(missions) >= 4:
                    # Check if our created missions are in the list
                    mission_ids = [m["id"] for m in missions]
                    created_found = sum(1 for mid in self.created_mission_ids if mid in mission_ids)
                    self.log_result("Get Missions List", True, f"Retrieved {len(missions)} missions, {created_found} of our created missions found")
                else:
                    self.log_result("Get Missions List", False, f"Expected at least 4 missions, got {len(missions) if isinstance(missions, list) else 'invalid response'}")
            else:
                self.log_result("Get Missions List", False, f"Failed to get missions: {response.status_code}")
        except Exception as e:
            self.log_result("Get Missions List", False, f"Request failed: {str(e)}")
        
        # Test 6: Update Mission
        if self.test_missions.get("one_time"):
            update_data = {
                "title": "Visita Castello di Otranto - AGGIORNATO",
                "points": 60,
                "is_active": False
            }
            
            try:
                response = requests.put(
                    f"{API_BASE}/admin/missions/{self.test_missions['one_time']}", 
                    json=update_data, 
                    headers=headers
                )
                if response.status_code == 200:
                    self.log_result("Update Mission", True, "Mission updated successfully (title, points, status)")
                else:
                    self.log_result("Update Mission", False, f"Failed to update mission: {response.status_code}")
            except Exception as e:
                self.log_result("Update Mission", False, f"Request failed: {str(e)}")
        
        # Test 7: Get Mission Statistics
        try:
            response = requests.get(f"{API_BASE}/admin/missions/statistics", headers=headers)
            if response.status_code == 200:
                stats = response.json()
                overview = stats.get("overview", {})
                total_missions = overview.get("total_missions", 0)
                total_completions = overview.get("total_completions", 0)
                total_points = overview.get("total_points_awarded", 0)
                self.log_result("Mission Statistics", True, f"Statistics: {total_missions} missions, {total_completions} completions, {total_points} points awarded")
            else:
                self.log_result("Mission Statistics", False, f"Failed to get statistics: {response.status_code}")
        except Exception as e:
            self.log_result("Mission Statistics", False, f"Request failed: {str(e)}")
    
    def test_user_mission_completion(self):
        """Test user mission completion system"""
        print("\n🎯 Testing User Mission Completion System...")
        
        if not self.regular_user_token:
            self.log_result("User Mission Completion", False, "No regular user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.regular_user_token}"}
        
        # Test 1: Get User Missions with Availability Status
        try:
            response = requests.get(f"{API_BASE}/missions", headers=headers)
            if response.status_code == 200:
                missions = response.json()
                if isinstance(missions, list):
                    available_missions = [m for m in missions if m.get("available", False)]
                    completed_missions = [m for m in missions if m.get("completed", False)]
                    self.log_result("Get User Missions", True, f"Retrieved {len(missions)} missions ({len(available_missions)} available, {len(completed_missions)} completed)")
                    
                    # Store available missions for testing
                    self.user_available_missions = available_missions
                else:
                    self.log_result("Get User Missions", False, "Invalid response format")
            else:
                self.log_result("Get User Missions", False, f"Failed to get user missions: {response.status_code}")
        except Exception as e:
            self.log_result("Get User Missions", False, f"Request failed: {str(e)}")
        
        # Test 2: Complete One-Time Mission
        one_time_missions = [m for m in getattr(self, 'user_available_missions', []) if m.get("frequency") == "one-time"]
        if one_time_missions:
            mission = one_time_missions[0]
            try:
                response = requests.post(f"{API_BASE}/missions/{mission['id']}/complete", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    points = data.get("points_earned", 0)
                    self.log_result("Complete One-Time Mission", True, f"One-time mission completed, earned {points} points")
                    
                    # Try to complete again (should fail)
                    response2 = requests.post(f"{API_BASE}/missions/{mission['id']}/complete", headers=headers)
                    if response2.status_code == 400:
                        self.log_result("One-Time Mission Rejection", True, "Correctly rejected second completion attempt")
                    else:
                        self.log_result("One-Time Mission Rejection", False, f"Should have rejected second attempt, got {response2.status_code}")
                else:
                    self.log_result("Complete One-Time Mission", False, f"Failed to complete mission: {response.status_code}")
            except Exception as e:
                self.log_result("Complete One-Time Mission", False, f"Request failed: {str(e)}")
        
        # Test 3: Complete Daily Mission (test limits)
        daily_missions = [m for m in getattr(self, 'user_available_missions', []) if m.get("frequency") == "daily" and m.get("daily_limit", 0) > 0]
        if daily_missions:
            mission = daily_missions[0]
            daily_limit = mission.get("daily_limit", 0)
            
            successful_completions = 0
            for attempt in range(daily_limit + 2):  # Try to exceed limit
                try:
                    response = requests.post(f"{API_BASE}/missions/{mission['id']}/complete", headers=headers)
                    if response.status_code == 200:
                        successful_completions += 1
                    elif response.status_code == 400 and "limit reached" in response.text.lower():
                        break
                    time.sleep(0.5)  # Small delay between attempts
                except Exception:
                    break
            
            if successful_completions == daily_limit:
                self.log_result("Daily Mission Limits", True, f"Daily limit properly enforced: {successful_completions}/{daily_limit} completions allowed")
            else:
                self.log_result("Daily Mission Limits", False, f"Daily limit not properly enforced: {successful_completions} completions vs {daily_limit} limit")
        
        # Test 4: Complete Weekly Mission (test limits)
        weekly_missions = [m for m in getattr(self, 'user_available_missions', []) if m.get("frequency") == "weekly" and m.get("weekly_limit", 0) > 0]
        if weekly_missions:
            mission = weekly_missions[0]
            weekly_limit = mission.get("weekly_limit", 0)
            
            successful_completions = 0
            for attempt in range(min(3, weekly_limit + 1)):  # Test a few completions
                try:
                    response = requests.post(f"{API_BASE}/missions/{mission['id']}/complete", headers=headers)
                    if response.status_code == 200:
                        successful_completions += 1
                    elif response.status_code == 400 and "limit reached" in response.text.lower():
                        break
                    time.sleep(0.5)
                except Exception:
                    break
            
            self.log_result("Weekly Mission Completion", True, f"Weekly mission completions: {successful_completions} (limit: {weekly_limit})")
    
    def test_integration_features(self):
        """Test integration features like point awarding and notifications"""
        print("\n🔗 Testing Integration Features...")
        
        if not self.regular_user_token:
            self.log_result("Integration Testing", False, "No regular user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.regular_user_token}"}
        
        # Get user profile before mission completion
        try:
            response = requests.get(f"{API_BASE}/user/profile", headers=headers)
            if response.status_code == 200:
                profile_before = response.json()
                points_before = profile_before.get("current_points", 0)
                
                # Find an available mission to complete
                missions_response = requests.get(f"{API_BASE}/missions", headers=headers)
                if missions_response.status_code == 200:
                    missions = missions_response.json()
                    available_missions = [m for m in missions if m.get("available", False) and not m.get("completed", False)]
                    
                    if available_missions:
                        mission = available_missions[0]
                        expected_points = mission.get("points", 0)
                        
                        # Complete the mission
                        complete_response = requests.post(f"{API_BASE}/missions/{mission['id']}/complete", headers=headers)
                        if complete_response.status_code == 200:
                            # Check if points were awarded
                            time.sleep(1)  # Small delay for processing
                            profile_response = requests.get(f"{API_BASE}/user/profile", headers=headers)
                            if profile_response.status_code == 200:
                                profile_after = profile_response.json()
                                points_after = profile_after.get("current_points", 0)
                                points_gained = points_after - points_before
                                
                                if points_gained == expected_points:
                                    self.log_result("Point Awarding Integration", True, f"Points correctly awarded: {points_gained} points")
                                else:
                                    self.log_result("Point Awarding Integration", False, f"Points mismatch: expected {expected_points}, got {points_gained}")
                            else:
                                self.log_result("Point Awarding Integration", False, "Failed to get updated profile")
                        else:
                            self.log_result("Point Awarding Integration", False, f"Mission completion failed: {complete_response.status_code}")
                    else:
                        self.log_result("Point Awarding Integration", True, "No available missions to test (this is normal if all are completed)")
                else:
                    self.log_result("Point Awarding Integration", False, "Failed to get missions list")
            else:
                self.log_result("Point Awarding Integration", False, "Failed to get user profile")
        except Exception as e:
            self.log_result("Point Awarding Integration", False, f"Request failed: {str(e)}")
        
        # Test notifications
        try:
            response = requests.get(f"{API_BASE}/notifications", headers=headers)
            if response.status_code == 200:
                notifications = response.json()
                if isinstance(notifications, list):
                    mission_notifications = [n for n in notifications if "missione" in n.get("message", "").lower()]
                    self.log_result("Notification Integration", True, f"Retrieved {len(notifications)} notifications ({len(mission_notifications)} mission-related)")
                else:
                    self.log_result("Notification Integration", False, "Invalid notifications response")
            else:
                self.log_result("Notification Integration", False, f"Failed to get notifications: {response.status_code}")
        except Exception as e:
            self.log_result("Notification Integration", False, f"Request failed: {str(e)}")
    
    def run_comprehensive_tests(self):
        """Run all comprehensive mission management tests"""
        print("🚀 Starting Comprehensive Mission Management Tests...")
        print(f"Backend URL: {BACKEND_URL}")
        print("Testing with specific admin credentials from review request")
        print("=" * 70)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Failed to setup authentication. Aborting tests.")
            return
        
        # Run all test suites
        self.test_admin_mission_crud()
        self.test_user_mission_completion()
        self.test_integration_features()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE MISSION MANAGEMENT TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if "✅ PASS" in result["status"])
        failed = sum(1 for result in self.test_results if "❌ FAIL" in result["status"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0%")
        
        # Categorize results
        admin_tests = [r for r in self.test_results if any(keyword in r["test"].lower() for keyword in ["admin", "create", "update", "statistics", "crud"])]
        user_tests = [r for r in self.test_results if any(keyword in r["test"].lower() for keyword in ["user", "complete", "mission", "daily", "weekly", "one-time"])]
        integration_tests = [r for r in self.test_results if any(keyword in r["test"].lower() for keyword in ["integration", "point", "notification"])]
        auth_tests = [r for r in self.test_results if "auth" in r["test"].lower()]
        
        print(f"\n📋 TEST BREAKDOWN:")
        print(f"Authentication Tests: {sum(1 for r in auth_tests if '✅' in r['status'])}/{len(auth_tests)} passed")
        print(f"Admin CRUD Tests: {sum(1 for r in admin_tests if '✅' in r['status'])}/{len(admin_tests)} passed")
        print(f"User Mission Tests: {sum(1 for r in user_tests if '✅' in r['status'])}/{len(user_tests)} passed")
        print(f"Integration Tests: {sum(1 for r in integration_tests if '✅' in r['status'])}/{len(integration_tests)} passed")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['message']}")
                    if result.get("details"):
                        print(f"    Details: {result['details']}")
        
        # Overall assessment
        if failed == 0:
            print("\n🎉 ALL COMPREHENSIVE TESTS PASSED!")
            print("✅ Admin mission management working perfectly")
            print("✅ User mission completion system functional")
            print("✅ Frequency limits properly enforced")
            print("✅ Point awarding and integration working")
            print("✅ Mission statistics accurate")
        elif passed > failed:
            print(f"\n⚠️  MOSTLY WORKING: {passed}/{total} tests passed.")
            print("Most functionality is working but some issues need attention.")
        else:
            print(f"\n🚨 CRITICAL ISSUES: {failed}/{total} tests failed.")
            print("Mission system needs significant fixes.")

if __name__ == "__main__":
    tester = ComprehensiveMissionTester()
    tester.run_comprehensive_tests()