from pydantic import BaseModel, ConfigDict

class ItemBase(BaseModel):
    title: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    owner_id: int

    model_config:ConfigDict = ConfigDict(from_attributes=True)
