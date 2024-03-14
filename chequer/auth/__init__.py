from chequer.database import SessionLocal


def get_db():
    """
    Get database session

    Returns
    -------
    - **Session**: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
