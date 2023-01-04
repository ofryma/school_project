import os
from database import *
import pandas as pd
import numpy as np
import matplotlib
from typing import List , Any
from fastapi import FastAPI , Query , Form
from fastapi import File, UploadFile
from fastapi.responses import FileResponse , HTMLResponse
import uvicorn
from pydantic import BaseModel

from analyze import *
from crud import *


app = FastAPI(
    title= "School Project"
    )


@app.post("/datafile/upload-data/{batch_number}" , tags=["Data files"])
async def create_file(
    batch_number : int,
    file_type : str = Query(datafiles_types[0] , enum = datafiles_types),
    encapsulation_material : str = Query(encapsulation_types[0] , enum = encapsulation_types),
    encapsulation_status : str = Query("before" , enum = ["before" , "after"]),
    file: UploadFile = File(...),
    cellarea : float = 0.09,
    extra_notes : str = "",
    
    ):

    
    filename = file.filename
    data = file.file.read().decode("utf-8")

    res = []

    if file_type == "all":
        all_file_data = read_from_all_file(data)
        data_keys = list(all_file_data.keys())

        

        for i in range(len(all_file_data[data_keys[0]])):
            cur_cell_data = {}
            cur_cell_data["src_filename"] = all_file_data["filename"][i]
            cur_cell_data["Jsc"] = all_file_data["Jsc"][i]
            cur_cell_data["Voc"] = all_file_data["Uoc"][i]
            cur_cell_data["FF"] = all_file_data["FF"][i]
            cur_cell_data["Eff"] = all_file_data["Eff"][i]
            cur_cell_data["cellarea"] = all_file_data["cellarea"][i]
            
            cur_cell_data["batch_number"] = batch_number
            cur_cell_data["encapsulation_status"] = encapsulation_status
            cur_cell_data["encapsulation_material"] = encapsulation_material
            cur_cell_data["extra_notes"] = extra_notes

            res.append(cur_cell_data)
            update_cell_IV_measurement(cur_cell_data)

    elif file_type == "IV mesure":
        data = get_IV_from_content(data=data)
        data = analyze_IV(I=data["I"] ,  V=data["V"] , cellarea=cellarea)

        data["src_filename"] = filename
        data["batch_number"] = batch_number
        data["encapsulation_status"] = encapsulation_status
        data["encapsulation_material"] = encapsulation_material
        data["extra_notes"] = extra_notes

        res.append(data)
        update_cell_IV_measurement(data)


    return res

@app.post("/update-batch/config/{batch_number}" , tags=["Batch"])
async def update_batch_configurations(
    batch_number : int,
    encapsulation_material : str = Query(encapsulation_types[0] , enum = encapsulation_types),
    update_times : bool = False,
    production_time : datetime = datetime.now(),
    encapsulation_time : datetime = datetime.now(),
    encapsulation_in_GB : bool = False,
    encapsulation_stored_location : str = "",
    extra_notes : str = "",
    applied_presure : bool = False,

):
    

    data = {}
    data["batch_number"] = batch_number
    data["encapsulation_material"] = encapsulation_material
    data["update_times"] = update_times
    data["encapsulation_time"] = encapsulation_time
    data["production_time"] = production_time
    data["encapsulation_in_GB"] = encapsulation_in_GB
    data["encapsulation_stored_location"] = encapsulation_stored_location
    data["extra_notes"] = extra_notes
    data["applied_presure"] = applied_presure
    
    update_batch_params(data)

    return data

@app.get("/celldata/get-all" , tags=["Cell data"])
async def get_all_cells(
):
    
    return get_all_cell_data()

@app.get("/" , tags=["stats"])
def display_dashboard(

):
    
    data = get_all_cell_data()
    
    batch_numbers_list , pixel_for_batch = get_pixels_is_batch(data)

    content_replace = {
        "encapsulation_types_list" : str([""] + encapsulation_types + [""]),
        "encapsulation_types_yield_data" : str([0] + [30 ,80] + [0]),
        "batch_list" : str(batch_numbers_list),
        "num_of_pixels_in_batch" : str(pixel_for_batch),
        # "celldata_table" : dict_to_html_table(data),
    }


    with open("static/index.html" , 'r') as f:    
        html_content = f.read()
        for key in content_replace.keys():
            html_content = html_content.replace(
                key , content_replace[key]
            )

    return HTMLResponse(content=html_content, status_code=200)


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)