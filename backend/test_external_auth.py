#!/usr/bin/env python3
"""
Simple test script to verify external authentication implementation
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'open_webui'))

from open_webui.utils.external_auth import (
    send_otp,
    verify_otp,
    authenticate_with_google,
    extract_user_info_from_external_response,
    build_full_name
)


async def test_external_auth():
    """Test the external authentication functions"""
    
    print("Testing External Authentication Implementation")
    print("=" * 50)
    
    # Test build_full_name function
    print("\n1. Testing build_full_name function:")
    name1 = build_full_name("John", "Doe")
    name2 = build_full_name("Jane")
    print(f"   Full name with last name: {name1}")
    print(f"   Full name without last name: {name2}")
    
    # Test extract_user_info_from_external_response function
    print("\n2. Testing extract_user_info_from_external_response function:")
    mock_user_data = {
        "id": "ext_123",
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "profilePic": "https://example.com/avatar.jpg",
        "authProvider": "GOOGLE",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z"
    }
    
    user_info = extract_user_info_from_external_response(mock_user_data)
    print(f"   Extracted user info: {user_info}")
    
    # Test send_otp function (this will make a real API call)
    print("\n3. Testing send_otp function:")
    try:
        response = await send_otp("+1234567890")
        print(f"   Send OTP response: {response}")
    except Exception as e:
        print(f"   Send OTP error: {e}")
    
    print("\nExternal authentication implementation test completed!")
    print("Note: The actual API calls will fail if the external server is not available.")


if __name__ == "__main__":
    asyncio.run(test_external_auth()) 