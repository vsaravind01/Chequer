from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float

from chequer.auth.models import User
from chequer.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uploader_id = Column(Integer, ForeignKey(User.id), nullable=False)
    account_number = Column(String, nullable=False, unique=True)
    ifs_code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=False, unique=True)
    balance = Column(Float, nullable=False)
    signature_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
