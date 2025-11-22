from __future__ import annotations
import pydantic as _pydantic
import datetime as _datetime
from pydantic import ConfigDict
from typing import Optional

class UserBase(_pydantic.BaseModel):
    name: str
    email: str
    phone: str
    model_config = ConfigDict(from_attributes=True)

class UserRequest(UserBase):
    password: str
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

class UserResponse(UserBase):
    id: int
    created_at: _datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class PostBase(_pydantic.BaseModel):
    title: str
    description: str

class PostRequest(PostBase):
    pass

class PostResponse(_pydantic.BaseModel):
    id: int
    user: Optional['UserResponse'] = None
    title: str
    description: str
    created_at: _datetime.datetime
    
    model_config = ConfigDict(from_attributes=True)

# Update forward references after all classes are defined
UserResponse.model_rebuild()
PostResponse.model_rebuild()