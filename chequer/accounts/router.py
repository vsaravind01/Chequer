from fastapi import APIRouter, Depends, File, HTTPException, Security, UploadFile, status, Body

from chequer.accounts.models import Account
from chequer.accounts.schemas import AccountCreate, AccountResponse, AccountUpdate
from chequer.auth.dependencies import get_current_user, is_user_authenticated
from chequer.auth.models import User
from chequer.utils.db_utils import get_db
from chequer.utils.s3_utils.s3_store import ChequerStore, StoreTypes

router = APIRouter(
    prefix="/accounts", tags=["accounts"], dependencies=[Security(is_user_authenticated)]
)


@router.post("/create")
async def create_account(
    account: AccountCreate = Depends(),
    image_file: UploadFile = File(...),
    db=Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AccountResponse:
    """
    Create a new account in the database.

    Parameters
    ----------
    - **account**: (AccountCreate) Account creation details
                - **uploader_id**: ID of the user who created the account
                - **account_number**: Account number
                - **ifs_code**: IFS or IRFC code
                - **name**: Name of the account holder
                - **email**: Email of the account holder
                - **phone**: Phone number of the account holder
                - **signature_image**: Signature image of the account holder
    - **db**: (Session) Database session

    Returns
    -------
    - **AccountResponse**: Account creation details
    """
    store = ChequerStore(StoreTypes.SIGNATURES)
    image = await image_file.read()

    uri = store.upload_file(image, f"{account.account_number}.png")

    new_account = Account(
        uploader_id=current_user.id,
        account_number=account.account_number,
        ifs_code=account.ifs_code,
        name=account.name,
        email=account.email,
        phone=account.phone,
        balance=account.balance,
        signature_url=uri,
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


@router.get("/get/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int, db=Depends(get_db)) -> AccountResponse:
    """
    Get account details by account ID.

    Parameters
    ----------
    - **account_id**: (int) Account ID
    - **db**: (Session) Database session

    Returns
    -------
    - **AccountResponse**: Account details
    """
    account = db.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return account


@router.put("/update/{account_id}")
async def update_account(
    account_id: int, account: AccountUpdate, db=Depends(get_db)
) -> AccountResponse:
    """
    Update account details by account ID.

    Parameters
    ----------
    - **account_id**: (int) Account ID
    - **account**: (AccountUpdate) Account update details
    - **db**: (Session) Database session

    Returns
    -------
    - **AccountResponse**: Account details
    """
    db_account = db.query(Account).filter(Account.id == account_id).first()
    if db_account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    for key, value in account.model_dump().items():
        setattr(db_account, key, value)
    db.commit()
    db.refresh(db_account)
    return db_account


@router.delete("/delete/{account_id}")
async def delete_account(account_id: int, db=Depends(get_db)) -> dict:
    """
    Delete account by account ID.

    Parameters
    ----------
    - **account_id**: (int) Account ID
    - **db**: (Session) Database session

    Returns
    -------
    - **dict**: JSON response with the status of account deletion
    """
    db_account = db.query(Account).filter(Account.id == account_id).first()
    if db_account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    db.delete(db_account)
    db.commit()
    return {"status": "Account deleted"}


@router.post("/transfer")
async def transfer_amount(
    from_account_id: int, to_account_id: int, amount: float, db=Depends(get_db)
) -> dict:
    """
    Transfer amount from one account to another.

    Parameters
    ----------
    - **from_account_id**: (int) Account ID from which the amount will be transferred
    - **to_account_id**: (int) Account ID to which the amount will be transferred
    - **amount**: (float) Amount to be transferred
    - **db**: (Session) Database session

    Returns
    -------
    - **dict**: JSON response with the status of the transfer
    """
    from_account = db.query(Account).filter(Account.id == from_account_id).first()
    to_account = db.query(Account).filter(Account.id == to_account_id).first()
    if from_account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Account not found {from_account_id}"
        )
    if to_account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Account not found {to_account_id}"
        )
    if from_account.balance < amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
    from_account.balance -= amount
    to_account.balance += amount
    db.commit()
    return {
        "status": "Amount transferred successfully",
        "new_balance": {
            from_account.account_number: from_account.balance,
            to_account.account_number: to_account.balance,
        },
    }
