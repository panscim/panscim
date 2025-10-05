#!/usr/bin/env python3
"""
Backend Testing Suite for Desideri di Puglia Club - Email Admin Functionality
Tests the newly implemented Email Admin features including SMTP integration.
"""

import requests
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://puglia-loyalty.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class EmailAdminTester:
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
        """Create or login test users (admin and regular user)"""
        print("\n🔧 Setting up test users...")
        
        # Try to create admin user
        admin_data = {
            "name": "Admin Tester",
            "username": "admin_test_email",
            "email": "admin.test.email@example.com",
            "password": "AdminTest123!",
            "country": "Italy"
        }
        
        try:
            # Try registration first
            response = requests.post(f"{API_BASE}/auth/register", json=admin_data)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.admin_user_id = data["user"]["id"]
                
                # Make user admin in database (this would normally be done manually)
                # For testing, we'll assume the user is already admin or we'll handle the 403 error
                print("✅ Admin user created successfully")
            else:
                # Try login if user already exists
                login_data = {"email": admin_data["email"], "password": admin_data["password"]}
                response = requests.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.admin_token = data["access_token"]
                    self.admin_user_id = data["user"]["id"]
                    print("✅ Admin user logged in successfully")
                else:
                    print(f"❌ Failed to create/login admin user: {response.text}")
                    return False
        except Exception as e:
            print(f"❌ Error setting up admin user: {str(e)}")
            return False
        
        # Create regular user for testing
        user_data = {
            "name": "Regular User",
            "username": "regular_test_email",
            "email": "regular.test.email@example.com", 
            "password": "RegularTest123!",
            "country": "Italy"
        }
        
        try:
            response = requests.post(f"{API_BASE}/auth/register", json=user_data)
            if response.status_code == 200:
                data = response.json()
                self.regular_user_token = data["access_token"]
                self.test_user_id = data["user"]["id"]
                print("✅ Regular user created successfully")
            else:
                # Try login if user already exists
                login_data = {"email": user_data["email"], "password": user_data["password"]}
                response = requests.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.regular_user_token = data["access_token"]
                    self.test_user_id = data["user"]["id"]
                    print("✅ Regular user logged in successfully")
                else:
                    print(f"❌ Failed to create/login regular user: {response.text}")
                    return False
        except Exception as e:
            print(f"❌ Error setting up regular user: {str(e)}")
            return False
        
        return True
    
    def test_smtp_configuration(self):
        """Test SMTP configuration with test email"""
        print("\n📧 Testing SMTP Configuration...")
        
        if not self.admin_token:
            self.log_result("SMTP Configuration Test", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        test_email = "test.recipient@example.com"  # Using a test email
        
        try:
            response = requests.post(
                f"{API_BASE}/admin/email/test",
                params={"test_email": test_email},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "SMTP Configuration Test", 
                    True, 
                    f"SMTP test successful: {data.get('message', 'Email sent')}"
                )
            elif response.status_code == 403:
                self.log_result(
                    "SMTP Configuration Test", 
                    False, 
                    "Access denied - user may not have admin privileges",
                    f"Response: {response.text}"
                )
            elif response.status_code == 500:
                self.log_result(
                    "SMTP Configuration Test", 
                    False, 
                    "SMTP configuration error - email sending failed",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "SMTP Configuration Test", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "SMTP Configuration Test", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_get_users_list(self):
        """Test getting users list for email selection"""
        print("\n👥 Testing Users List Retrieval...")
        
        if not self.admin_token:
            self.log_result("Users List Test", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/admin/users/list", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Check if users have required fields
                    user = data[0]
                    required_fields = ["id", "name", "email", "current_points", "level"]
                    missing_fields = [field for field in required_fields if field not in user]
                    
                    if not missing_fields:
                        self.log_result(
                            "Users List Test", 
                            True, 
                            f"Successfully retrieved {len(data)} users with all required fields"
                        )
                    else:
                        self.log_result(
                            "Users List Test", 
                            False, 
                            f"Users missing required fields: {missing_fields}",
                            f"Sample user: {user}"
                        )
                else:
                    self.log_result(
                        "Users List Test", 
                        False, 
                        "No users returned or invalid format",
                        f"Response: {data}"
                    )
            elif response.status_code == 403:
                self.log_result(
                    "Users List Test", 
                    False, 
                    "Access denied - user may not have admin privileges",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Users List Test", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Users List Test", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_send_email_with_templates(self):
        """Test sending email with template variables"""
        print("\n📨 Testing Email Sending with Template Variables...")
        
        if not self.admin_token or not self.test_user_id:
            self.log_result("Email Send Test", False, "Missing admin token or test user ID")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Email with template variables
        email_data = {
            "recipients": [self.test_user_id],
            "subject": "🌿 Test Email with Template Variables",
            "body": """
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Ciao {{user_name}}!</h2>
                <p>Hai attualmente <strong>{{user_points}}</strong> punti.</p>
                <p>Il tuo livello attuale è: <strong>{{user_level}}</strong></p>
                <p>Tema del mese: {{month_theme}}</p>
                <p>Punti necessari per entrare nella top 3: {{points_to_top3}}</p>
                <p>Questo è un test dell'integrazione email! 🌿</p>
            </body>
            </html>
            """
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/admin/email/send",
                json=email_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                if "successo" in message.lower() or "success" in message.lower():
                    self.log_result(
                        "Email Send Test", 
                        True, 
                        f"Email sent successfully: {message}"
                    )
                else:
                    self.log_result(
                        "Email Send Test", 
                        False, 
                        f"Email sending may have failed: {message}"
                    )
            elif response.status_code == 403:
                self.log_result(
                    "Email Send Test", 
                    False, 
                    "Access denied - user may not have admin privileges",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Email Send Test", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Email Send Test", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_email_logs(self):
        """Test email logs retrieval"""
        print("\n📋 Testing Email Logs Retrieval...")
        
        if not self.admin_token:
            self.log_result("Email Logs Test", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{API_BASE}/admin/email/logs", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check log structure
                        log = data[0]
                        required_fields = ["id", "recipients", "subject", "sent_at", "status", "recipient_count"]
                        missing_fields = [field for field in required_fields if field not in log]
                        
                        if not missing_fields:
                            self.log_result(
                                "Email Logs Test", 
                                True, 
                                f"Successfully retrieved {len(data)} email logs with all required fields"
                            )
                        else:
                            self.log_result(
                                "Email Logs Test", 
                                False, 
                                f"Email logs missing required fields: {missing_fields}",
                                f"Sample log: {log}"
                            )
                    else:
                        self.log_result(
                            "Email Logs Test", 
                            True, 
                            "No email logs found (this is normal for new installations)"
                        )
                else:
                    self.log_result(
                        "Email Logs Test", 
                        False, 
                        "Invalid response format - expected list",
                        f"Response: {data}"
                    )
            elif response.status_code == 403:
                self.log_result(
                    "Email Logs Test", 
                    False, 
                    "Access denied - user may not have admin privileges",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Email Logs Test", 
                    False, 
                    f"Unexpected response status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Email Logs Test", 
                False, 
                f"Request failed: {str(e)}"
            )
    
    def test_authentication_enforcement(self):
        """Test that email endpoints require admin authentication"""
        print("\n🔒 Testing Authentication & Authorization...")
        
        # Test without token
        try:
            response = requests.get(f"{API_BASE}/admin/email/logs")
            if response.status_code == 401:
                self.log_result(
                    "No Token Auth Test", 
                    True, 
                    "Correctly rejected request without authentication token"
                )
            else:
                self.log_result(
                    "No Token Auth Test", 
                    False, 
                    f"Should have returned 401, got {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "No Token Auth Test", 
                False, 
                f"Request failed: {str(e)}"
            )
        
        # Test with regular user token (should fail with 403)
        if self.regular_user_token:
            headers = {"Authorization": f"Bearer {self.regular_user_token}"}
            try:
                response = requests.get(f"{API_BASE}/admin/email/logs", headers=headers)
                if response.status_code == 403:
                    self.log_result(
                        "Regular User Auth Test", 
                        True, 
                        "Correctly rejected regular user access to admin endpoints"
                    )
                else:
                    self.log_result(
                        "Regular User Auth Test", 
                        False, 
                        f"Should have returned 403, got {response.status_code}",
                        f"Response: {response.text}"
                    )
            except Exception as e:
                self.log_result(
                    "Regular User Auth Test", 
                    False, 
                    f"Request failed: {str(e)}"
                )
    
    def run_all_tests(self):
        """Run all email admin tests"""
        print("🚀 Starting Email Admin Backend Tests...")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users. Aborting tests.")
            return
        
        # Run tests
        self.test_authentication_enforcement()
        self.test_get_users_list()
        self.test_smtp_configuration()
        self.test_send_email_with_templates()
        self.test_email_logs()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
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
            print("\n🎉 ALL EMAIL ADMIN TESTS PASSED! Email functionality is working correctly.")
        elif passed > failed:
            print(f"\n⚠️  MOSTLY WORKING: {passed}/{total} tests passed. Some issues need attention.")
        else:
            print(f"\n🚨 CRITICAL ISSUES: {failed}/{total} tests failed. Email functionality needs fixes.")

if __name__ == "__main__":
    tester = EmailAdminTester()
    tester.run_all_tests()