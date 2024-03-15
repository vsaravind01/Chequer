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


class DBSession:
    def __init__(self):
        self.db = SessionLocal()

    def add(self, item):
        self.db.add(item)

    def add_commit(self, item):
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

    def update_commit(self, item):
        item_class = item.__class__
        _item = self.db.query(item_class).filter(item_class.id == item.id).first()
        if _item is None:
            raise Exception(f"{item_class.__name__} not found")
        for key, value in item.dict().items():
            setattr(_item, key, value)
        self.db.commit()
        self.db.refresh(_item)

    def commit(self):
        self.db.commit()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
