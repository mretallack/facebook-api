from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter()

GRAPH_API_BASE = "https://graph.facebook.com/v18.0"

@router.get("/me")
async def get_user_profile(access_token: str):
    """Get current user's profile"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GRAPH_API_BASE}/me",
            params={"access_token": access_token, "fields": "id,name,email"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

@router.get("/me/feed")
async def get_user_feed(access_token: str, limit: int = 25):
    """Get current user's feed"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GRAPH_API_BASE}/me/feed",
            params={"access_token": access_token, "limit": limit}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
