from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import os
import sys
from pathlib import Path
from routes.user_auth import oauth2_scheme, get_current_user
from config.supabase import get_supabase
import logging

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response Models
class AnalyticsResponse(BaseModel):
    tool_usage: Dict[str, int]
    query_timeline: List[Dict[str, Any]]
    popular_properties: List[Dict[str, Any]]
    economic_indicators: List[Dict[str, Any]]

class SavedItemCreate(BaseModel):
    item_type: str
    title: str
    content: Dict[str, Any]
    tags: List[str] = []

class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    type: str
    read: bool
    created_at: datetime

# Analytics Endpoints
@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(current_user: Dict = Depends(get_current_user)):
    """Get analytics data for the dashboard."""
    try:
        logger.info(f"Fetching analytics for user {current_user['id']}")
        supabase = get_supabase(auth=False)
        
        # Initialize default response
        response = {
            "tool_usage": {},
            "query_timeline": [],
            "popular_properties": [],
            "economic_indicators": []
        }
        
        try:
            # Get tool usage statistics
            tool_usage_result = await supabase.rpc(
                'get_tool_usage_stats',
                {'user_id': current_user["id"]}
            ).execute()
            
            if tool_usage_result and hasattr(tool_usage_result, 'data'):
                response["tool_usage"] = tool_usage_result.data or {}
            else:
                # Fallback to direct query if RPC fails
                logger.warning("RPC failed, falling back to direct query")
                tool_usage_result = await supabase.table("chat_history") \
                    .select("tool_used") \
                    .eq("user_id", current_user["id"]) \
                    .not_.is_("tool_used", "null") \
                    .execute()
                
                tool_usage = {}
                if tool_usage_result and hasattr(tool_usage_result, 'data'):
                    for record in tool_usage_result.data:
                        tool = record.get("tool_used")
                        if tool:
                            tool_usage[tool] = tool_usage.get(tool, 0) + 1
                response["tool_usage"] = tool_usage
                
        except Exception as e:
            logger.error(f"Error getting tool usage stats: {str(e)}")
            # Continue with empty tool usage
        
        try:
            # Get query timeline
            query_timeline_result = await supabase.table("chat_history") \
                .select("created_at, tool_used") \
                .eq("user_id", current_user["id"]) \
                .order("created_at", desc=True) \
                .limit(100) \
                .execute()
                
            if query_timeline_result and hasattr(query_timeline_result, 'data'):
                response["query_timeline"] = query_timeline_result.data
                
        except Exception as e:
            logger.error(f"Error getting query timeline: {str(e)}")
            # Continue with empty query timeline
        
        try:
            # Get popular properties
            popular_properties_result = await supabase.table("property_views") \
                .select("property_id, views_count") \
                .eq("user_id", current_user["id"]) \
                .order("views_count", desc=True) \
                .limit(5) \
                .execute()
                
            if popular_properties_result and hasattr(popular_properties_result, 'data'):
                response["popular_properties"] = popular_properties_result.data
                
        except Exception as e:
            logger.error(f"Error getting popular properties: {str(e)}")
            # Continue with empty popular properties
        
        try:
            # Get economic indicators
            economic_indicators_result = await supabase.table("economic_indicators") \
                .select("*") \
                .limit(5) \
                .execute()
                
            if economic_indicators_result and hasattr(economic_indicators_result, 'data'):
                response["economic_indicators"] = economic_indicators_result.data
                
        except Exception as e:
            logger.error(f"Error getting economic indicators: {str(e)}")
            # Continue with empty economic indicators
        
        logger.info(f"Successfully fetched analytics for user {current_user['id']}")
        return response
        
    except Exception as e:
        logger.error(f"Error in get_analytics: {str(e)}")
        # Return a default response instead of raising an error
        return {
            "tool_usage": {},
            "query_timeline": [],
            "popular_properties": [],
            "economic_indicators": []
        }

# History Endpoints
@router.get("/history")
async def get_chat_history(
    current_user: Dict = Depends(get_current_user),
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    tool: Optional[str] = None
):
    """Get user's chat history with pagination."""
    try:
        print(f"Fetching chat history for user {current_user['id']}")  # Debug log
        offset = (page - 1) * limit
        supabase = get_supabase(auth=False)  # Use admin client for data operations
        
        # Build the base query
        query = supabase.table("chat_history") \
            .select("*", count="exact") \
            .eq("user_id", current_user["id"])
            
        # Add search filter if provided
        if search:
            query = query.or_(f"message.ilike.%{search}%,response.ilike.%{search}%")
            
        # Add tool filter if provided
        if tool and tool != 'all':
            query = query.eq("tool_used", tool)
            
        # Add pagination and ordering
        result = await query \
            .order("created_at", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
            
        total = result.count if hasattr(result, 'count') else 0
        
        return {
            "status": "success",
            "data": result.data if result and hasattr(result, 'data') else [],
            "page": page,
            "limit": limit,
            "total": total
        }
    except Exception as e:
        print(f"Error in get_chat_history: {str(e)}")  # Debug log
        return {
            "status": "success",
            "data": [],
            "page": page,
            "limit": limit,
            "total": 0
        }

# Saved Items Endpoints
@router.post("/save-item")
async def save_item(
    item: SavedItemCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Save a new item to the user's saved items."""
    try:
        supabase = get_supabase(auth=False)
        
        result = await supabase.table("saved_items").insert({
            "user_id": current_user["id"],
            "item_type": item.item_type,
            "title": item.title,
            "content": item.content,
            "tags": item.tags or []
        }).execute()
        
        return {"status": "success", "data": result.data[0] if result.data else None}
    except Exception as e:
        logger.error(f"Error saving item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/saved-items")
async def get_saved_items(
    current_user: Dict = Depends(get_current_user),
    item_type: Optional[str] = None
):
    """Get user's saved items with optional type filter."""
    try:
        print(f"Fetching saved items for user {current_user['id']}")  # Debug log
        supabase = get_supabase(auth=False)  # Use admin client for data operations
        
        query = supabase.table("saved_items") \
            .select("*") \
            .eq("user_id", current_user["id"])
            
        if item_type and item_type != 'all':
            query = query.eq("item_type", item_type)
            
        result = await query.execute()
        
        # Handle empty results gracefully
        if not result or not hasattr(result, 'data'):
            print("No result object returned from Supabase")  # Debug log
            return {"status": "success", "data": []}
            
        if not result.data:
            print(f"No saved items found for user {current_user['id']}")  # Debug log
            return {"status": "success", "data": []}
            
        print(f"Found {len(result.data)} saved items")  # Debug log
        return {"status": "success", "data": result.data}
        
    except Exception as e:
        print(f"Error in get_saved_items: {str(e)}")  # Debug log
        return {"status": "success", "data": []}

@router.delete("/saved-items/{item_id}")
async def delete_saved_item(
    item_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Delete a saved item."""
    try:
        supabase = get_supabase(auth=False)  # Use admin client for data operations
        
        result = await supabase.table("saved_items") \
            .delete() \
            .eq("id", item_id) \
            .eq("user_id", current_user["id"]) \
            .execute()
            
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="Item not found or you don't have permission to delete it"
            )
            
        return {"status": "success", "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Notifications Endpoints
@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    current_user: Dict = Depends(get_current_user),
    unread_only: bool = False
):
    """Get user's notifications."""
    try:
        supabase = get_supabase(auth=False)  # Use admin client for data operations
        
        query = supabase.table("notifications") \
            .select("*") \
            .eq("user_id", current_user["id"])
            
        if unread_only:
            query = query.eq("read", False)
            
        result = await query.order("created_at", desc=True).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notifications/{notification_id}/mark-read")
async def mark_notification_read(
    notification_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Mark a notification as read."""
    try:
        supabase = get_supabase(auth=False)  # Use admin client for data operations
        
        result = await supabase.table("notifications") \
            .update({"read": True}) \
            .eq("id", notification_id) \
            .eq("user_id", current_user["id"]) \
            .execute()
            
        return {"status": "success", "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track-chat")
async def track_chat(
    chat_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Track a chat interaction in the history."""
    try:
        supabase = get_supabase(auth=False)
        
        result = await supabase.table("chat_history").insert({
            "user_id": current_user["id"],
            "message": chat_data["message"],
            "response": chat_data["response"],
            "tool_used": chat_data.get("tool_used"),
            "metadata": chat_data.get("metadata", {})
        }).execute()
        
        return {"status": "success", "data": result.data[0] if result.data else None}
    except Exception as e:
        logger.error(f"Error tracking chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats(current_user: Dict = Depends(get_current_user)):
    """Get user's dashboard statistics."""
    try:
        supabase = get_supabase(auth=False)
        
        # Get saved items count
        saved_items_result = await supabase.table("saved_items") \
            .select("id", count="exact") \
            .eq("user_id", current_user["id"]) \
            .execute()
            
        # Get active chats (chats from last 24 hours)
        active_chats_result = await supabase.table("chat_history") \
            .select("id", count="exact") \
            .eq("user_id", current_user["id"]) \
            .gte("created_at", (datetime.now() - timedelta(days=1)).isoformat()) \
            .execute()
            
        # Get total queries
        total_queries_result = await supabase.table("chat_history") \
            .select("id", count="exact") \
            .eq("user_id", current_user["id"]) \
            .execute()
        
        return {
            "status": "success",
            "data": {
                "saved_items": saved_items_result.count if hasattr(saved_items_result, 'count') else 0,
                "active_chats": active_chats_result.count if hasattr(active_chats_result, 'count') else 0,
                "total_queries": total_queries_result.count if hasattr(total_queries_result, 'count') else 0
            }
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 