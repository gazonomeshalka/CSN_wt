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
    company_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("companies.id"), nullable=True)
    store_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey("stores.id"), nullable=True)
    specialization = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    sender_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey("users.id"), nullable=True)
    receiver_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("users.id"), nullable=True)
