from sqlalchemy.orm import Session
from .models.user import User
from .models.item import Item
from .schemas.auth import UserCreate
from .schemas.item import ItemCreate
from passlib.hash import bcrypt
from ..core.security import hash_password

def get_user(db: Session, username: str):
    if not isinstance(username, str):
        raise ValueError('Username must be a string')
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    """Create a new user, hashing the password."""
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, username: str):
    user = get_user(db,username)
    if user is None:
        return False
    db.delete(user)
    db.commit()
    return True


def create_item(db: Session, item: ItemCreate, user_id: int):
    db_item = Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)