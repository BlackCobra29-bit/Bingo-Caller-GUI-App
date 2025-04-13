from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WalletCreate(BaseModel):
    balance: float

class WalletUpdate(BaseModel):
    balance: Optional[float] = None
    date_of_stored: Optional[datetime] = None
    time: Optional[datetime] = None

class Wallet(BaseModel):
    id: int
    balance: float
    date_of_stored: datetime
    time: datetime

    class Config:
        orm_mode = True