import datetime
from pydantic import BaseModel
from typing import Optional, List



class UserShow(BaseModel):
    name: str
    rfid_uid: str
    mobile_number: int


class User(BaseModel):
    id: int
    name: str
    rfid_uid: str
    mobile_number: int

class AccessGive(BaseModel):
    rfid_uid: str

class Access_log(BaseModel):
    id: int
    user_id: str
    is_active: bool
    logging_time: datetime.datetime

    class Config:
        from_attributes = True



