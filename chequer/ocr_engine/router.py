from fastapi.routing import APIRouter
from fastapi import Depends, status, Security, UploadFile
from chequer.auth.dependencies import get_current_user, is_user_authenticated
from chequer.utils.db_utils import get_db
from chequer.utils.s3_utils.s3_store import ChequerStore, StoreTypes
from chequer.accounts.services import get_account_by_id, get_account_by_account_number
from chequer.ocr_engine.models import ChequerTextractQueue, ChequeClearedRecord
from chequer.ocr_engine.v1.analyse import TextractEngine, SignatureSimilarityEngine
from uuid import uuid4
from PIL import Image
import json

router = APIRouter(
    prefix="/ocr-engine", tags=["ocr-engine"], dependencies=[Security(is_user_authenticated)]
)

SSE = SignatureSimilarityEngine()


@router.post("/clear_cheque", status_code=status.HTTP_200_OK)
async def extract_data(image: UploadFile, to_account_number: str, db=Depends(get_db)):
    """
    Extract data from the cheque image.

    Parameters
    ----------
    - **image**: (UploadFile) Cheque image
    - **to_account_number**: (str) Account number
    - **db**: (Session) Database session

    Returns
    -------
    - **ChequerTextractQueue**: Textract queue item
    """
    textract_engine = TextractEngine()
    ocr_store = ChequerStore(StoreTypes.OCR)
    cheque_store = ChequerStore(StoreTypes.CHEQUES)
    sign_store = ChequerStore(StoreTypes.SIGNATURES)

    assert image.content_type is not None
    image_type = image.content_type.split("/")[1]

    image_uri = cheque_store.upload_file(
        image.file,
        f"{uuid4()}.{image_type}",
    )

    document = textract_engine.analyze_document(image_uri)
    from_account_number = textract_engine.get_account_number(document)
    cheque_record = ChequeClearedRecord(
        image_uri=image_uri,
        to_account_number=to_account_number,
        response=json.dumps(document.response),
    )

    if from_account_number is None:
        setattr(cheque_record, "status", "FROM_ACCOUNT_NOT_FOUND")
    else:
        from_account = get_account_by_account_number(from_account_number, db)
        if from_account is None:
            setattr(cheque_record, "status", "FROM_ACCOUNT_NOT_FOUND")
        else:
            setattr(cheque_record, "payer_id", from_account.id)

    to_account = get_account_by_account_number(to_account_number, db)
    if to_account is None:
        setattr(cheque_record, "status", "TO_ACCOUNT_NOT_FOUND")
    if to_account.name is not textract_engine.get_payee_name(document):
        setattr(cheque_record, "status", "PAYEE_NAME_MISMATCH")

    payee_name = textract_engine.get_payee_name(document)
    amount = textract_engine.get_amount(document)
    date = textract_engine.get_date(document)
    bank_name = textract_engine.get_bank_name(document)
    ifs_code = textract_engine.get_ifs_code(document)
    cheque_number = textract_engine.get_cheque_number(document)

    setattr(cheque_record, "payee_name", payee_name)
    setattr(cheque_record, "amount", amount)
    setattr(cheque_record, "cheque_date", date)
    setattr(cheque_record, "bank_name", bank_name)
    setattr(cheque_record, "ifs_code", ifs_code)
    setattr(cheque_record, "cheque_number", cheque_number)
    setattr(cheque_record, "status", "CLEARED")

    ocr_dict = {
        "Queries": [{"Query": q.alias, "Answer": q.result} for q in document.queries],
        "Signature": document.signatures[0]._raw_object,
    }

    ocr_uri = ocr_store.upload_file(json.dumps(ocr_dict), f"{cheque_record.id}.json")
    setattr(cheque_record, "ocr_uri", ocr_uri)

    original_signature_image = sign_store.get_file_from_uri(from_account.signature_url.value)
    original_signature_image = Image.open(original_signature_image)
    cheque_image = Image.open(image.file)
    cheque_image_sign = SSE.crop_image(
        cheque_image, ocr_dict["Signature"]["Geometry"]["BoundingBox"]
    )

    similarity = SSE.check_signature_similarity(original_signature_image, cheque_image_sign)

    setattr(cheque_record, "signature_similarity", similarity)

    db.add(cheque_record)
    db.commit()
    db.refresh(cheque_record)
    return cheque_record


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
