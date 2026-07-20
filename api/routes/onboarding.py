from fastapi import APIRouter, HTTPException, status
from api.routes.onboarding_schemas import UserSignupRequest, UserLoginRequest, PlatformConfigureRequest, TestConnectionRequest
from onboarding.connection_tester import test_platform_connection
from core.database import get_database

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

@router.post("/signup")
async def signup(body: UserSignupRequest):
    try:
        db = get_database()
        # Check if user already exists
        existing = await db.users.find_one({"email": body.email})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email address already exists"
            )

        new_user = {
            "email": body.email,
            "password_hash": f"pbkdf2:{body.password[::-1]}" # Simple reverse mock hash
        }
        await db.users.insert_one(new_user)
        return {"status": "success", "message": "Account created successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process signup: {str(e)}"
        )

@router.post("/login")
async def login(body: UserLoginRequest):
    try:
        db = get_database()
        user = await db.users.find_one({"email": body.email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email or password"
            )
            
        expected_hash = f"pbkdf2:{body.password[::-1]}"
        if user.get("password_hash") != expected_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email or password"
            )

        return {"status": "success", "message": "Login successful"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process login: {str(e)}"
        )

@router.post("/test-connection")
async def test_connection(body: TestConnectionRequest):
    try:
        success = await test_platform_connection(body.platform_name, body.credentials)
        return {"status": "success", "connected": success}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/configure-platform")
async def configure_platform(body: PlatformConfigureRequest):
    # 1. Test the connection first
    try:
        await test_platform_connection(body.platform_name, body.credentials)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connection test failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during connection test: {str(e)}"
        )

    # 2. If successful, persist to MongoDB configuration collection
    try:
        db = get_database()
        await db.configurations.update_one(
            {"platform_name": body.platform_name.lower()},
            {"$set": {
                "credentials": body.credentials,
                "connected": True
            }},
            upsert=True
        )
        return {"status": "success", "message": f"{body.platform_name} configured and saved successfully in MongoDB"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist platform configuration: {str(e)}"
        )
