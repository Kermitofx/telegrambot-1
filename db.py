from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine,Column, Integer, String
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
class SearchData(Base):
    __tablename__ = 'search_data'
    id = Column(Integer, primary_key=True)
    song_short=Column(String)
    song_link=Column(String)
engine=create_engine("postgres://bniufsqeyqiebh:be2d82048281446cad3890a5e5b02f6920be7e718f0a130b083bae68e9eab694@ec2-174-129-33-107.compute-1.amazonaws.com:5432/d17fc4io4po963")

def loadSession():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
