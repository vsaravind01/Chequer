from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Float
from datetime import datetime

from chequer.database import Base
from chequer.accounts.models import Account


class ChequeClearedRecord(Base):
    __tablename__ = "cheque_cleared_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payer_id = Column(Integer, ForeignKey(Account.id), nullable=False)
    image_uri = Column(String, nullable=False)
    ocr_uri = Column(String, nullable=False)
    to_account_number = Column(String, nullable=False)
    payee_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    ifs_code = Column(String, nullable=False)
    cheque_date = Column(DateTime(timezone=True), nullable=False)
    cheque_number = Column(String, nullable=False)
    status = Column(String, nullable=False)
    signature_similarity = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)


class ChequerTextractQueue(Base):
    __tablename__ = "chequer_textract_queue"

    id = Column(Integer, primary_key=True, autoincrement=True)
    image_uri = Column(String, nullable=False)
    to_account_number = Column(String, nullable=False)
    status = Column(String, nullable=False)
    response = Column(String, default="")
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
