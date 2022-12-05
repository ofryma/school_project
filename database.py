from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String , DateTime , JSON , ForeignKey , Float

from datetime import datetime

engine = create_engine("sqlite:///memory.db" , echo=True)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class Batch(Base):
    __tablename__ = "batches"

    id = Column(String, primary_key=True)
    batch_number = Column(Integer , nullable = False)
    prod_date = Column(DateTime , nullable=True)
    BL_TiCl4_sol = Column(Integer)
    BL_c_TiO2 = Column(Integer)
    ETL_mTiO2 = Column(Integer)
    HTL_Spiro = Column(Integer)
    HTL_CUSCN = Column(Integer)
    Electrode_Au = Column(Integer)
    Electrode_C  = Column(Integer)
    Encap_in_GB = Column(Integer)
    UV_glue = Column(Integer)
    Boom_epoxy = Column(Integer)

class FileLog(Base):
    __tablename__ = "file_logs"

    id = Column(String , primary_key=True)
    path = Column(String , nullable=False)
    update_time = Column(DateTime)

class CellData(Base):
    __tablename__ = "celldata"

    id = Column(Integer, primary_key=True)
    src_filename = Column(String)
    batch_number = Column(Integer)
    test_date = Column(DateTime , default=datetime.now())
    cell_number = Column(Integer , nullable = True)
    Voc = Column(Float , nullable=True)
    FF = Column(Float , nullable=True)
    Eff = Column(Float , nullable=True)
    cellarea = Column(Float , nullable=True)


Base.metadata.create_all(engine)