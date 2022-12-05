import os
from database import *
import pandas as pd
import numpy as np
import matplotlib
from typing import List , Any
from fastapi import FastAPI

app = FastAPI()


app = FastAPI()

datafile_url = os.getcwd() + "/all.txt"

def read_our_csv(csv_url : str) -> any:
    
    with open(datafile_url , "r") as datafile:
        txt = datafile.read()
        txt_lines = txt.split("\n")

        # first line is the headers:
        txt_lines.pop(0)
        data_dict = {
            "filename" : [] ,
            "Uoc,mV" : [],
            "Jsc,mA/cm2" : [] ,
            "FF,%" : [] ,
            "Eff,%" : [] ,
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
            data_dict["Uoc,mV"].append(line_list[1])
            data_dict["Jsc,mA/cm2"].append(line_list[2])
            data_dict["FF,%"].append(line_list[3])
            data_dict["Eff,%"].append(line_list[4])
            data_dict["cellarea"].append(line_list[5])
        
        df = pd.DataFrame().from_dict(data_dict)
        return df

@app.get("/")
async def root():
    return {"message": "API is up and running"}


@app.post("/batch/new")
async def create_new_batch(
    data : BatchCreate
):
    return data.create()

@app.get("/batch/{id}")
async def read_item(id: int):
    
    return BatchResponse().recive(id)

@app.post("/datafile/upload/{batch_number}")
async def upload_dataframe(
    data: DataFileCreate,
    batch_number : int
):

    for i in range(len(data.filename)):
        session.add(CellData(
            src_filename = data.filename[i] ,
            batch_number = batch_number,
            Uoc = data.Uoc[i],
            FF = data.FF[i],
            Eff = data.Eff[i],
            Jsc = data.Jsc[i],
            cellarea = data.cellarea[i]
        ))
        session.commit()
    



    return "Hello"


@app.post("/celldata")
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

    






