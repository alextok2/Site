import sqlalchemy
from .db_session import SqlAlchemyBase
import sqlalchemy.orm as orm


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    fio = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    login = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True, index=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)


