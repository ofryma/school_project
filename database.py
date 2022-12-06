import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String , DateTime , JSON , ForeignKey , Boolean , Float
from pydantic import BaseModel

from datetime import datetime
from typing import List


db_url = "sqlite:///memory.db"

engine = create_engine(db_url , echo=True)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

###############
# TABLES      #
###############

class Batch(Base):
    __tablename__ = "batches"

    batch_number = Column(Integer , primary_key=True)
    prod_date = Column(DateTime , nullable=True , default=datetime.now())
    BL_TiCl4_sol = Column(Integer  , nullable=True)
    BL_c_TiO2 = Column(Integer , nullable=True)
    ETL_mTiO2 = Column(Integer , nullable=True)
    HTL_Spiro = Column(Integer , nullable=True)
    HTL_CUSCN = Column(Integer , nullable=True)
    Electrode_Au = Column(Integer , nullable=True)
    Electrode_C  = Column(Integer , nullable=True)
    Encap_in_GB = Column(Integer , nullable=True)
    UV_glue = Column(Integer , nullable=True)
    Boom_epoxy = Column(Integer , nullable=True)
    applied_presure = Column(Integer , nullable = True)
    extra_notes = Column(String , nullable = True)


class FileLog(Base):
    __tablename__ = "file_logs"

    id = Column(String , primary_key=True)
    path = Column(String , nullable=False)
    
class CellData(Base):
    __tablename__ = "celldata"

    id = Column(Integer, primary_key=True)
    src_filename = Column(String)   
    batch_number = Column(Integer , ForeignKey("batches.batch_number"))
    prod_date = Column(DateTime , default=datetime.now())
    before_encap = Column(Boolean , default=True)
    Jsc = Column(Float , nullable = True)
    Uoc = Column(Float , nullable = True)
    FF = Column(Float , nullable = True)
    Eff = Column(Float , nullable = True)
    cellarea = Column(Float , nullable = True)
    extra_notes = Column(String , nullable = True)

###############
# BASE MODELS #
###############

class DataFileCreate(BaseModel):
    filename : List[str]
    Uoc : List[float]
    Jsc : List[float]
    FF : List[float]
    Eff : List[float] 
    cellarea : List[float]

class BatchCreate(BaseModel):
    batch_number : int
    prod_date : datetime
    BL_TiCl4_sol : int
    BL_c_TiO2 : int
    ETL_mTiO2 : int
    HTL_Spiro : int
    HTL_CUSCN : int
    Electrode_Au : int
    Electrode_C  : int
    Encap_in_GB : int
    UV_glue : int
    Boom_epoxy : int
    applied_presure : int
    extra_notes : str


    def create(self):

        obj = session.query(Batch).filter(Batch.batch_number == self.batch_number).first()
        if obj == None:

            session.add(Batch(
                batch_number = self.batch_number,
                prod_date  = self.prod_date,
                BL_TiCl4_sol = self.BL_TiCl4_sol,
                BL_c_TiO2  = self.BL_c_TiO2,
                ETL_mTiO2 = self.ETL_mTiO2,
                HTL_Spiro = self.HTL_Spiro,
                HTL_CUSCN = self.HTL_CUSCN,
                Electrode_Au = self.Electrode_Au,
                Electrode_C  = self.Electrode_C,
                Encap_in_GB = self.Encap_in_GB,
                UV_glue = self.UV_glue,
                Boom_epoxy = self.Boom_epoxy,
                applied_presure = self.applied_presure,
                extra_notes = self.extra_notes,
                
            ))
            return session.commit()
        else:
            return {"Error" : "This batch is already exists"}

    def update(self , obj):
        
        obj.prod_date  = self.prod_date
        obj.BL_TiCl4_sol = self.BL_TiCl4_sol
        obj.BL_c_TiO2  = self.BL_c_TiO2
        obj.ETL_mTiO2 = self.ETL_mTiO2
        obj.HTL_Spiro = self.HTL_Spiro
        obj.HTL_CUSCN = self.HTL_CUSCN
        obj.Electrode_Au = self.Electrode_Au
        obj.Electrode_C  = self.Electrode_C
        obj.Encap_in_GB = self.Encap_in_GB
        obj.UV_glue = self.UV_glue
        obj.Boom_epoxy = self.Boom_epoxy
        obj.applied_presure = self.applied_presure
        obj.extra_notes = self.extra_notes

        return obj



class CellDataCreate(BaseModel):
    src_filename: str
    batch_number: int
    Uoc : float
    FF : float
    Eff : float
    Jsc: float

    def create(self):
        session.add(CellData(
            src_filename = self.src_filename,
            batch_number = self.batch_number,
            Uoc = self.Uoc,
            FF = self.FF,
            Eff = self.Eff,
            Jsc = self.Jsc,
        ))
        session.commit()

class BatchResponse(BaseModel):

    def recive(self , id):
        return session.query(Batch).get(id)


Base.metadata.create_all(engine)