from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine,Column, Integer, String
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
class SearchData(Base):
    __tablename__ = 'search_data'
    id = Column(Integer, primary_key=True)
    song_short=Column(String)
    song_link=Column(String)
engine=create_engine("postgres://mzkgcqwmoaywpx:9e89df52e90c30a6674e5c53edfcbf313a8b4cc95e5f8f0f07a829d780ba080d@ec2-54-235-67-106.compute-1.amazonaws.com:5432/dfk12mf6e1p2g7")

def loadSession():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session