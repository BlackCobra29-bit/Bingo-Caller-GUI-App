from sqlalchemy.orm import Session
from . import models, schemas

def create_wallet(db: Session, wallet: schemas.WalletCreate):
    db_wallet = models.Wallet(**wallet.dict())
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet

def get_wallet(db: Session, wallet_id: int):
    return db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()

def get_wallets(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Wallet).offset(skip).limit(limit).all()

def update_wallet(db: Session, wallet_id: int, wallet: schemas.WalletUpdate):
    db_wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if db_wallet:
        for key, value in wallet.dict(exclude_unset=True).items():
            setattr(db_wallet, key, value)
        db.commit()
        db.refresh(db_wallet)
    return db_wallet

def delete_wallet(db: Session, wallet_id: int):
    db_wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if db_wallet:
        db.delete(db_wallet)
        db.commit()
    return db_wallet