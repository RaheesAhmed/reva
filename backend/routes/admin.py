from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from datetime import datetime
from config.supabase import get_supabase
from logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)

# Initialize Supabase admin client
supabase_admin = get_supabase(auth=False)

class User(BaseModel):
    id: str
    email: str
    role: str
    last_sign_in_at: str | None
    created_at: str
    updated_at: str
    status: str

class UsersResponse(BaseModel):
    users: List[User]

@router.get("/users", response_model=UsersResponse)
async def get_users():
    """Get all registered users."""
    try:
        # Fetch users from Supabase auth.users view
        result = supabase_admin.rpc(
            'get_users'
        ).execute()
        
        if not result.data:
            return {"users": []}

        # Transform the data to match our User model
        users = []
        for user_data in result.data:
            user = {
                "id": user_data["id"],
                "email": user_data["email"],
                "role": user_data["role"],
                "last_sign_in_at": user_data.get("last_sign_in_at"),
                "created_at": user_data["created_at"],
                "updated_at": user_data["updated_at"],
                "status": "active" if user_data.get("confirmed_at") else "inactive"
            }
            users.append(user)

        return {"users": users}
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 