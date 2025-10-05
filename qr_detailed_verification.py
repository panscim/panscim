#!/usr/bin/env python3
"""
Detailed QR Code URL Verification
Additional verification to ensure old URLs are completely replaced
"""

import requests
import json

# Configuration
BASE_URL = "https://puglia-club.preview.emergentagent.com/api"
TEST_USER_EMAIL = "test@desideridipuglia.com"
TEST_USER_PASSWORD = "test123"

def authenticate_and_get_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        return data["access_token"], data["user"]["id"]
    return None, None

def test_qr_url_details():
    """Test detailed QR URL verification"""
    token, user_id = authenticate_and_get_token()
    if not token:
        print("❌ Authentication failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 DETAILED QR URL VERIFICATION")
    print("=" * 50)
    
    # Test club card endpoint
    response = requests.get(f"{BASE_URL}/club-card", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        qr_url = data.get("club_card_qr_url", "")
        
        print(f"📋 Club Card Data:")
        print(f"   User: {data.get('name')}")
        print(f"   Username: {data.get('username')}")
        print(f"   Club Code: {data.get('club_card_code')}")
        print(f"   QR URL: {qr_url}")
        print(f"   User ID: {user_id}")
        
        # Detailed URL analysis
        print(f"\n🔍 URL Analysis:")
        print(f"   ✅ Contains new domain: {'puglia-club.preview.emergentagent.com' in qr_url}")
        print(f"   ✅ Contains popup parameter: {'?popup=' in qr_url}")
        print(f"   ✅ Contains user ID: {user_id in qr_url}")
        print(f"   ✅ Does NOT contain old domain: {'desideridipuglia.com' not in qr_url}")
        
        # Expected vs actual
        expected_url = f"https://puglia-club.preview.emergentagent.com/profile?popup={user_id}"
        print(f"\n📊 URL Comparison:")
        print(f"   Expected: {expected_url}")
        print(f"   Actual:   {qr_url}")
        print(f"   Match: {expected_url == qr_url}")
        
        # Test public profile endpoint
        print(f"\n🌐 Testing Public Profile Endpoint:")
        public_response = requests.get(f"{BASE_URL}/club/profile/{user_id}")
        
        if public_response.status_code == 200:
            public_data = public_response.json()
            print(f"   ✅ Public profile accessible")
            print(f"   User Info: {public_data.get('user_info', {}).get('name')}")
            print(f"   Current Points: {public_data.get('stats', {}).get('current_points')}")
            print(f"   Total Points: {public_data.get('stats', {}).get('total_points')}")
            print(f"   Current Rank: {public_data.get('stats', {}).get('current_rank')}")
            print(f"   Club Member: {public_data.get('club_member')}")
        else:
            print(f"   ❌ Public profile failed: {public_response.status_code}")
        
        # Test legacy QR endpoint
        print(f"\n🔗 Testing Legacy QR Endpoint:")
        legacy_response = requests.get(f"{BASE_URL}/club-card/qr/{user_id}")
        
        if legacy_response.status_code == 200:
            print(f"   ✅ Legacy QR endpoint working (redirects to public profile)")
        else:
            print(f"   ❌ Legacy QR endpoint failed: {legacy_response.status_code}")
        
    else:
        print(f"❌ Failed to get club card: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_qr_url_details()