import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Specialization(SqlAlchemyBase):
    __tablename__ = 'specializations'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)