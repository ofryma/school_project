import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String , DateTime , JSON , ForeignKey , Boolean , Float
from pydantic import BaseModel

from datetime import datetime
from typing import List



drive_path = "C:\\Users\Asus\Google Drive\Projects\school_project"

if not os.path.exists(drive_path):
    drive_path = ""

db_url = f"sqlite:///{os.path.join(drive_path , 'memory.db')}"
engine = create_engine(db_url , connect_args={"check_same_thread": False}) # , echo=True

print(db_url)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

###############
# TABLES      #
###############

class CellData(Base):
    __tablename__ = "celldata"

    id = Column( Integer , primary_key=True , autoincrement=True )
    src_filename = Column(String)   
    batch_number = Column(Integer)
    prod_date = Column(DateTime , default=datetime.now())
    
    # check criteria
    bias = Column(String , nullable = True)
    light = Column(String , nullable = True)

    # mesured before encapsulation
    Pmax_before = Column(Float , nullable = True)
    Vmp_before = Column(Float , nullable = True)
    Imp_before = Column(Float , nullable = True)
    Jsc_before = Column(Float , nullable = True)
    Uoc_before = Column(Float , nullable = True)
    FF_before = Column(Float , nullable = True)
    Eff_before = Column(Float , nullable = True)

    # mesured after encapsulation
    Pmax_after = Column(Float , nullable = True)
    Vmp_after = Column(Float , nullable = True)
    Imp_after = Column(Float , nullable = True)
    Jsc_after = Column(Float , nullable = True)
    Uoc_after = Column(Float , nullable = True)
    FF_after = Column(Float , nullable = True)
    Eff_after = Column(Float , nullable = True)
    
    device_area = Column(Float , nullable = True)

    # Fabrication data
    fabrication_procedure_number = Column(Integer , ForeignKey("fabrication_procedures.id"))

    # Encapsulation data
    encap_procedure_number = Column(Integer , ForeignKey("encapsulation_procedures.id"))
    encap_material = Column(String)
    encap_prod_date = Column(DateTime , nullable=True)
    extra_notes = Column(String , nullable = True)

    pass_cell = Column(Boolean , nullable = True)
    yeild_cell = Column(Boolean , nullable = True)

class FabricationProcedure(Base):

    __tablename__ = "fabrication_procedures"

    id = Column(Integer , primary_key=True )
    name = Column(String(20) , nullable = False)
    description = Column(String)

class EncapsulationProcedure(Base):
    
    __tablename__ = "encapsulation_procedures"

    id = Column(Integer , primary_key=True )
    name = Column(String(20) , nullable = True)
    pressure = Column(Float , nullable = True)
    kapton_in_gb = Column(Boolean)
    encapsulation_in_gb = Column(Boolean)
    encapsulation_material = Column(String)


# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)