import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    SNO = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    specialization = sqlalchemy.Column(sqlalchemy.Integer,
                                       index=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    company_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("companies.id"), index=True)
    company = orm.relationship('Company')
    store_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey("stores.id"), index=True)
    store = orm.relationship('Store')
