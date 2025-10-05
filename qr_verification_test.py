#!/usr/bin/env python3
"""
QR Code URL Update Verification Test
Focus: Verify QR code now points to new popup URL and all corrections are working
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://puglia-club.preview.emergentagent.com/api"
TEST_USER_EMAIL = "test@desideridipuglia.com"
TEST_USER_PASSWORD = "test123"

class QRVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"{status} - {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate_test_user(self):
        """Authenticate test user and get token"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.test_user_id = data["user"]["id"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                self.log_result("Authentication", True, f"Successfully authenticated user: {TEST_USER_EMAIL}")
                return True
            else:
                self.log_result("Authentication", False, f"Failed to authenticate: {response.status_code}", 
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_qr_url_update_priority_maximum(self):
        """
        PRIORITY MAXIMUM: Test QR Code URL Update
        - GET /api/club-card (for test user)
        - Verify club_card_qr_url contains: "puglia-club.preview.emergentagent.com/profile?popup="
        - Should NOT contain: "desideridipuglia.com"
        - Endpoint should auto-update QR URL if still old
        """
        try:
            response = self.session.get(f"{BASE_URL}/club-card")
            
            if response.status_code == 200:
                data = response.json()
                qr_url = data.get("club_card_qr_url", "")
                
                # Check if QR URL contains new popup format
                expected_base = "puglia-club.preview.emergentagent.com/profile?popup="
                old_domain = "desideridipuglia.com"
                
                if expected_base in qr_url:
                    if old_domain not in qr_url:
                        if self.test_user_id and self.test_user_id in qr_url:
                            self.log_result("QR URL Update - PRIORITY MAXIMUM", True, 
                                          f"QR URL correctly updated to popup format: {qr_url}")
                            return True
                        else:
                            self.log_result("QR URL Update - PRIORITY MAXIMUM", False, 
                                          f"QR URL missing user ID: {qr_url}", 
                                          {"expected_user_id": self.test_user_id})
                    else:
                        self.log_result("QR URL Update - PRIORITY MAXIMUM", False, 
                                      f"QR URL still contains old domain: {qr_url}")
                else:
                    self.log_result("QR URL Update - PRIORITY MAXIMUM", False, 
                                  f"QR URL doesn't contain expected popup format: {qr_url}",
                                  {"expected_base": expected_base, "actual_url": qr_url})
                
                return False
                
            else:
                self.log_result("QR URL Update - PRIORITY MAXIMUM", False, 
                              f"Failed to get club card: {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("QR URL Update - PRIORITY MAXIMUM", False, f"Error testing QR URL: {str(e)}")
            return False
    
    def test_public_profile_popup_url(self):
        """
        Test Public Profile Popup URL
        - GET /api/club/profile/{user_id}
        - Verify data is served correctly for popup
        """
        if not self.test_user_id:
            self.log_result("Public Profile Popup", False, "No test user ID available")
            return False
            
        try:
            # Test public profile endpoint (no auth required)
            response = requests.get(f"{BASE_URL}/club/profile/{self.test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required fields for popup
                required_fields = ["user_info", "stats", "status", "prizes", "club_member"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    user_info = data.get("user_info", {})
                    stats = data.get("stats", {})
                    
                    if user_info.get("name") and stats.get("total_points") is not None:
                        self.log_result("Public Profile Popup", True, 
                                      f"Public profile data correctly served for popup. User: {user_info.get('name')}, Points: {stats.get('total_points')}")
                        return True
                    else:
                        self.log_result("Public Profile Popup", False, 
                                      "Missing essential user data in profile",
                                      {"user_info": user_info, "stats": stats})
                else:
                    self.log_result("Public Profile Popup", False, 
                                  f"Missing required fields: {missing_fields}",
                                  {"available_fields": list(data.keys())})
                
                return False
                
            else:
                self.log_result("Public Profile Popup", False, 
                              f"Failed to get public profile: {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Public Profile Popup", False, f"Error testing public profile: {str(e)}")
            return False
    
    def verify_backend_function_logic(self):
        """
        Verify Backend Function Logic
        - Check that generate_club_card_qr_url() generates correct popup URL format
        - URL should be: "https://puglia-club.preview.emergentagent.com/profile?popup={user_id}"
        """
        if not self.test_user_id:
            self.log_result("Backend Function Logic", False, "No test user ID available")
            return False
        
        # Expected URL format based on backend code
        expected_url = f"https://puglia-club.preview.emergentagent.com/profile?popup={self.test_user_id}"
        
        try:
            # Get club card data to verify the generated URL
            response = self.session.get(f"{BASE_URL}/club-card")
            
            if response.status_code == 200:
                data = response.json()
                actual_url = data.get("club_card_qr_url", "")
                
                if actual_url == expected_url:
                    self.log_result("Backend Function Logic", True, 
                                  f"Backend function generates correct popup URL: {actual_url}")
                    return True
                else:
                    self.log_result("Backend Function Logic", False, 
                                  f"Backend function generates incorrect URL",
                                  {"expected": expected_url, "actual": actual_url})
                    return False
            else:
                self.log_result("Backend Function Logic", False, 
                              f"Failed to verify backend function: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Backend Function Logic", False, f"Error verifying backend function: {str(e)}")
            return False
    
    def test_automatic_qr_update_mechanism(self):
        """
        Test Automatic QR Update Mechanism
        - Verify that old QR URLs are automatically updated on first /api/club-card call
        """
        try:
            # Make multiple calls to ensure consistency
            first_response = self.session.get(f"{BASE_URL}/club-card")
            second_response = self.session.get(f"{BASE_URL}/club-card")
            
            if first_response.status_code == 200 and second_response.status_code == 200:
                first_data = first_response.json()
                second_data = second_response.json()
                
                first_url = first_data.get("club_card_qr_url", "")
                second_url = second_data.get("club_card_qr_url", "")
                
                # URLs should be consistent and in new format
                if first_url == second_url and "puglia-club.preview.emergentagent.com/profile?popup=" in first_url:
                    self.log_result("Automatic QR Update Mechanism", True, 
                                  "QR URL update mechanism working consistently")
                    return True
                else:
                    self.log_result("Automatic QR Update Mechanism", False, 
                                  "QR URL inconsistent between calls",
                                  {"first_call": first_url, "second_call": second_url})
                    return False
            else:
                self.log_result("Automatic QR Update Mechanism", False, 
                              "Failed to test update mechanism")
                return False
                
        except Exception as e:
            self.log_result("Automatic QR Update Mechanism", False, f"Error testing update mechanism: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all QR verification tests"""
        print("🔍 Starting QR Code URL Update Verification Tests")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate_test_user():
            print("❌ Cannot proceed without authentication")
            return False
        
        print("\n📋 Running Priority Tests:")
        
        # Priority Maximum Test
        test1_success = self.test_qr_url_update_priority_maximum()
        
        # Supporting Tests
        test2_success = self.test_public_profile_popup_url()
        test3_success = self.verify_backend_function_logic()
        test4_success = self.test_automatic_qr_update_mechanism()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY:")
        
        total_tests = len(self.results) - 1  # Exclude authentication
        passed_tests = sum(1 for r in self.results[1:] if "✅ PASS" in r["status"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        
        # Critical test results
        if test1_success:
            print("\n🎯 PRIORITY MAXIMUM TEST: ✅ PASSED")
            print("   QR Code URL successfully updated to popup format!")
        else:
            print("\n🎯 PRIORITY MAXIMUM TEST: ❌ FAILED")
            print("   QR Code URL update needs attention!")
        
        # Overall result
        all_critical_passed = test1_success and test2_success and test3_success
        
        if all_critical_passed:
            print("\n🌟 OVERALL RESULT: ✅ ALL CRITICAL TESTS PASSED")
            print("   QR Code corrections are working correctly!")
        else:
            print("\n⚠️  OVERALL RESULT: ❌ SOME CRITICAL TESTS FAILED")
            print("   QR Code system needs fixes!")
        
        return all_critical_passed

def main():
    """Main test execution"""
    tester = QRVerificationTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()