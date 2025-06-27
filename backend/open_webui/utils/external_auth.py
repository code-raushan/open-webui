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


class VerifyOtpResponse(BaseModel):
    success: bool
    message: str
    user: Optional[Dict[str, Any]] = None
    token: Optional[str] = None


class GoogleAuthRequest(BaseModel):
    googleToken: str


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
                    return SendOtpResponse(
                        success=True,
                        message=data.get("message", "OTP sent successfully"),
                        session=data.get("session")
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
    Verify OTP with the external auth server
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
                    return VerifyOtpResponse(
                        success=True,
                        message=data.get("message", "OTP verified successfully"),
                        user=data.get("user"),
                        token=data.get("token")
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
    Authenticate with Google via external auth server
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
                    return GoogleAuthResponse(
                        success=True,
                        message=data.get("message", "Google authentication successful"),
                        user=data.get("user"),
                        token=data.get("token")
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
        "external_user_id": user_data.get("id"),
        "firstName": user_data.get("firstName"),
        "lastName": user_data.get("lastName"),
        "email": user_data.get("email"),
        "phone": user_data.get("phone"),
        "profilePic": user_data.get("profilePic"),
        "authProvider": user_data.get("authProvider", "CREDENTIALS"),
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