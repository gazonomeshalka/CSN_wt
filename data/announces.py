import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Announce(SqlAlchemyBase):
    __tablename__ = 'announces'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    importance = sqlalchemy.Column(sqlalchemy.Integer)
    picture_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    company_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("companies.id"), nullable=True)
    store_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey("stores.id"), nullable=True)
    specialization_id = sqlalchemy.Column(sqlalchemy.Integer,
                                          sqlalchemy.ForeignKey("specializations.id"), nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"), nullable=True)
