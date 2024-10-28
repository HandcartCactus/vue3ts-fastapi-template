from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...db import crud
from ...db.schemas.item import ItemCreate, ItemResponse
from ...core.security import get_current_user
from ...db.database import get_db
from ...db.models import Item, User

from typing import List

router = APIRouter()

@router.get("/", response_model=List[ItemResponse])
async def create_item(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    all_items = db.query(Item).filter(Item.owner_id == current_user.id).all()
    return [ItemResponse(**item.__dict__) for item in all_items]

@router.post("/", response_model=ItemResponse)
async def create_item(item: ItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.create_item(db, item, user_id=current_user.id)

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": "You have access to this protected route", "username": current_user.username}