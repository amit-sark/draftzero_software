# schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    mobile: str


class feedbackCreate(BaseModel):
    name: str
    timestamp: datetime
    email: EmailStr
    feedback: str



class updateCheck(BaseModel):
    version: float
    executable_link: str


class UserResponse(BaseModel):
    sl: int
    username: str
    email: str
    mobile: str
    free_trial_active: bool
    free_trial_start: datetime
    free_trial_end: datetime

    class Config:
        from_attributes = True  

class ActivationKey(BaseModel):

    uuid: str