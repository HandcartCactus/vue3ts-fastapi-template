from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from ..config import SECRET_KEY, ALGORITHM, APP_NAME
from ..db.database import get_db  # Dependency to get database session
from ..db.models.user import User
from fastapi.security import OAuth2PasswordBearer
import pyotp
import base64
import qrcode
from io import BytesIO


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def validate_otp(secret: str, otp: str) -> bool:
    """Validate the OTP against the user's TOTP secret."""
    totp = pyotp.TOTP(secret)
    return totp.verify(otp)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)

# Function to get the current authenticated user
def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db),
    otp: str | None = None  # Optional OTP parameter for 2FA
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and verify JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Retrieve user from database
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    # If 2FA is enabled, check OTP
    if user.totp_secret:
        if otp is None or not validate_otp(user.totp_secret, otp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing 2FA code"
            )

    return user

# Function to get the current authenticated user
def get_current_user_no_otp(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db),
    otp: str | None = None  # Optional OTP parameter for 2FA
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and verify JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Retrieve user from database
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    return user

def generate_totp_secret() -> str:
    return pyotp.random_base32()

def generate_totp_provisioning_uri(username:str, totp_secret:str) -> str:
    totp = pyotp.TOTP(totp_secret)
    return totp.provisioning_uri(name=username, issuer_name=APP_NAME)

def generate_totp_qr_b64(provisioning_uri:str) -> str:
    qr_image = qrcode.make(provisioning_uri)
    buf = BytesIO()
    qr_image.save(buf, format="PNG")
    buf.seek(0)
    
    # Convert image to base64 to include in response
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    return img_str
