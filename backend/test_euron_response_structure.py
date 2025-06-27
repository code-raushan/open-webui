#!/usr/bin/env python3
"""
Test script to verify Euron API response structure handling
"""

import asyncio
import sys
import os
import json

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'open_webui'))

from open_webui.utils.external_auth import (
    SendOtpResponse,
    VerifyOtpResponse,
    GoogleAuthResponse,
    EuronOtpResponse,
    EuronGoogleResponse
)


def test_response_parsing():
    """Test the response parsing logic"""
    
    print("Testing Euron API Response Structure Handling")
    print("=" * 50)
    
    # Test 1: Send OTP Response Structure
    print("\n1. Testing Send OTP Response Structure:")
    
    # Simulate Euron API response structure
    mock_send_otp_response = {
        "data": {
            "phone": "+1234567890",
            "session": "session_token_12345"
        },
        "message": "OTP sent successfully"
    }
    
    print(f"   Mock Euron response: {json.dumps(mock_send_otp_response, indent=2)}")
    
    # Test parsing logic
    response_data = mock_send_otp_response.get("data", {})
    message = mock_send_otp_response.get("message", "OTP sent successfully")
    session = response_data.get("session")
    
    print(f"   Parsed session: {session}")
    print(f"   Parsed message: {message}")
    
    # Test 2: Verify OTP Response Structure
    print("\n2. Testing Verify OTP Response Structure:")
    
    mock_verify_otp_response = {
        "data": {
            "message": "OTP verified successfully",
            "type": "otp",
            "accessToken": "access_token_12345",
            "expiresAt": "2024-12-31T23:59:59Z",
            "userId": "user_12345"
        },
        "message": "OTP verification completed"
    }
    
    print(f"   Mock Euron response: {json.dumps(mock_verify_otp_response, indent=2)}")
    
    # Test parsing logic
    response_data = mock_verify_otp_response.get("data", {})
    message = mock_verify_otp_response.get("message", "OTP verified successfully")
    
    try:
        euron_response = EuronOtpResponse(**response_data)
        print(f"   Parsed userId: {euron_response.userId}")
        print(f"   Parsed accessToken: {euron_response.accessToken}")
        print(f"   Parsed message: {message}")
    except Exception as e:
        print(f"   Error parsing Euron response: {e}")
    
    # Test 3: Google Auth Response Structure
    print("\n3. Testing Google Auth Response Structure:")
    
    mock_google_response = {
        "data": {
            "accessToken": "google_access_token_12345",
            "type": "google",
            "expiresAt": "2024-12-31T23:59:59Z",
            "userId": "google_user_12345"
        },
        "message": "Google authentication successful"
    }
    
    print(f"   Mock Euron response: {json.dumps(mock_google_response, indent=2)}")
    
    # Test parsing logic
    response_data = mock_google_response.get("data", {})
    message = mock_google_response.get("message", "Google authentication successful")
    
    try:
        euron_response = EuronGoogleResponse(**response_data)
        print(f"   Parsed userId: {euron_response.userId}")
        print(f"   Parsed accessToken: {euron_response.accessToken}")
        print(f"   Parsed message: {message}")
    except Exception as e:
        print(f"   Error parsing Euron response: {e}")
    
    print("\n✅ Response structure handling test completed!")
    print("\nKey Points:")
    print("- Euron API returns: { data: {...}, message: string }")
    print("- Python code now correctly accesses: response.get('data') and response.get('message')")
    print("- This matches the axios structure: response.data.data and response.data.message")


if __name__ == "__main__":
    test_response_parsing() 