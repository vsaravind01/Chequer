from chequer.utils.db_utils import DBSession
from chequer.accounts.models import Account


def get_account_by_id(account_id: int, db=None) -> Account:
    """Get account details by account ID.

    Parameters
    ----------
    - **account_id**: (int) Account ID
    - **db**: (Session) Database session

    Returns
    -------
    - **Account**: Account details
    """
    if db is not None:
        _db = db
    else:
        _db = DBSession().db
    return _db.query(Account).filter(Account.id == account_id).first()


def get_account_by_account_number(account_number: str, db=None) -> Account:
    """Get account details by account number.

    Parameters
    ----------
    - **account_number**: (str) Account number
    - **db**: (Session) Database session

    Returns
    -------
    - **Account**: Account details
    """
    if db is not None:
        _db = db
    else:
        _db = DBSession().db
    return _db.query(Account).filter(Account.account_number == account_number).first()
