import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Store(SqlAlchemyBase):
    __tablename__ = 'stores'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    boss_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String)
    company_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("companies.id"))
