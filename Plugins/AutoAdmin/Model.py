from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer
from Database import engine

base = declarative_base()


class Blacklist(base):
    __tablename__ = 'Admin_Blacklist'
    id = Column(Integer, primary_key=True)

base.metadata.create_all(bind=engine)