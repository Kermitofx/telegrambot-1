from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine,Column, Integer, String
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
class SearchData(Base):
    __tablename__ = 'search_data'
    id = Column(Integer, primary_key=True)
    song_short=Column(String)
    song_link=Column(String)
engine=create_engine("DATABASE_URL")

def loadSession():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session