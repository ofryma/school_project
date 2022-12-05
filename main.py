import os
from database import *
import pandas as pd
import numpy as np
import matplotlib
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI

app = FastAPI()


def read_our_csv(csv_url : str) -> any:
    
    with open(csv_url , "r") as datafile:
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
    return {"message": "Hello World"}


@app.get("/table/")
async def get_example_csv():
    datafile_url = os.getcwd() + "/all.txt"
    return read_our_csv(datafile_url)


def insert_data_to_db(csv_path: str , batch_number : int):
    data = read_our_csv(csv_path)
    cell_data_list = []

    for i in range(len(data[list(data.keys())[0]])):
        cell_data_list.append(CellData(
            src_filename = data["filename"][i],
            batch_number = batch_number,
            Voc = data["Uoc,mV"][i],
            FF = data["FF,%"][i],
            Eff = data["Eff,%"][i],
            cellarea = data["cellarea"][i]
        ))
    session.add_all(cell_data_list)

    session.commit()


insert_data_to_db("./all.txt" , 4)





