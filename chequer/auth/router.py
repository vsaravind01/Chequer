# Standard Imports
import os
from datetime import datetime, timedelta

# Third Party Imports
import bcrypt
import jwt
from dotenv import load_dotenv

# Fastapi imports
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# Ayush-Connect imports
from chequer.auth.dependencies import get_current_user, get_db
from chequer.auth.models import User
from chequer.auth.schemas import UserCreate, UserLogin, UserResponse, UserUpdate

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

router = APIRouter(prefix="/auth", tags=["auth"])

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_jwt_token(data: dict, expires_delta: timedelta = timedelta(hours=3)):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/signup")
async def signup(user: UserCreate, db=Depends(get_db)) -> JSONResponse:
    """
    Create a new user in the database.

    Parameters
    ----------
    - **user**: (UserCreate) User creation details
                    - **username**: Username of the user
                    - **name**: Name of the user
                    - **email**: Email of the user
                    - **password**: Password of the user
                    - **user_type**: Type of user (ADMIN, PROFESSIONAL, CONSUMER)
    **db**: (Session) Database session

    Returns
    -------
    - **JSONResponse**: JSON response with the status of user creation

    Raises
    ------
    - **HTTPException**
                    - **500** - If user creation fails
    """
    try:
        hashed_password = password_context.hash(user.password)
        db_user = User(
            username=user.username,
            name=user.name,
            email=user.email,
            password=hashed_password,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed insering into db. Error:{e}")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_jwt_token(
        {"username": db_user.username}, expires_delta=access_token_expires
    )

    response = JSONResponse(
        status_code=201,
        content={
            "message": f"User - '{db_user.username}' created successfully.",
            "access_token": access_token,
            "token_type": "bearer",
        },
    )

    response.set_cookie("access_token", access_token, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return response


@router.post("/login")
async def login(user_login: UserLogin, db=Depends(get_db)) -> JSONResponse:
    """
    Log in a user by verifying their credentials and providing an access token.

    Parameters
    ----------
    - **user_login**: (UserLogin) User login details
                    - **username**: Username of the user
                    - **password**: Password of the user
    **db**: (Session) Database session

    Returns
    -------
    - **JSONResponse**: JSON response with the status of user login and an access token

    Raises
    ------
    - **HTTPException**
                    - **401 Unauthorized** - If the provided username or password is incorrect
    """
    username = user_login.username
    password = user_login.password

    user = db.query(User).filter(User.username == username).first()

    if user is None or not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_jwt_token({"username": user.username}, expires_delta=access_token_expires)

    response = JSONResponse(
        status_code=201,
        content={
            "message": f"User - '{user.username}' logged in successfully.",
            "access_token": access_token,
            "token_type": "bearer",
        },
    )

    response.set_cookie("access_token", access_token, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return response


@router.post("/logout")
async def logout(user: UserResponse = Depends(get_current_user)):
    """
    Log out a user by clearing the access token cookie.

    Parameters
    ----------
    - **user**: (UserResponse) User information obtained from the access token, obtained through `get_current_user`.

    Returns
    -------
    - **JSONResponse**: JSON response with the status of user logout

    Raises
    ------
    - **HTTPException**
                    - **401 Unauthorized** - If no access token is found (user is not logged in)
    """

    if user:
        response = JSONResponse(content={"message": "Logged out successfully"})
        response.delete_cookie("access_token")
        return response

    raise HTTPException(status_code=401, detail="No access token found. You are not logged in.")


@router.get("/{username}", response_model=UserResponse)
async def get_user(username: str, db=Depends(get_db)):
    """
    Retrieve user information by user ID.

    Parameters
    ----------
    - **username**: (int) The username of the user to retrieve.
    **db**: (Session) Database session

    Returns
    -------
    - **UserResponse**: User information in a JSON-serializable format

    Raises
    ------
    - **HTTPException**
                    - **404** - If the user with the specified ID is not found
                    - **500** - If there is an error while fetching user information
    """
    try:
        db_user = db.query(User).filter(User.username == username).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch user from db.")
    return UserResponse.from_orm(db_user)


@router.put("/{username}")
async def update_user(username: str, user: UserUpdate, db=Depends(get_db)) -> JSONResponse:
    """
    Update user information by user ID.

    Parameters
    ----------
    - **user_id**: (int) The ID of the user to update.
    - **user**: (UserUpdate) User update details
    **db**: (Session) Database session

    Returns
    -------
    - **JSONResponse**: JSON response with the status of user update

    Raises
    ------
    - **HTTPException**
                    - **404** - If the user with the specified ID is not found
                    - **500** - If there is an error while updating user information
    """
    try:
        db_user = db.query(User).filter(User.username == username).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        for key, value in user.dict().items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update user details.")
    return JSONResponse(
        status_code=201,
        content={"message": f"User - '{db_user.username}' updated successfully."},
    )


@router.delete("/{username}")
async def delete_user(username: str, db=Depends(get_db)) -> JSONResponse:
    """
    Delete a user by user ID.

    Parameters
    ----------
    - **user_id**: (int) The ID of the user to delete.
    **db**: (Session) Database session

    Returns
    -------
    - **JSONResponse**: JSON response with the status of user deletion

    Raises
    ------
    - **HTTPException**
                    - **404** - If the user with the specified ID is not found
                    - **500** - If there is an error while deleting user information
    """
    try:
        db_user = db.query(User).filter(User.username == username).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(db_user)
        db.commit()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to delete user details.")
    return JSONResponse(
        status_code=201,
        content={"message": f"User - '{db_user.username}' deleted successfully."},
    )
