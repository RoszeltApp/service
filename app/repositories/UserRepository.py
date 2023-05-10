from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.Models.models import User
from app.repositories.BaseRepository import BaseRepository


class UserRepository(BaseRepository):

    def add_user(self, new_user: User):
        self.db.add(new_user)
        self.db.commit()
        pass

    def suppliers_list(self):
        # query = self.db.query(User.id, User.name).where(User.role_code == 1).all()
        query = self.db.execute(select(User.id, User.name).where(User.role_code == 1)).all()

        return [
            {
                'id': supplier.id,
                'name': supplier.name
            } for supplier in query
        ]

    def personal_account(self, id: int):
        query = self.db.query(User).options(joinedload(User.role)).where(User.id == id).first()
        return query

    def check_user(self, name: str):
        exist = self.db.execute(select(User.id, User.name).where(User.name == name)).first()
        return exist

    def update_token(self, user_id: int, new_token: str):
        query = self.db.query(User).where(User.id == user_id).first()
        query.refresh_token = new_token
        self.db.merge(query)
        self.db.commit()
