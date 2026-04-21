from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_active_user, get_user_roles, get_user_permissions
from app.models import User
from app.schemas import LoginRequest, Token, UserResponse, MyPermissionsResponse
from app.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


def authenticate_user(email: str, password: str, db: Session) -> User:
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    return user


@router.post("/login", response_model=Token)
def login_json(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(data.email, data.password, db)
    access_token = create_access_token(subject=str(user.id))

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/login-form", response_model=Token)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # В Swagger поле username используется как email
    user = authenticate_user(form_data.username, form_data.password, db)
    access_token = create_access_token(subject=str(user.id))

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/my-permissions", response_model=MyPermissionsResponse)
def get_my_permissions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    direct_roles = get_user_roles(current_user.id, db)
    role_names = [role.name for role in direct_roles]

    permissions = sorted(list(get_user_permissions(current_user, db)))

    return MyPermissionsResponse(
        user_id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        is_super_admin=current_user.is_super_admin,
        roles=role_names,
        permissions=permissions,
    )