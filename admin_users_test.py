#!/usr/bin/env python3
"""
Admin Users List Endpoint Testing - PRIORITY MAXIMUM
Focus: Test /api/admin/users/list endpoint and related admin endpoints for user statistics
"""

import requests
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://puglia-club.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class AdminUsersListTester:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        self.admin_user_id = None
        
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
    
    def setup_admin_user(self):
        """Login with admin credentials from review request"""
        print("\n🔧 Setting up admin user...")
        
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
                    return True
                else:
                    print(f"❌ User {admin_credentials['email']} exists but is not admin")
                    return False
            else:
                print(f"❌ Failed to login admin user: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error logging in admin user: {str(e)}")
            return False
    
    def test_admin_users_list_endpoint(self):
        """Test /api/admin/users/list endpoint - PRIORITY MAXIMUM"""
        print("\n👥 Testing Admin Users List Endpoint - PRIORITY MAXIMUM...")
        
        if not self.admin_token:
            self.log_result("Admin Users List", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/admin/users/list", headers=headers)
            
            print(f"📡 Request: GET {API_BASE}/admin/users/list")
            print(f"📡 Response Status: {response.status_code}")
            print(f"📡 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    users_data = response.json()
                    print(f"📡 Response Body: {json.dumps(users_data, indent=2)}")
                    
                    if isinstance(users_data, list):
                        if len(users_data) > 0:
                            # Check user structure
                            user = users_data[0]
                            expected_fields = ["id", "name", "email", "username", "current_points", "total_points", "join_date"]
                            missing_fields = [field for field in expected_fields if field not in user]
                            
                            if not missing_fields:
                                self.log_result(
                                    "Admin Users List", 
                                    True, 
                                    f"Successfully retrieved {len(users_data)} users with all expected fields"
                                )
                                
                                # Show sample user data
                                print(f"📊 Sample User Data:")
                                for field in expected_fields:
                                    print(f"   {field}: {user.get(field)}")
                                    
                            else:
                                self.log_result(
                                    "Admin Users List", 
                                    False, 
                                    f"Users missing expected fields: {missing_fields}",
                                    f"Available fields: {list(user.keys())}"
                                )
                        else:
                            self.log_result(
                                "Admin Users List", 
                                False, 
                                "Endpoint returned empty list - no users found in database",
                                "This could indicate: 1) No users in database, 2) Query filtering out all users, 3) Database connection issue"
                            )
                    elif isinstance(users_data, dict):
                        # Check if it's an error response
                        if "detail" in users_data:
                            self.log_result(
                                "Admin Users List", 
                                False, 
                                f"API returned error: {users_data['detail']}",
                                f"Full response: {users_data}"
                            )
                        else:
                            self.log_result(
                                "Admin Users List", 
                                False, 
                                "Expected list but got dict - check API implementation",
                                f"Response: {users_data}"
                            )
                    else:
                        self.log_result(
                            "Admin Users List", 
                            False, 
                            f"Unexpected response format: {type(users_data)}",
                            f"Response: {users_data}"
                        )
                        
                except json.JSONDecodeError as e:
                    self.log_result(
                        "Admin Users List", 
                        False, 
                        "Response is not valid JSON",
                        f"Raw response: {response.text[:500]}..."
                    )
                    
            elif response.status_code == 404:
                self.log_result(
                    "Admin Users List", 
                    False, 
                    "Endpoint not found - /api/admin/users/list may not be implemented",
                    f"Response: {response.text}"
                )
            elif response.status_code == 403:
                self.log_result(
                    "Admin Users List", 
                    False, 
                    "Access denied - admin authentication may be failing",
                    f"Response: {response.text}"
                )
            elif response.status_code == 401:
                self.log_result(
                    "Admin Users List", 
                    False, 
                    "Unauthorized - admin token may be invalid",
                    f"Response: {response.text}"
                )
            elif response.status_code == 500:
                self.log_result(
                    "Admin Users List", 
                    False, 
                    "Internal server error - check backend logs",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Admin Users List", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.ConnectionError as e:
            self.log_result(
                "Admin Users List", 
                False, 
                f"Connection error - backend may be down: {str(e)}"
            )
        except Exception as e:
            self.log_result(
                "Admin Users List", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_leaderboard_endpoint(self):
        """Test /api/leaderboard endpoint for user stats"""
        print("\n🏆 Testing Leaderboard Endpoint for User Stats...")
        
        try:
            response = requests.get(f"{API_BASE}/leaderboard")
            
            print(f"📡 Request: GET {API_BASE}/leaderboard")
            print(f"📡 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    leaderboard_data = response.json()
                    print(f"📡 Response Body: {json.dumps(leaderboard_data, indent=2)}")
                    
                    if isinstance(leaderboard_data, dict):
                        leaderboard = leaderboard_data.get("leaderboard", [])
                        if isinstance(leaderboard, list) and len(leaderboard) > 0:
                            user = leaderboard[0]
                            expected_fields = ["position", "user_id", "username", "name", "points"]
                            missing_fields = [field for field in expected_fields if field not in user]
                            
                            if not missing_fields:
                                self.log_result(
                                    "Leaderboard Endpoint", 
                                    True, 
                                    f"Successfully retrieved leaderboard with {len(leaderboard)} users"
                                )
                            else:
                                self.log_result(
                                    "Leaderboard Endpoint", 
                                    False, 
                                    f"Leaderboard users missing fields: {missing_fields}",
                                    f"Available fields: {list(user.keys())}"
                                )
                        else:
                            self.log_result(
                                "Leaderboard Endpoint", 
                                False, 
                                "Leaderboard is empty - no users with points found",
                                f"Response: {leaderboard_data}"
                            )
                    else:
                        self.log_result(
                            "Leaderboard Endpoint", 
                            False, 
                            f"Unexpected response format: {type(leaderboard_data)}",
                            f"Response: {leaderboard_data}"
                        )
                        
                except json.JSONDecodeError as e:
                    self.log_result(
                        "Leaderboard Endpoint", 
                        False, 
                        "Response is not valid JSON",
                        f"Raw response: {response.text[:500]}..."
                    )
            else:
                self.log_result(
                    "Leaderboard Endpoint", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Leaderboard Endpoint", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_admin_missions_endpoint(self):
        """Test /api/admin/missions endpoint for mission stats"""
        print("\n🎯 Testing Admin Missions Endpoint...")
        
        if not self.admin_token:
            self.log_result("Admin Missions", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/admin/missions", headers=headers)
            
            print(f"📡 Request: GET {API_BASE}/admin/missions")
            print(f"📡 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    missions_data = response.json()
                    print(f"📡 Response Body: {json.dumps(missions_data, indent=2)}")
                    
                    if isinstance(missions_data, list):
                        if len(missions_data) > 0:
                            mission = missions_data[0]
                            expected_fields = ["id", "title", "description", "points", "frequency", "is_active"]
                            missing_fields = [field for field in expected_fields if field not in mission]
                            
                            if not missing_fields:
                                active_missions = sum(1 for m in missions_data if m.get("is_active", False))
                                self.log_result(
                                    "Admin Missions", 
                                    True, 
                                    f"Successfully retrieved {len(missions_data)} missions ({active_missions} active)"
                                )
                            else:
                                self.log_result(
                                    "Admin Missions", 
                                    False, 
                                    f"Missions missing expected fields: {missing_fields}",
                                    f"Available fields: {list(mission.keys())}"
                                )
                        else:
                            self.log_result(
                                "Admin Missions", 
                                True, 
                                "No missions found (this is normal if no missions created yet)"
                            )
                    else:
                        self.log_result(
                            "Admin Missions", 
                            False, 
                            f"Unexpected response format: {type(missions_data)}",
                            f"Response: {missions_data}"
                        )
                        
                except json.JSONDecodeError as e:
                    self.log_result(
                        "Admin Missions", 
                        False, 
                        "Response is not valid JSON",
                        f"Raw response: {response.text[:500]}..."
                    )
            elif response.status_code == 403:
                self.log_result(
                    "Admin Missions", 
                    False, 
                    "Access denied - admin authentication failing",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Admin Missions", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Admin Missions", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_pending_submissions_endpoint(self):
        """Test /api/admin/missions/submissions/pending endpoint"""
        print("\n📝 Testing Pending Submissions Endpoint...")
        
        if not self.admin_token:
            self.log_result("Pending Submissions", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/admin/missions/submissions/pending", headers=headers)
            
            print(f"📡 Request: GET {API_BASE}/admin/missions/submissions/pending")
            print(f"📡 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    submissions_data = response.json()
                    print(f"📡 Response Body: {json.dumps(submissions_data, indent=2)}")
                    
                    if isinstance(submissions_data, list):
                        if len(submissions_data) > 0:
                            submission = submissions_data[0]
                            expected_fields = ["id", "user_id", "mission_id", "mission_title", "verification_status"]
                            missing_fields = [field for field in expected_fields if field not in submission]
                            
                            if not missing_fields:
                                pending_count = sum(1 for s in submissions_data if s.get("verification_status") == "pending")
                                self.log_result(
                                    "Pending Submissions", 
                                    True, 
                                    f"Successfully retrieved {len(submissions_data)} submissions ({pending_count} pending)"
                                )
                            else:
                                self.log_result(
                                    "Pending Submissions", 
                                    False, 
                                    f"Submissions missing expected fields: {missing_fields}",
                                    f"Available fields: {list(submission.keys())}"
                                )
                        else:
                            self.log_result(
                                "Pending Submissions", 
                                True, 
                                "No pending submissions found (this is normal if no submissions pending)"
                            )
                    else:
                        self.log_result(
                            "Pending Submissions", 
                            False, 
                            f"Unexpected response format: {type(submissions_data)}",
                            f"Response: {submissions_data}"
                        )
                        
                except json.JSONDecodeError as e:
                    self.log_result(
                        "Pending Submissions", 
                        False, 
                        "Response is not valid JSON",
                        f"Raw response: {response.text[:500]}..."
                    )
            elif response.status_code == 403:
                self.log_result(
                    "Pending Submissions", 
                    False, 
                    "Access denied - admin authentication failing",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Pending Submissions", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Pending Submissions", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def check_backend_logs(self):
        """Check backend logs for any errors"""
        print("\n📋 Checking Backend Logs...")
        
        try:
            import subprocess
            result = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logs = result.stdout.strip()
                if logs:
                    print("🔍 Recent Backend Error Logs:")
                    print(logs)
                    
                    # Check for specific errors related to users endpoint
                    if "users/list" in logs.lower():
                        print("⚠️  Found users/list related errors in logs!")
                    if "error" in logs.lower() or "exception" in logs.lower():
                        print("⚠️  Found errors/exceptions in backend logs!")
                else:
                    print("✅ No recent error logs found")
            else:
                print("❌ Could not read backend error logs")
                
        except Exception as e:
            print(f"❌ Error checking backend logs: {str(e)}")
    
    def run_all_tests(self):
        """Run all admin users list tests"""
        print("🚀 Starting Admin Users List Endpoint Testing - PRIORITY MAXIMUM...")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Setup
        if not self.setup_admin_user():
            print("❌ Failed to setup admin user. Aborting tests.")
            return
        
        # Run tests in priority order
        print("\n🎯 PRIORITY TESTS:")
        print("1. Admin Users List Endpoint - MAXIMUM PRIORITY")
        self.test_admin_users_list_endpoint()
        
        print("\n2. Leaderboard for User Stats")
        self.test_leaderboard_endpoint()
        
        print("\n3. Admin Missions")
        self.test_admin_missions_endpoint()
        
        print("\n4. Pending Submissions")
        self.test_pending_submissions_endpoint()
        
        # Check backend logs
        self.check_backend_logs()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 ADMIN USERS LIST ENDPOINT TEST SUMMARY")
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
                    if result['details']:
                        print(f"    Details: {result['details']}")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"{result['status']} - {result['test']}")
        
        # Focus on admin users list endpoint
        admin_users_test = next((r for r in self.test_results if r['test'] == 'Admin Users List'), None)
        if admin_users_test:
            if "✅ PASS" in admin_users_test['status']:
                print("\n🎉 ADMIN USERS LIST ENDPOINT IS WORKING!")
                print("✅ /api/admin/users/list returns user data correctly")
            else:
                print("\n🚨 ADMIN USERS LIST ENDPOINT ISSUE IDENTIFIED!")
                print("❌ /api/admin/users/list is not working as expected")
                print(f"❌ Issue: {admin_users_test['message']}")
                if admin_users_test['details']:
                    print(f"❌ Details: {admin_users_test['details']}")

if __name__ == "__main__":
    tester = AdminUsersListTester()
    tester.run_all_tests()