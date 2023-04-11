import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    SNO = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    specialization = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    key_pass = sqlalchemy.Column(sqlalchemy.BINARY)
    store_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("stores.id"), nullable=True)
    company_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("companies.id"), nullable=True)
