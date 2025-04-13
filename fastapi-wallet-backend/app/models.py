from sqlalchemy import Column, Float, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Wallet(Base):
    __tablename__ = 'wallets'

    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, default=0.0)
    date_of_stored = Column(DateTime, default=datetime.utcnow)  # Automatically stores the current date
    time = Column(DateTime, default=datetime.utcnow)  # Automatically stores the current time