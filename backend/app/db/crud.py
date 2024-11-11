from sqlalchemy.orm import Session
from .models.user import User
from .models.item import Item
from .schemas.auth import UserCreate
from .schemas.item import ItemCreate
from passlib.hash import bcrypt
from ..core.security import hash_password

class ExistingObjectError(Exception):
    """
    Exception raised when an object with the same ID already exists in the database.
    """
    pass

class NonexistentObjectError(Exception):
    """
    Exception raised when an object with a given ID does not exist in the database.
    """
    pass 

def get_user(db: Session, username: str):
    if not isinstance(username, str):
        raise ValueError('Username must be a string')
    
    return db.query(User).filter(User.username == username).first()


def change_password(db: Session, username: str, new_password: str) -> None:
    if not isinstance(username, str):
        raise ValueError('Username must be a string')
    
    if not isinstance(new_password, str):
        raise ValueError('Password must be a string')
    
    hashed_password = hash_password(new_password)

    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise NonexistentObjectError('User does not exist in the database.')
    
    user.hashed_password = hashed_password
    db.commit()
    db.refresh(user)
    return user

def create_user(db: Session, user: UserCreate):
    """Create a new user, hashing the password."""
    if get_user(db, user.username):
        raise ExistingObjectError('User already exists in the database.')
    
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

def delete_user2(db: Session, username: str):
    user = get_user(db,username)
    if user is None:
        raise NonexistentObjectError('User does not exist in the database.')
    db.delete(user)
    db.commit()

def create_item(db: Session, item: ItemCreate, user_id: int):
    db_item = Item(**item.model_dump(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)