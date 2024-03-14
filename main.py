from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text

from chequer.auth.router import router as auth_router
from chequer.accounts.router import router as accounts_router
from chequer.utils.db_utils import get_db
from chequer.database import sync_engine, Base

Base.metadata.create_all(bind=sync_engine)

app = FastAPI()

app.include_router(auth_router)
app.include_router(accounts_router)


@app.get("/")
async def root():
    """
    Root endpoint

    Returns
    -------
    - **JSONResponse**: JSON response with message and version
    """
    return {"message": "Chequer API", "version": "0.1.0"}


@app.get("/healthcheck", status_code=status.HTTP_200_OK)
async def perform_healthcheck(db=Depends(get_db)):
    """
    Healthcheck endpoint

    Parameters
    ----------
    - **db**: (Session) Database session

    Returns
    -------
    - **JSONResponse**: JSON response with status of the database connection
    """
    result = db.execute(text("SELECT 1"))
    one = result.one()
    if not one[0] == 1:
        db_status = False
    else:
        db_status = True

    _status = {}
    if not db_status:
        raise HTTPException(status_code=404, detail="db conn not available")
    elif db_status:
        _status["operations"] = "ok"
    return _status
