import sqlalchemy
from .db_session import SqlAlchemyBase
import sqlalchemy.orm as orm


class Test(SqlAlchemyBase):
    __tablename__ = 'tests'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    questions = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    answers = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)

    result = orm.relation("Result", back_populates='test')

