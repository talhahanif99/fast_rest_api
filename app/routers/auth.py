from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.core.security import create_access_token, hash_password, verify_password
from app.dependencies.auth import CurrentUser, DbSession
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserRegister, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a user account with a securely hashed password.",
)
def register_user(payload: UserRegister, db: DbSession) -> User:
    normalized_email = payload.email.lower()
    existing_user = db.scalar(
        select(User).where(func.lower(User.email) == normalized_email)
    )
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        name=payload.name,
        email=normalized_email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from exc

    db.refresh(user)
    return user


async def parse_login_request(request: Request) -> LoginRequest:
    """Accept JSON login payloads and OAuth2 form submissions from Swagger UI."""
    content_type = request.headers.get("content-type", "").lower()

    try:
        if "application/json" in content_type:
            raw_payload: dict[str, Any] = await request.json()
            return LoginRequest.model_validate(raw_payload)

        form = await request.form()
        # OAuth2 password flow sends the email in the conventional "username" field.
        return LoginRequest(
            email=str(form.get("username") or form.get("email") or ""),
            password=str(form.get("password") or ""),
        )
    except (ValidationError, ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Valid email and password are required",
        ) from exc


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive an access token",
    description=(
        "Authenticate with email and password. Accepts JSON requests and the "
        "OAuth2 form format used by Swagger's Authorize button."
    ),
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["email", "password"],
                        "properties": {
                            "email": {
                                "type": "string",
                                "format": "email",
                                "example": "john@example.com",
                            },
                            "password": {
                                "type": "string",
                                "format": "password",
                                "example": "SecurePassword123",
                            },
                        },
                    }
                },
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "required": ["username", "password"],
                        "properties": {
                            "username": {
                                "type": "string",
                                "format": "email",
                                "description": "Registered email address",
                            },
                            "password": {
                                "type": "string",
                                "format": "password",
                            },
                        },
                    }
                },
            },
        }
    },
)
async def login_user(request: Request, db: DbSession) -> TokenResponse:
    payload = await parse_login_request(request)
    normalized_email = payload.email.lower()

    user = db.scalar(select(User).where(func.lower(User.email) == normalized_email))
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Return the profile of the currently authenticated user.",
)
def get_current_user_profile(current_user: CurrentUser) -> User:
    return current_user
