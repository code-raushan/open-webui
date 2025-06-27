#!/usr/bin/env python3
"""
Test script to verify OTP frontend integration
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8080"
API_BASE_URL = f"{BASE_URL}/api"

async def test_backend_config():
    """Test that the backend config includes external auth features"""
    print("Testing backend config...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/config") as response:
            if response.status == 200:
                config = await response.json()
                features = config.get("features", {})
                
                print(f"✓ Backend config endpoint accessible")
                print(f"  - enable_external_auth: {features.get('enable_external_auth', False)}")
                print(f"  - external_auth_enable_otp: {features.get('external_auth_enable_otp', False)}")
                
                return features.get('enable_external_auth', False) and features.get('external_auth_enable_otp', False)
            else:
                print(f"✗ Backend config endpoint failed: {response.status}")
                return False

async def test_send_otp_endpoint():
    """Test the send OTP endpoint"""
    print("\nTesting send OTP endpoint...")
    
    # Test data
    test_phone = "1234567890"  # Use a test phone number
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/auths/external/send-otp",
            json={"phone": test_phone},
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✓ Send OTP endpoint working")
                print(f"  - Success: {data.get('success', False)}")
                print(f"  - Message: {data.get('message', 'N/A')}")
                print(f"  - Session: {data.get('session', 'N/A')}")
                return data.get('success', False), data.get('session')
            else:
                error_data = await response.json()
                print(f"✗ Send OTP endpoint failed: {response.status}")
                print(f"  - Error: {error_data}")
                return False, None

async def test_verify_otp_endpoint():
    """Test the verify OTP endpoint"""
    print("\nTesting verify OTP endpoint...")
    
    # First send OTP to get session
    success, session = await test_send_otp_endpoint()
    if not success or not session:
        print("✗ Cannot test verify OTP without successful send OTP")
        return False
    
    # Test data
    test_phone = "1234567890"
    test_code = "123456"  # Use a test code
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/auths/external/verify-otp",
            json={
                "phone": test_phone,
                "code": test_code,
                "session": session
            },
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✓ Verify OTP endpoint working")
                print(f"  - Token: {data.get('token', 'N/A')[:20]}...")
                print(f"  - User ID: {data.get('id', 'N/A')}")
                print(f"  - Name: {data.get('name', 'N/A')}")
                return True
            else:
                error_data = await response.json()
                print(f"✗ Verify OTP endpoint failed: {response.status}")
                print(f"  - Error: {error_data}")
                return False

async def test_frontend_routes():
    """Test that frontend routes are accessible"""
    print("\nTesting frontend routes...")
    
    routes_to_test = [
        "/auth",
        "/",
    ]
    
    async with aiohttp.ClientSession() as session:
        for route in routes_to_test:
            async with session.get(f"{BASE_URL}{route}") as response:
                if response.status == 200:
                    print(f"✓ Frontend route {route} accessible")
                else:
                    print(f"✗ Frontend route {route} failed: {response.status}")

async def main():
    """Main test function"""
    print("🧪 Testing OTP Frontend Integration")
    print("=" * 50)
    
    # Test backend config
    config_ok = await test_backend_config()
    
    if not config_ok:
        print("\n⚠️  External auth not enabled in backend config")
        print("   Make sure ENABLE_EXTERNAL_AUTH=true and EXTERNAL_AUTH_ENABLE_OTP=true")
        return
    
    # Test OTP endpoints
    await test_send_otp_endpoint()
    await test_verify_otp_endpoint()
    
    # Test frontend routes
    await test_frontend_routes()
    
    print("\n" + "=" * 50)
    print("✅ OTP Frontend Integration Test Complete")
    print("\nNext steps:")
    print("1. Start the frontend development server")
    print("2. Navigate to /auth")
    print("3. Click 'Continue with OTP'")
    print("4. Enter a phone number and test the OTP flow")

if __name__ == "__main__":
    asyncio.run(main()) 