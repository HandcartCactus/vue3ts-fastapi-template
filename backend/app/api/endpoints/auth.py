from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from ...db import crud
from ...db.models import User
from ...db.schemas.auth import UserCreate, Token, TokenWith2FA, UserPwChange
from ...core.security import (
    create_access_token, get_current_user_no_otp, 
    get_current_user, validate_otp, generate_totp_provisioning_uri, 
    generate_totp_qr_b64, generate_totp_secret
)
from ...db.database import get_db
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user in the system with the provided user details.

    Args:
        user (UserCreate): An object containing the username and password for the new user.
        db (Session, optional): The SQLAlchemy database session. Defaults to using dependency injection.

    Raises:
        HTTPException: If the username is already taken, a 409 Conflict response is returned.

    Returns:
        dict: A dictionary with the access token and token type for the newly registered user.
    """

    if crud.get_user(db, user.username) is not None:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail="User already exists")
    db_user = crud.create_user(db, user)
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=TokenWith2FA)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates a user and provides an access token. The function first verifies the user's credentials and then checks if two-factor authentication is enabled for the user.

    Args:
        form_data (OAuth2PasswordRequestForm): An object containing the form fields for OAuth2 authentication. This typically includes the username and password.
        db (Session, optional): The SQLAlchemy database session. Defaults to using dependency injection.

    Raises:
        HTTPException: If the user authentication fails due to incorrect username or password, a 401 Unauthorized response is returned.

    Returns:
        dict: Returns a dictionary containing the access token, token type, and a boolean indicating if the user requires 2FA.
              If 2FA is required, an empty token is returned with `requires_2fa` set to True.
              If 2FA is not required, a valid token is returned with `requires_2fa` set to False.
    """
    print('form data',form_data)
    # Authenticate the user
    user = crud.get_user(db, form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if 2FA is enabled
    if user.totp_secret:
        # If 2FA is enabled, return response indicating 2FA is required
        return {"access_token": "", "token_type": "", "requires_2fa": True}

    # If 2FA is not enabled, issue an access token
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "requires_2fa": False}

@router.post("/verify-2fa", response_model=Token)
def verify_2fa(username: str, otp: str, db: Session = Depends(get_db)):

    user = crud.get_user(db, username)
    if not user or not user.totp_secret:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="2FA not enabled for user")

    # Validate OTP
    if not validate_otp(user.totp_secret, otp):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid 2FA code")

    # Issue access token upon successful 2FA verification
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/enable-2fa")
def enable_2fa(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_no_otp)):
    user = crud.get_user(db, current_user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Generate TOTP secret if not already set
    if not user.totp_secret:
        user.totp_secret = generate_totp_secret()
        db.commit()

    # Create provisioning URI and generate QR code
    provisioning_uri = generate_totp_provisioning_uri(username=user.username, totp_secret=user.totp_secret)
    img_str = generate_totp_qr_b64(provisioning_uri)
    
    return JSONResponse(content={"provisioning_uri": provisioning_uri, "qr_code_base64": img_str})

@router.post("/disable-2fa")
def disable_2fa(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = crud.get_user(db, current_user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.totp_secret:
        user.totp_secret = None
        db.commit()

@router.post("/change-password", response_model=Token)
def change_password(password_change_form:UserPwChange, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = crud.get_user(db, current_user.username)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check old password
    if not crud.verify_password(password_change_form.old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    crud.change_password(db=db, username=current_user.username, new_password=password_change_form.new_password)

    # Generate new JWT token
    access_token = create_access_token(data={"sub": current_user.username})
    
    # TODO: revoke old refresh token
    
    return {"access_token": access_token, "token_type": "bearer"}
    

