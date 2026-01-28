from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

session_manager = None

def set_session_manager(manager):
    global session_manager
    session_manager = manager

class LoginRequest(BaseModel):
    email: str
    password: str
    account_id: str = "default"

class AuthResponse(BaseModel):
    success: bool
    message: str
    account_id: str = None

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login to Facebook"""
    try:
        await session_manager.start(request.account_id)
        await session_manager.login(request.email, request.password, request.account_id)
        return AuthResponse(
            success=True,
            message="Login successful",
            account_id=request.account_id
        )
    except Exception as e:
        return AuthResponse(
            success=False,
            message=str(e)
        )

@router.post("/logout", response_model=AuthResponse)
async def logout(account_id: str = "default"):
    """Logout from Facebook"""
    try:
        await session_manager.stop(account_id)
        return AuthResponse(
            success=True,
            message="Logout successful",
            account_id=account_id
        )
    except Exception as e:
        return AuthResponse(
            success=False,
            message=str(e)
        )

@router.get("/status", response_model=AuthResponse)
async def status(account_id: str = "default"):
    """Check login status"""
    try:
        is_logged_in = await session_manager.is_logged_in(account_id)
        return AuthResponse(
            success=is_logged_in,
            message="Logged in" if is_logged_in else "Not logged in",
            account_id=account_id
        )
    except Exception as e:
        return AuthResponse(
            success=False,
            message=str(e)
        )
