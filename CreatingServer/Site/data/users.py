import sqlalchemy
from .db_session import SqlAlchemyBase
import sqlalchemy.orm as orm


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True)
    fio = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    login = sqlalchemy.Column(
        sqlalchemy.String, nullable=True, unique=True, index=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    role = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    group_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("groups.id"))

    # group = orm.relation("Group")
    group = orm.relation("Group", back_populates='user')
