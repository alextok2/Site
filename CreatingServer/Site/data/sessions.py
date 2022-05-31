import sqlalchemy
from .db_session import SqlAlchemyBase
import sqlalchemy.orm as orm


class Session(SqlAlchemyBase):
    __tablename__ = "sessions"

    token = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))

    user = orm.relation('User')



