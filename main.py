from contextlib import asynccontextmanager
from typing import Annotated, List
import logging
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Session, SQLModel, select

from database.postgres import engine, get_db
from models.account import (
    Account,
    AccountCreate,
    AccountResponse,
    AccountTransfer,
    AccountType,
    AccountTypeResponse,
)
from models.user import User, UserCreate, UserResponse, UserUpdate
from logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    # Shutdown


app = FastAPI(lifespan=lifespan)


@app.post("/users/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    usr = User.model_validate(user)
    usr.calculate_lat_long()
    db.add(usr)
    db.commit()
    db.refresh(usr)
    return usr


@app.get("/users/", response_model=List[UserResponse])
def list_users(
    db: Annotated[Session, Depends(get_db)],
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    users = db.exec(select(User).offset(offset).limit(limit)).all()
    return users


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, user: UserUpdate, db: Annotated[Session, Depends(get_db)]
):
    db_user = db.get(User, user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data)

    db_user.calculate_lat_long()
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User created: {db_user.id}")
    return db_user


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    db_user = db.get(User, user_id)
    if not db_user:
        logger.error(f"User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


###############


@app.get("/account_types/", response_model=List[AccountTypeResponse])
def get_account_types(db: Annotated[Session, Depends(get_db)]):
    account_types = db.exec(select(AccountType)).all()
    return account_types


@app.post("/accounts/", response_model=AccountResponse, status_code=201)
def create_account(account: AccountCreate, db: Annotated[Session, Depends(get_db)]):
    acc = Account.model_validate(account)
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return acc


@app.get("/accounts/", response_model=List[AccountResponse])
def get_accounts(db: Annotated[Session, Depends(get_db)]):
    accounts = db.exec(select(Account)).all()
    return accounts


@app.post("/accounts/transfer/", response_model=None)
def transfer_funds(
    transfer_data: AccountTransfer, db: Annotated[Session, Depends(get_db)]
):
    """
    Transfers funds between two accounts atomically with database locking.
    """
    if transfer_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    from_account = db.exec(
        select(Account)
        .where(Account.id == transfer_data.from_account_id)
        .with_for_update()
    ).first()
    to_account = db.exec(
        select(Account)
        .where(Account.id == transfer_data.to_account_id)
        .with_for_update()
    ).first()

    if not from_account:
        raise HTTPException(status_code=404, detail="From account not found")
    if not to_account:
        raise HTTPException(status_code=404, detail="To account not found")

    if from_account.balance < transfer_data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    try:
        from_account.balance -= transfer_data.amount
        to_account.balance += transfer_data.amount
        db.add(from_account)
        db.add(to_account)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error making transference between {transfer_data.from_account_id} and {transfer_data.to_account_id}")
        raise HTTPException(status_code=500, detail=f"Transfer failed: {e}") from None

    return {"message": "Transfer successful"}
