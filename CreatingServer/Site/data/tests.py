import sqlalchemy
from .db_session import SqlAlchemyBase
import sqlalchemy.orm as orm


class Test(SqlAlchemyBase):
    __tablename__ = 'tests'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    questions = sqlalchemy.Column(sqlalchemy.String, index=True)
    answers = sqlalchemy.Column(sqlalchemy.String, index=True)
    max_score = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))

    result = orm.relation("Result", back_populates='test')
    user = orm.relation('User')

