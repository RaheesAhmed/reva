from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from config.supabase import get_supabase
from postgrest.exceptions import APIError
from fastapi.security import OAuth2PasswordBearer
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    message: str
    email: str
    user: Optional[Dict[str, Any]] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

def serialize_user(user) -> Dict[str, Any]:
    """Convert Supabase user object to a dictionary."""
    if not user:
        return None
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.user_metadata.get("full_name"),
        "email_verified": user.user_metadata.get("email_verified", False),
        "created_at": str(user.created_at) if user.created_at else None,
        "last_sign_in": str(user.last_sign_in_at) if user.last_sign_in_at else None
    }

@router.post("/register", response_model=AuthResponse)
async def register_user(request: UserRegisterRequest):
    # Explicitly use auth client for user operations
    supabase = get_supabase(auth=True)
    try:
        logger.info(f"Attempting to register user: {request.email}")
        
        # Register user with Supabase
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.name
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=400,
                detail="Failed to create user account"
            )
            
        logger.info(f"User registered successfully: {request.email}")
        
        # Return success message with email confirmation notice
        return {
            "message": "Registration successful! Please check your email to confirm your account before logging in.",
            "email": request.email,
            "user": serialize_user(auth_response.user)
        }
        
    except APIError as e:
        logger.error(f"Supabase API error during registration: {str(e)}")
        error_msg = str(e)
        
        # Handle rate limiting error
        if "security purposes" in error_msg and "30 seconds" in error_msg:
            raise HTTPException(
                status_code=429,  # Too Many Requests
                detail="Please wait 30 seconds before trying to register again."
            )
        # Handle existing user error
        elif "User already registered" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="An account with this email already exists. Please try logging in instead."
            )
        # Handle duplicate key error
        elif "duplicate key value" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="An account with this email already exists. Please try logging in instead."
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=error_msg
            )
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during registration: {str(e)}"
        )

@router.post("/login", response_model=AuthResponse)
async def login_user(request: UserLoginRequest):
    # Explicitly use auth client for user operations
    supabase = get_supabase(auth=True)
    try:
        logger.info(f"Attempting to login user: {request.email}")
        
        # Sign in user with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.session:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
            
        logger.info(f"User logged in successfully: {request.email}")
        
        return {
            "message": "Login successful!",
            "email": request.email,
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
            "user": serialize_user(auth_response.user)
        }
    except APIError as e:
        logger.error(f"Supabase API error during login: {str(e)}")
        error_msg = str(e)
        if "Email not confirmed" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="Please confirm your email address before logging in. Check your inbox for the confirmation link."
            )
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during login: {str(e)}"
        )

@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    supabase = get_supabase(auth=True)
    try:
        # Get current user
        user = supabase.auth.get_user(token)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
            
        return {
            "user": serialize_user(user.user)
        }
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

@router.post("/logout")
async def logout_user(token: str = Depends(oauth2_scheme)):
    # Explicitly use auth client for user operations
    supabase = get_supabase(auth=True)
    try:
        logger.info("Attempting to logout user")
        supabase.auth.sign_out()
        logger.info("User logged out successfully")
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during logout: {str(e)}"
        )
