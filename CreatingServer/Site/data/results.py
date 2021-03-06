from email.policy import default
import sqlalchemy
from .db_session import SqlAlchemyBase
import sqlalchemy.orm as orm
import datetime

class Result(SqlAlchemyBase):
    __tablename__ = "results"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    score = sqlalchemy.Column(sqlalchemy.Integer)
    test_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tests.id"))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    date = sqlalchemy.Column(sqlalchemy.DateTime)

    test = orm.relation('Test')
    user = orm.relation('User')



