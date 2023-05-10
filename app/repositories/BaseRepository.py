from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.database import get_db_connection


class BaseRepository:
    db: Session

    def __init__(self, db: Session = Depends(get_db_connection)):
        self.db = db
