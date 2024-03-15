from fastapi.routing import APIRouter
from fastapi import Depends, status, HTTPException, Security
from chequer.auth.dependencies import get_current_user, is_user_authenticated
from chequer.utils.db_utils import get_db
from chequer.ocr_engine.models import ChequerTextractQueue, ChequeClearedRecord

router = APIRouter(
    prefix="/ocr-engine", tags=["ocr-engine"], dependencies=[Security(is_user_authenticated)]
)


@router.get("/queue", status_code=status.HTTP_200_OK)
async def get_queue(db=Depends(get_db)):
    """
    Get the Textract queue.

    Parameters
    ----------
    - **db**: (Session) Database session

    Returns
    -------
    - **List[ChequerTextractQueue]**: List of Textract queue items
    """
    return db.query(ChequerTextractQueue).all()


@router.get("/cleared", status_code=status.HTTP_200_OK)
async def get_cleared(db=Depends(get_db)):
    """
    Get the cleared cheques.

    Parameters
    ----------
    - **db**: (Session) Database session

    Returns
    -------
    - **List[ChequeClearedRecord]**: List of cleared cheques
    """
    return db.query(ChequeClearedRecord).all()
