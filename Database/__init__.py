from nonebot import get_driver
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

connectStr = get_driver().config.db_connect_str
engine = create_engine(connectStr)
dbSession = sessionmaker(bind=engine, check_same_thread=False)