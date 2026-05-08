from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.firebase import verify_firebase_token
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenVerifyRequest(BaseModel):
    token: str


class UserResponse(BaseModel):
    user_id: str
    email: str
    display_name: str | None
    avatar_url: str | None

    model_config = {"from_attributes": True}


@router.post("/verify", response_model=UserResponse)
async def verify_token(body: TokenVerifyRequest, db: AsyncSession = Depends(get_db)):
    claims = verify_firebase_token(body.token)
    firebase_uid = claims["uid"]
    email = claims.get("email", "")
    display_name = claims.get("name")
    avatar_url = claims.get("picture")

    result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            firebase_uid=firebase_uid,
            email=email,
            display_name=display_name,
            avatar_url=avatar_url,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        user.email = email
        if display_name:
            user.display_name = display_name
        if avatar_url:
            user.avatar_url = avatar_url
        await db.commit()
        await db.refresh(user)

    return UserResponse(
        user_id=str(user.id),
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    result = await db.execute(select(User).where(User.firebase_uid == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserResponse(
        user_id=str(user.id),
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
    )
