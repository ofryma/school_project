from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String , DateTime , JSON , ForeignKey

from datetime import datetime

engine = create_engine("sqlite:///memory.db" , echo=True)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# class Batch(Base):
#     __tablename__ = "baches"

class CellData(Base):
    __tablename__ = "celldata"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    basename = Column(String)
    root = Column(String)
    extension = Column(String)
    creation_time = Column(DateTime)
    original_location = Column(String)
    last_transaction = Column(DateTime , default=datetime.now())
    file_metadata = Column(JSON)
    

    def __repr__(self):
        return "<File(name='%s', creation date='%s')>" % (
            self.basename,
            self.creation_time,
        )

Base.metadata.create_all(engine)