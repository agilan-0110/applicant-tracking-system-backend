from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from app.auth.token import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse,UserLogin
from app.auth.hashing import hash_password,verify_password

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    summary="Register a new user",
    description="Creates a recruiter or candidate account."
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    hashed = hash_password(user.password)

    existing_user = db.query(User).filter(
    User.email == user.email
).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
    )
    db_user = User(
        name=user.name,
        email=user.email,
        password_hashed=hashed,
        role=user.role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post(
    "/login",
    summary="User Login",
    description="Authenticates a user and returns a JWT access token."
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(form_data.password, db_user.password_hashed):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        {
            "user_id": db_user.id,
            "email": db_user.email,
            "role": db_user.role,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }