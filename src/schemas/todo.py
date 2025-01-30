from pydantic import BaseModel


class TodoBase(BaseModel):
    title: str
    owner_id: int


class TodoUpdate(BaseModel):
    title: str
    complete: bool = False


class TodoResponse(TodoBase):
    id: int
    complete: bool = False

    class Config:
        from_attributes = True
