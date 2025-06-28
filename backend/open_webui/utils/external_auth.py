import logging
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from pydantic import BaseModel

from open_webui.env import SRC_LOG_LEVELS
from open_webui.config import EXTERNAL_AUTH_BASE_URL, EXTERNAL_AUTH_TIMEOUT

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MAIN"])


class SendOtpRequest(BaseModel):
    phone: str
    hash: Optional[str] = None


class SendOtpResponse(BaseModel):
    success: bool
    message: str
    session: Optional[str] = None


class VerifyOtpRequest(BaseModel):
    phone: str
    code: str
    session: str


# Euron server response structure for OTP verification
class EuronOtpResponse(BaseModel):
    message: str
    type: str
    accessToken: str
    expiresAt: str  # Date string
    userId: str


class VerifyOtpResponse(BaseModel):
    success: bool
    message: str
    user: Optional[Dict[str, Any]] = None
    token: Optional[str] = None


class GoogleAuthRequest(BaseModel):
    googleToken: str


# Euron server response structure for Google auth
class EuronGoogleResponse(BaseModel):
    accessToken: str
    type: str
    expiresAt: str  # Date string
    userId: str
    email: str
    firstName: str
    lastName: Optional[str] = None


class GoogleAuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[Dict[str, Any]] = None
    token: Optional[str] = None


async def send_otp(phone: str, hash: Optional[str] = None, affiliate_code: Optional[str] = None) -> SendOtpResponse:
    """
    Send OTP to the specified phone number via external auth server
    """
    try:
        url = f"{EXTERNAL_AUTH_BASE_URL.value}/send-otp"
        params = {}
        if affiliate_code:
            params["ref"] = affiliate_code
            
        payload = {"phone": phone}
        if hash:
            payload["hash"] = hash
            
        timeout = aiohttp.ClientTimeout(total=EXTERNAL_AUTH_TIMEOUT.value)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    # Euron server returns data in response.data.data structure
                    # response.data = { data: { phone, session }, message: string }
                    response_data = data.get("data", {})
                    message = data.get("message", "OTP sent successfully")
                    
                    return SendOtpResponse(
                        success=True,
                        message=message,
                        session=response_data.get("session")
                    )
                else:
                    error_data = await response.json()
                    return SendOtpResponse(
                        success=False,
                        message=error_data.get("message", "Failed to send OTP")
                    )
    except Exception as e:
        log.error(f"Error sending OTP: {str(e)}")
        return SendOtpResponse(
            success=False,
            message=f"Error sending OTP: {str(e)}"
        )


async def verify_otp(phone: str, code: str, session: str, affiliate_code: Optional[str] = None) -> VerifyOtpResponse:
    """
    Verify OTP with the external auth server (Euron).
    - Returns user data with only phone and external_user_id set.
    - All info is extracted from response.data.data.
    """
    try:
        url = f"{EXTERNAL_AUTH_BASE_URL.value}/verify-otp"
        params = {}
        if affiliate_code:
            params["ref"] = affiliate_code
            
        payload = {
            "phone": phone,
            "code": code,
            "session": session
        }
        
        timeout = aiohttp.ClientTimeout(total=EXTERNAL_AUTH_TIMEOUT.value)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    # Euron server returns data in response.data.data structure
                    # response.data = { data: { message, type, accessToken, expiresAt, userId }, message: string }
                    response_data = data.get("data", {})
                    message = data.get("message", "OTP verified successfully")
                    
                    # Parse the Euron response structure
                    euron_response = EuronOtpResponse(**response_data)
                    
                    # Create user data for OTP-based auth (phone only)
                    user_data = {
                        "external_user_id": euron_response.userId,
                        "phone": phone,
                        "auth_provider": "OTP",
                        "email": None,  # OTP users don't have email
                        "firstName": None,
                        "lastName": None,
                        "profilePic": "/user.png"
                    }
                    
                    return VerifyOtpResponse(
                        success=True,
                        message=message,
                        user=user_data,
                        token=euron_response.accessToken
                    )
                else:
                    error_data = await response.json()
                    return VerifyOtpResponse(
                        success=False,
                        message=error_data.get("message", "Failed to verify OTP")
                    )
    except Exception as e:
        log.error(f"Error verifying OTP: {str(e)}")
        return VerifyOtpResponse(
            success=False,
            message=f"Error verifying OTP: {str(e)}"
        )


async def authenticate_with_google(google_token: str, affiliate_code: Optional[str] = None) -> GoogleAuthResponse:
    """
    Authenticate with Google via external auth server (Euron).
    - Returns user data with only email and external_user_id set.
    Authenticate with Google via external auth server
    Returns Euron server response structure
    """
    try:
        url = f"{EXTERNAL_AUTH_BASE_URL.value}/google"
        params = {}
        if affiliate_code:
            params["ref"] = affiliate_code
            
        payload = {"googleToken": google_token}
        
        timeout = aiohttp.ClientTimeout(total=EXTERNAL_AUTH_TIMEOUT.value)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    # Euron server returns data in response.data.data structure
                    # response.data = { data: { accessToken, type, expiresAt, userId }, message: string }
                    response_data = data.get("data", {})
                    message = data.get("message", "Google authentication successful")
                    
                    # Parse the Euron response structure
                    euron_response = EuronGoogleResponse(**response_data)
                    
                    # Create user data for Google-based auth with email
                    user_data = {
                        "external_user_id": euron_response.userId,
                        "auth_provider": "GOOGLE",
                        "phone": None,  # Google users don't have phone
                        "email": euron_response.email,  # Extract email from response
                        "firstName": euron_response.firstName,
                        "lastName": euron_response.lastName,
                        "profilePic": "/user.png"
                    }
                    
                    return GoogleAuthResponse(
                        success=True,
                        message=message,
                        user=user_data,
                        token=euron_response.accessToken
                    )
                else:
                    error_data = await response.json()
                    return GoogleAuthResponse(
                        success=False,
                        message=error_data.get("message", "Failed to authenticate with Google")
                    )
    except Exception as e:
        log.error(f"Error authenticating with Google: {str(e)}")
        return GoogleAuthResponse(
            success=False,
            message=f"Error authenticating with Google: {str(e)}"
        )


def extract_user_info_from_external_response(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and map user information from external auth server response
    """
    return {
        "external_user_id": user_data.get("external_user_id"),
        "firstName": user_data.get("firstName"),
        "lastName": user_data.get("lastName"),
        "email": user_data.get("email"),
        "phone": user_data.get("phone"),
        "profilePic": user_data.get("profilePic"),
        "authProvider": user_data.get("auth_provider", "CREDENTIALS"),
        "createdAt": user_data.get("createdAt"),
        "updatedAt": user_data.get("updatedAt"),
    }


def build_full_name(first_name: str, last_name: Optional[str] = None) -> str:
    """
    Build full name from first and last name
    """
    if last_name:
        return f"{first_name} {last_name}".strip()
    return first_name 