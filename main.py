import os
from database import *
import pandas as pd
import numpy as np
import matplotlib
from typing import List , Any
from fastapi import FastAPI
from fastapi import File, UploadFile

app = FastAPI()



def read_from_txt(txt : str) -> any:
    
    txt_lines = txt.split("\n")

    # first line is the headers:
    txt_lines.pop(0)
    data_dict = {
        "filename" : [] ,
        "Uoc" : [],
        "Jsc" : [] ,
        "FF" : [] ,
        "Eff" : [] ,
        "cellarea" : []
    }

    for line in txt_lines:
        line_list = line.split(" ")
        if len(line_list) < 6:
            continue
        
        i=0
        while i < len(line_list):
            if line_list[i] == "":
                line_list.pop(i)
            else:
                i += 1


        data_dict["filename"].append(line_list[0])
        data_dict["Uoc"].append(line_list[1])
        data_dict["Jsc"].append(line_list[2])
        data_dict["FF"].append(line_list[3])
        data_dict["Eff"].append(line_list[4])
        data_dict["cellarea"].append(line_list[5])
    
    return data_dict
def read_our_csv(csv_url : str) -> any:
    
    with open(csv_url , "r") as datafile:
        txt = datafile.read()
    
    txt_lines = txt.split("\n")

    # first line is the headers:
    txt_lines.pop(0)
    data_dict = {
        "filename" : [] ,
        "Uoc" : [],
        "Jsc" : [] ,
        "FF" : [] ,
        "Eff" : [] ,
        "cellarea" : []
    }

    for line in txt_lines:
        line_list = line.split(" ")
        if len(line_list) < 6:
            continue
        
        i=0
        while i < len(line_list):
            if line_list[i] == "":
                line_list.pop(i)
            else:
                i += 1


        data_dict["filename"].append(line_list[0])
        data_dict["Uoc"].append(line_list[1])
        data_dict["Jsc"].append(line_list[2])
        data_dict["FF"].append(line_list[3])
        data_dict["Eff"].append(line_list[4])
        data_dict["cellarea"].append(line_list[5])
    
    return data_dict
def insert_data(data: dict , batch_number : int):
    
    for i in range(len(data["filename"])):
        session.add(CellData(
            src_filename = data["filename"][i] ,
            batch_number = batch_number,
            Uoc = data["Uoc"][i],
            FF = data["FF"][i],
            Eff = data["Eff"][i],
            Jsc = data["Jsc"][i],
            cellarea = data["cellarea"][i]
        ))
        session.commit()


##############
# BATCH      #
##############


@app.get("/batch/{id}" , tags=["Batch"])
async def read_item(id: int):
    
    return BatchResponse().recive(id)

@app.post("/batch/new" , tags=["Batch"])
async def create_new_batch(
    data : BatchCreate
):
    data.create()
    return {"Success" : f"New batch created" , "batch_data" : data}

@app.put("/batch/update/{batch_number}" , tags=["Batch"])
def update_object(batch_number: int, obj_data: BatchCreate):
    obj = session.query(Batch).filter(Batch.batch_number == batch_number).first()
    if obj is None:
        return {"Error" : "Could not find this batch number in the database"}
    else:
        obj = obj_data.update(obj)
        session.commit()
        return {"Success" : f"Batch number {batch_number} was updated"}

@app.delete("/batch/{batch_number}" , tags=["Batch"])
def delete_record(batch_number: int):
    

    session.query(CellData).filter(CellData.batch_number == batch_number).delete()
    session.query(Batch).filter(Batch.batch_number == batch_number).delete()
    session.commit()
    
    return {"message": "Record deleted successfully"}

    


##############
# DATAFILES  #
##############


@app.post("/datafile/upload-txt/{batch_number}" , tags=["Data files"])
async def create_file(
    batch_number : int,
    file: bytes = File(),
    ):
    data = read_from_txt(file.decode("utf-8"))
    if session.query(Batch).get(batch_number) == None:
        session.add(Batch(
            batch_number = batch_number
        ))
    insert_data(data , batch_number)

    return data


# @app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile):
#     # this route will be able to later upload the file to S3
#     return {"filename": file.filename}


# @app.post("/datafile/upload/{csv_url}/{batch_number}")
# async def upload_read_from_csv(
#     csv_url: str,
#     batch_number: int
# ):
#     data = read_our_csv(csv_url)
#     insert_data(data , batch_number)

# @app.post("/datafile/upload/{batch_number}")
# async def upload_dataframe(
#     data: DataFileCreate,
#     batch_number : int
# ):

#     insert_data(data)

#     return "Hello"



##############
# CELLDATA   #
##############

@app.get("/celldata" , tags=["Cell Data"])
async def get_all_cells():
    
    return session.query(CellData).all()

@app.post("/celldata" , tags=["Cell Data"])
async def create_list_of_cell_data(
    data: List[CellDataCreate]
):
    for cell in data:
        if BatchResponse().recive(cell.batch_number) == None:
            session.add(Batch(
                batch_number = cell.batch_number
            ))
            session.commit()
            

        cell.create()






@app.get("/" , tags=["Tests"])
async def root():
    return {"message": "API is up and running"}




