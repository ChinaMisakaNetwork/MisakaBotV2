from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer
from Database import engine

base = declarative_base()


class Blacklist(base):
    __tablename__ = 'Admin_Blacklist'
    id = Column(BigInteger, primary_key=True)

class AdminUser(base):
    __tablename__ = 'Admin_AdminUser'
    id = Column(BigInteger, primary_key=True)
    tier = Column(Integer)

base.metadata.create_all(bind=engine)