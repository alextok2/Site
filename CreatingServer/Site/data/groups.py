import sqlalchemy
from .db_session import SqlAlchemyBase
import sqlalchemy.orm as orm


class Group(SqlAlchemyBase):
    __tablename__ = "groups"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))

    user = orm.relation('User')



