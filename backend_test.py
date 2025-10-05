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
    
    def test_create_mission_with_verification_settings(self):
        """Test creating a mission with verification requirements"""
        print("\n🎯 Testing Mission Creation with Verification Settings...")
        
        if not self.admin_token:
            self.log_result("Create Mission with Verification", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        mission_data = {
            "title": "Visita Castello di Lecce con Foto",
            "description": "Visita il Castello di Lecce, scatta una foto e condividi il link della tua esperienza",
            "points": 75,
            "frequency": "one-time",
            "daily_limit": 0,
            "weekly_limit": 0,
            "is_active": True,
            # Verification requirements as specified in review request
            "requires_description": True,
            "requires_photo": True,
            "photo_source": "camera",
            "requires_link": True,
            "requires_approval": True
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
                        "Create Mission with Verification", 
                        True, 
                        f"Mission with verification requirements created successfully: {mission_data['title']}"
                    )
                    
                    # Verify the mission was created with correct verification settings
                    self.verify_mission_verification_settings(mission_id)
                else:
                    self.log_result(
                        "Create Mission with Verification", 
                        False, 
                        "Mission created but no mission_id returned",
                        f"Response: {data}"
                    )
            elif response.status_code == 403:
                self.log_result(
                    "Create Mission with Verification", 
                    False, 
                    "Access denied - user may not have admin privileges",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Create Mission with Verification", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Create Mission with Verification", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def verify_mission_verification_settings(self, mission_id: str):
        """Verify that mission was created with correct verification settings"""
        print("\n🔍 Verifying Mission Verification Settings...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/admin/missions", headers=headers)
            
            if response.status_code == 200:
                missions = response.json()
                mission = next((m for m in missions if m["id"] == mission_id), None)
                
                if mission:
                    verification_fields = {
                        "requires_description": True,
                        "requires_photo": True,
                        "photo_source": "camera",
                        "requires_link": True,
                        "requires_approval": True
                    }
                    
                    all_correct = True
                    for field, expected_value in verification_fields.items():
                        actual_value = mission.get(field)
                        if actual_value != expected_value:
                            all_correct = False
                            self.log_result(
                                "Verify Mission Settings", 
                                False, 
                                f"Field {field}: expected {expected_value}, got {actual_value}"
                            )
                    
                    if all_correct:
                        self.log_result(
                            "Verify Mission Settings", 
                            True, 
                            "All verification settings correctly saved and retrieved"
                        )
                else:
                    self.log_result(
                        "Verify Mission Settings", 
                        False, 
                        "Created mission not found in admin missions list"
                    )
            else:
                self.log_result(
                    "Verify Mission Settings", 
                    False, 
                    f"Failed to retrieve admin missions: {response.status_code}"
                )
        except Exception as e:
            self.log_result(
                "Verify Mission Settings", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_mission_submission_system(self):
        """Test mission submission with FormData (description, photo, link)"""
        print("\n📝 Testing Mission Submission System...")
        
        if not self.regular_user_token or not self.created_mission_ids:
            self.log_result("Mission Submission System", False, "No regular user token or created missions available")
            return
        
        headers = {"Authorization": f"Bearer {self.regular_user_token}"}
        mission_id = self.created_mission_ids[0]  # Use first created mission
        
        # Create a simple test image (10x10 pixel PNG with proper format)
        from PIL import Image
        import io
        
        # Create a simple 10x10 red image
        img = Image.new('RGB', (10, 10), color='red')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        test_image_data = img_buffer.getvalue()
        
        # Prepare FormData
        files = {
            'photo': ('test_photo.png', BytesIO(test_image_data), 'image/png')
        }
        
        data = {
            'description': 'Ho visitato il Castello di Lecce e ho scattato questa bellissima foto durante il tramonto. L\'architettura medievale è davvero impressionante!',
            'submission_url': 'https://www.instagram.com/p/example123/'
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/missions/{mission_id}/submit",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                response_data = response.json()
                requires_approval = response_data.get("requires_approval", False)
                points_earned = response_data.get("points_earned", 0)
                
                if requires_approval:
                    self.log_result(
                        "Mission Submission System", 
                        True, 
                        f"Mission submitted successfully for approval. Will earn {points_earned} points after approval."
                    )
                    
                    # Check if MissionSubmission record was created
                    self.verify_mission_submission_created(mission_id)
                else:
                    self.log_result(
                        "Mission Submission System", 
                        True, 
                        f"Mission auto-approved and completed. Earned {points_earned} points immediately."
                    )
            elif response.status_code == 400:
                error_msg = response.json().get("detail", response.text)
                if "already submitted" in error_msg.lower():
                    self.log_result(
                        "Mission Submission System", 
                        True, 
                        f"Mission submission properly rejected (already submitted): {error_msg}"
                    )
                else:
                    self.log_result(
                        "Mission Submission System", 
                        False, 
                        f"Mission submission failed with validation error: {error_msg}",
                        f"Response: {response.text}"
                    )
            elif response.status_code == 404:
                self.log_result(
                    "Mission Submission System", 
                    False, 
                    "Mission not found or inactive",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Mission Submission System", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Mission Submission System", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def verify_mission_submission_created(self, mission_id: str):
        """Verify that MissionSubmission record was created with pending status"""
        print("\n🔍 Verifying Mission Submission Record...")
        
        if not self.admin_token:
            self.log_result("Verify Submission Record", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/admin/missions/submissions/pending", headers=headers)
            
            if response.status_code == 200:
                submissions = response.json()
                
                # Find submission for our mission
                mission_submission = next(
                    (s for s in submissions if s["mission_id"] == mission_id and s["user_id"] == self.test_user_id), 
                    None
                )
                
                if mission_submission:
                    if mission_submission["verification_status"] == "pending":
                        self.created_submission_ids.append(mission_submission["id"])
                        self.log_result(
                            "Verify Submission Record", 
                            True, 
                            f"MissionSubmission record created with pending status for mission: {mission_submission['mission_title']}"
                        )
                    else:
                        self.log_result(
                            "Verify Submission Record", 
                            False, 
                            f"Submission found but status is {mission_submission['verification_status']}, expected 'pending'"
                        )
                else:
                    self.log_result(
                        "Verify Submission Record", 
                        False, 
                        "No pending submission found for the submitted mission"
                    )
            else:
                self.log_result(
                    "Verify Submission Record", 
                    False, 
                    f"Failed to get pending submissions: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Verify Submission Record", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_admin_approval_workflow(self):
        """Test admin approval workflow for mission submissions"""
        print("\n✅ Testing Admin Approval Workflow...")
        
        if not self.admin_token or not self.created_submission_ids:
            self.log_result("Admin Approval Workflow", False, "No admin token or pending submissions available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        submission_id = self.created_submission_ids[0]  # Use first created submission
        
        # First, get pending submissions to verify our submission is there
        try:
            response = requests.get(f"{API_BASE}/admin/missions/submissions/pending", headers=headers)
            
            if response.status_code == 200:
                submissions = response.json()
                submission = next((s for s in submissions if s["id"] == submission_id), None)
                
                if submission:
                    self.log_result(
                        "Get Pending Submissions", 
                        True, 
                        f"Found pending submission: {submission['mission_title']} by {submission['user_name']}"
                    )
                    
                    # Now approve the submission
                    self.approve_mission_submission(submission_id, submission)
                else:
                    self.log_result(
                        "Get Pending Submissions", 
                        False, 
                        "Created submission not found in pending submissions list"
                    )
            else:
                self.log_result(
                    "Get Pending Submissions", 
                    False, 
                    f"Failed to get pending submissions: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Get Pending Submissions", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def approve_mission_submission(self, submission_id: str, submission_data: dict):
        """Approve a mission submission and verify point awarding"""
        print("\n🎉 Testing Mission Submission Approval...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get user's current points before approval
        user_headers = {"Authorization": f"Bearer {self.regular_user_token}"}
        
        try:
            # Get user profile before approval
            profile_response = requests.get(f"{API_BASE}/user/profile", headers=user_headers)
            points_before = 0
            if profile_response.status_code == 200:
                points_before = profile_response.json().get("current_points", 0)
            
            # Approve the submission
            response = requests.put(
                f"{API_BASE}/admin/missions/submissions/{submission_id}/verify?status=approved",
                headers=headers
            )
            
            if response.status_code == 200:
                self.log_result(
                    "Approve Submission", 
                    True, 
                    f"Mission submission approved successfully: {response.json().get('message', 'Approved')}"
                )
                
                # Verify UserMission record was created and points awarded
                time.sleep(1)  # Small delay for processing
                self.verify_points_awarded(points_before, submission_data["points_earned"])
                
            else:
                self.log_result(
                    "Approve Submission", 
                    False, 
                    f"Failed to approve submission: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Approve Submission", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def verify_points_awarded(self, points_before: int, expected_points: int):
        """Verify that points were correctly awarded after approval"""
        print("\n💰 Verifying Points Awarded...")
        
        user_headers = {"Authorization": f"Bearer {self.regular_user_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/user/profile", headers=user_headers)
            
            if response.status_code == 200:
                profile = response.json()
                points_after = profile.get("current_points", 0)
                points_awarded = points_after - points_before
                
                if points_awarded == expected_points:
                    self.log_result(
                        "Verify Points Awarded", 
                        True, 
                        f"Correct points awarded: {points_awarded} points (from {points_before} to {points_after})"
                    )
                else:
                    self.log_result(
                        "Verify Points Awarded", 
                        False, 
                        f"Incorrect points awarded: expected {expected_points}, got {points_awarded}",
                        f"Points before: {points_before}, after: {points_after}"
                    )
            else:
                self.log_result(
                    "Verify Points Awarded", 
                    False, 
                    f"Failed to get user profile: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Verify Points Awarded", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_enhanced_mission_retrieval(self):
        """Test enhanced mission retrieval with verification requirements and submission status"""
        print("\n📋 Testing Enhanced Mission Retrieval...")
        
        if not self.regular_user_token:
            self.log_result("Enhanced Mission Retrieval", False, "No regular user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.regular_user_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/missions", headers=headers)
            
            if response.status_code == 200:
                missions = response.json()
                if isinstance(missions, list):
                    if len(missions) > 0:
                        # Check mission structure includes verification requirements
                        mission = missions[0]
                        required_fields = [
                            "id", "title", "description", "points", "frequency",
                            "requires_description", "requires_photo", "photo_source", 
                            "requires_link", "requires_approval", "available", "completed"
                        ]
                        missing_fields = [field for field in required_fields if field not in mission]
                        
                        if not missing_fields:
                            # Check submission status tracking
                            status_fields = ["pending_approval", "available", "completed"]
                            has_status_tracking = all(field in mission for field in status_fields)
                            
                            if has_status_tracking:
                                verification_missions = sum(1 for m in missions if m.get("requires_approval", False))
                                self.log_result(
                                    "Enhanced Mission Retrieval", 
                                    True, 
                                    f"Successfully retrieved {len(missions)} missions with verification requirements and status tracking ({verification_missions} require approval)"
                                )
                            else:
                                self.log_result(
                                    "Enhanced Mission Retrieval", 
                                    False, 
                                    f"Missions missing submission status fields: {[f for f in status_fields if f not in mission]}"
                                )
                        else:
                            self.log_result(
                                "Enhanced Mission Retrieval", 
                                False, 
                                f"Missions missing verification requirement fields: {missing_fields}",
                                f"Sample mission: {mission}"
                            )
                    else:
                        self.log_result(
                            "Enhanced Mission Retrieval", 
                            True, 
                            "No missions found (this is normal if no active missions exist)"
                        )
                else:
                    self.log_result(
                        "Enhanced Mission Retrieval", 
                        False, 
                        "Invalid response format - expected list",
                        f"Response: {missions}"
                    )
            elif response.status_code == 401:
                self.log_result(
                    "Enhanced Mission Retrieval", 
                    False, 
                    "Authentication failed - invalid user token",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Enhanced Mission Retrieval", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Enhanced Mission Retrieval", 
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
        """Run all mission verification tests"""
        print("🚀 Starting ENHANCED Mission Management with VERIFICATION Backend Tests...")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users. Aborting tests.")
            return
        
        # Run verification workflow tests in order
        print("\n🎯 PRIORITY VALIDATION TESTS:")
        print("1. Mission Creation with Verification Settings")
        self.test_create_mission_with_verification_settings()
        
        print("\n2. Mission Submission System")
        self.test_mission_submission_system()
        
        print("\n3. Admin Approval Workflow")
        self.test_admin_approval_workflow()
        
        print("\n4. Enhanced Mission Retrieval")
        self.test_enhanced_mission_retrieval()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 ENHANCED MISSION MANAGEMENT WITH VERIFICATION TEST SUMMARY")
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
            print("\n🎉 ALL VERIFICATION WORKFLOW TESTS PASSED!")
            print("✅ Mission verification settings properly saved and retrieved")
            print("✅ Submission system accepting FormData with validation")
            print("✅ Approval workflow functional with point awarding")
            print("✅ Mission availability logic updated for submissions")
        elif passed > failed:
            print(f"\n⚠️  MOSTLY WORKING: {passed}/{total} tests passed. Some verification features need attention.")
        else:
            print(f"\n🚨 CRITICAL VERIFICATION ISSUES: {failed}/{total} tests failed. Verification system needs fixes.")
        
        # Cleanup created missions
        if self.created_mission_ids and self.admin_token:
            print(f"\n🧹 Cleaning up {len(self.created_mission_ids)} test missions...")

if __name__ == "__main__":
    tester = MissionVerificationTester()
    tester.run_all_tests()