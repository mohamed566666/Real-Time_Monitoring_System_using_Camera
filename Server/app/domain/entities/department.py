from pydantic import BaseModel
from typing import Optional


class Department(BaseModel):
    id: Optional[int] = None
    name: str
    manager_id: Optional[int] = None

    class Config:
        from_attributes = True
