import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String , DateTime , JSON , ForeignKey , Boolean , Float
from pydantic import BaseModel

from datetime import datetime
from typing import List


db_url = "sqlite:///memory.db"

engine = create_engine(db_url , connect_args={"check_same_thread": False}) # , echo=True

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

    # layers description 
    procedure = Column(String , nullable = True)
    
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


    # Encapsulation data
    encap_prod_date = Column(DateTime , nullable=True)
    encap_in_GB = Column(Integer , nullable=True)
    encap_stored_location = Column(String)
    encap_material = Column(String)
    applied_presure = Column(Integer , nullable = True)
    process_time_interval = Column(DateTime , nullable = True)
    extra_notes = Column(String , nullable = True)


class Procedure(Base):

    __tablename__ = "procedures"

    id = Column(Integer , primary_key=True )
    name = Column(String(20) , nullable = False)


    device_transperacy = Column(Integer , nullable=True)
    number_of_layers = Column(Integer , nullable=True)
    Substrate_material = Column(String , nullable=True)

    # Layer 1
    l1_function = Column(String , nullable=True)
    l1_material = Column(String , nullable=True)
    l1_fabrication_method = Column(String , nullable=True)
    l1_thickness = Column(Float , nullable=True)
    

    # Layer 2
    l2_function = Column(String , nullable=True)
    l2_material = Column(String , nullable=True)
    l2_fabrication_method = Column(String , nullable=True)
    l2_thickness = Column(Float , nullable=True)
    

    # Layer 3
    l3_function = Column(String , nullable = True)
    l3_material = Column(String , nullable=True)
    l3_fabrication_method = Column(String)
    l3_thickness = Column(Float , nullable=True)
    

    # Layer 4
    l4_function = Column(String , nullable=True)
    l4_material = Column(String , nullable=True)
    l4_fabrication_method = Column(String , nullable=True)
    l4_thickness = Column(Float , nullable=True)
    
    l4_ratio = Column(String , nullable=True)
    Processing_solvent = Column(String , nullable=True)
    Additive_1 = Column(String , nullable=True)
    Additive_1_concentration  = Column(Float , nullable=True)
    Additive_2   = Column(String , nullable=True)
    Additive_2_concentration = Column(Float , nullable=True)
    Active_layer_treatment_from_processing =  Column(String , nullable=True)
    # Time since solution was prepared
    # Solution concentration
    # Solution temperature
    # Relative humidity during processing
    # "When was thermal annealing done 
    # (pre-deposition, post-deposition, post-sealing, none)"
    # Annealing temperature
    # Annealing time
    # Solvent vapor annealing
    # Solvent used
    # Solvent annealing time
    # Antisolvent treatment (yes/no)
    # Antisolvent (if used)
    # Treatment Time (if used)
    # Removal of Antisolvent (if used)

    # Layer 5
    l5_function = Column(String , nullable=True)
    l5_material = Column(String , nullable=True)
    l5_fabrication_method = Column(String , nullable=True)
    l5_thickness = Column(Float , nullable=True)
    
    # Processing solvent
    # Additive 1
    # Additive 1 concentration
    # Additive 2
    # Additive 2 concentration
    # Additive 3
    # Additive 3 concentration
    # Time since solution was prepared
    # Solution concentration
    # Solution temperature
    # "When was thermal annealing done 
    # (pre-deposition, post-deposition, post-sealing, none)"
    # Annealing temperature
    # Annealing time
    # Antisolvent treatment (yes/no)


    # Layer 6
    l6_function = Column(String , nullable=True)
    l6_material = Column(String , nullable=True)
    l6_fabrication_method = Column(String , nullable=True)
    l6_thickness = Column(Float , nullable=True)
    
    # Growth rate 1
    # Growth rate 2
    # Base pressure
    # Substrate temperature
    # Co-deposition (yes/no)
    # Ratio (if co-deposited)
    # Annealing temperature (if used)
    # Annealing solvent (if used)  
    # Annealing time (if used)

    extra_description = Column(String)




# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)