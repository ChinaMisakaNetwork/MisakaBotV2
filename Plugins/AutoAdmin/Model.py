from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer
from Database import engine

base = declarative_base()


class Blacklist(base):
    __tablename__ = 'Admin_Blacklist'
    id = Column(BigInteger, primary_key=True)

    def __init__(self, id):
        self.id = id

class AdminUser(base):
    __tablename__ = 'Admin_AdminUser'
    id = Column(BigInteger, primary_key=True)
    tier = Column(Integer)

    def __init__(self, id, tier=1):
        self.id = id
        self.tier = tier

base.metadata.create_all(bind=engine)