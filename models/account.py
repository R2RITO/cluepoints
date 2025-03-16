# Class used to define Accounts
from typing import Optional

from pydantic import BaseModel
from sqlmodel import CheckConstraint, Field, Relationship, SQLModel

from models.user import User


class AccountTypeBase(SQLModel):
    name: str = Field(unique=True)


class AccountType(AccountTypeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    accounts: list["Account"] = Relationship(back_populates="account_type")


class AccountTypeResponse(AccountTypeBase):
    id: int


class AccountBase(SQLModel):
    account_number: str = Field(unique=True)
    balance: float = Field(default=0.0)
    account_type_id: int = Field(default=None, foreign_key="accounttype.id")
    user_id: int = Field(default=None, foreign_key="user.id")


class AccountCreate(AccountBase):
    pass


class AccountResponse(AccountBase):
    id: int
    user: "User"
    account_type: "AccountType"


class AccountTransfer(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float


class Account(AccountBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_type: Optional[AccountType] = Relationship(back_populates="accounts")
    user: Optional["User"] = Relationship(back_populates="accounts")

    __table_args__ = (CheckConstraint("balance >= 0", name="balance_non_negative"),)
