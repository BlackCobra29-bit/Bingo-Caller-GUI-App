from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import crud, models, schemas
from ..database import get_db

router = APIRouter()

@router.post("/wallet/", response_model=schemas.Wallet)
def create_wallet(wallet: schemas.WalletCreate, db: Session = Depends(get_db)):
    db_wallet = crud.create_wallet(db=db, wallet=wallet)
    return db_wallet

@router.get("/wallet/{wallet_id}", response_model=schemas.Wallet)
def read_wallet(wallet_id: int, db: Session = Depends(get_db)):
    db_wallet = crud.get_wallet(db=db, wallet_id=wallet_id)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return db_wallet

@router.put("/wallet/{wallet_id}", response_model=schemas.Wallet)
def update_wallet(wallet_id: int, wallet: schemas.WalletUpdate, db: Session = Depends(get_db)):
    db_wallet = crud.update_wallet(db=db, wallet_id=wallet_id, wallet=wallet)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return db_wallet

@router.delete("/wallet/{wallet_id}", response_model=schemas.Wallet)
def delete_wallet(wallet_id: int, db: Session = Depends(get_db)):
    db_wallet = crud.delete_wallet(db=db, wallet_id=wallet_id)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return db_wallet