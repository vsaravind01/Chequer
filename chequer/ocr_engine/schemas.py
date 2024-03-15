from pydantic import BaseModel


class ChequeRecordResponse(BaseModel):
    id: int
    payer_id: int
    image_uri: str
    to_account_number: str
    payee_name: str
    amount: float
    ifs_code: str
    cheque_date: str
    cheque_number: str
    status: str
    signature_similarity: float

    created_at: str
    updated_at: str

    @classmethod
    def from_orm(cls, cheque_record):
        return cls(
            id=cheque_record.id,
            payer_id=cheque_record.payer_id,
            image_uri=cheque_record.image_uri,
            to_account_number=cheque_record.to_account_number,
            payee_name=cheque_record.payee_name,
            amount=cheque_record.amount,
            ifs_code=cheque_record.ifs_code,
            cheque_date=cheque_record.cheque_date,
            cheque_number=cheque_record.cheque_number,
            status=cheque_record.status,
            signature_similarity=cheque_record.signature_similarity,
            created_at=cheque_record.created_at,
            updated_at=cheque_record.updated_at,
        )
