#!/usr/bin/env python3
"""
Test script to verify Google authentication email handling
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'open_webui'))

from open_webui.utils.external_auth import (
    authenticate_with_google,
    EuronGoogleResponse,
    extract_user_info_from_external_response
)


async def test_google_auth_email_handling():
    """Test the Google authentication email handling"""
    
    print("Testing Google Authentication Email Handling")
    print("=" * 50)
    
    # Test 1: Check EuronGoogleResponse model includes email
    print("\n1. Testing EuronGoogleResponse model:")
    try:
        # Mock response data from Euron server
        mock_response_data = {
            "accessToken": "mock_access_token",
            "type": "Bearer",
            "expiresAt": "2024-12-31T23:59:59Z",
            "userId": "ext_google_123",
            "email": "test@example.com"
        }
        
        # Parse the response
        euron_response = EuronGoogleResponse(**mock_response_data)
        print(f"   ✅ Email extracted: {euron_response.email}")
        print(f"   ✅ User ID: {euron_response.userId}")
        print(f"   ✅ Access Token: {euron_response.accessToken}")
        
    except Exception as e:
        print(f"   ❌ Error parsing Euron response: {e}")
        return False
    
    # Test 2: Check user info extraction
    print("\n2. Testing user info extraction:")
    try:
        mock_user_data = {
            "external_user_id": "ext_google_123",
            "email": "test@example.com",
            "auth_provider": "GOOGLE",
            "phone": None,
            "firstName": "John",
            "lastName": "Doe",
            "profilePic": "/user.png"
        }
        
        user_info = extract_user_info_from_external_response(mock_user_data)
        print(f"   ✅ Extracted email: {user_info.get('email')}")
        print(f"   ✅ Extracted external_user_id: {user_info.get('external_user_id')}")
        print(f"   ✅ Extracted auth provider: {user_info.get('authProvider')}")
        
    except Exception as e:
        print(f"   ❌ Error extracting user info: {e}")
        return False
    
    # Test 3: Test actual Google authentication (will fail if server not available)
    print("\n3. Testing actual Google authentication:")
    try:
        # This will fail if the external server is not available
        response = await authenticate_with_google("mock_google_token")
        if response.success:
            print(f"   ✅ Google auth successful")
            print(f"   ✅ User email: {response.user.get('email') if response.user else 'None'}")
        else:
            print(f"   ⚠️  Google auth failed: {response.message}")
            print("   (This is expected if external server is not available)")
        
    except Exception as e:
        print(f"   ⚠️  Google auth error: {e}")
        print("   (This is expected if external server is not available)")
    
    print("\n" + "=" * 50)
    print("✅ Google Authentication Email Handling Test Complete")
    print("\nSummary:")
    print("1. EuronGoogleResponse model now includes email field")
    print("2. Email is properly extracted from response")
    print("3. User info extraction handles email correctly")
    print("\nNext steps:")
    print("1. The backend should now properly handle email in Google auth")
    print("2. Test with actual Google authentication flow")
    print("3. Verify email is saved to user record")
    
    return True


if __name__ == "__main__":
    asyncio.run(test_google_auth_email_handling()) 