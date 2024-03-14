from pydantic import BaseModel, EmailStr
from datetime import datetime


class AccountCreate(BaseModel):
    account_number: str
    branch_name: str
    name: str
    email: EmailStr
    phone: str
    signature_url: str
    balance: int


class AccountUpdate(BaseModel):
    branch_name: str
    name: str
    email: EmailStr
    phone: str
    signature_url: str


class AccountUpdateBalance(BaseModel):
    balance: float


class AccountUpdateEmail(BaseModel):
    email: EmailStr


class AccountUpdateName(BaseModel):
    name: str
    signature_url: str


class AccountUpdatePhone(BaseModel):
    phone: str


class AccountResponse(BaseModel):
    id: int
    uploader_id: int
    account_number: str
    branch_name: str
    name: str
    email: EmailStr
    phone: str
    signature_url: str
    balance: float
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, account):
        return cls(
            id=account.id,
            uploader_id=account.uploader_id,
            account_number=account.account_number,
            branch_name=account.branch_name,
            name=account.name,
            email=account.email,
            phone=account.phone,
            signature_url=account.signature_url,
            balance=account.balance,
            created_at=account.created_at,
            updated_at=account.updated_at,
        )
