import os

import jwt
from fastapi import Cookie, Depends, status
from fastapi.exceptions import HTTPException
from jwt.exceptions import DecodeError, ExpiredSignatureError
from typing import Optional

from chequer.auth.models import User
from chequer.utils.db_utils import get_db

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]


def get_current_user(access_token: str = Cookie(None), db=Depends(get_db)) -> Optional[User]:
    """Get the current user from the access token.

    Parameters
    ----------
    - **access_token**: (str) Access token
    - **db**: (Session) Database session

    Returns
    -------
    - **User**: User details
    """
    if access_token is None:
        return None
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def is_user_authenticated(current_user: User = Depends(get_current_user)) -> bool:
    """Check if the user is authenticated.

    Parameters
    ----------
    - **current_user**: (User) Current user

    Returns
    -------
    - **bool**: True if the user is authenticated, False otherwise
    """
    return current_user is not None
