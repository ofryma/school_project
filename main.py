import os
from database import *
import pandas as pd
from typing import List , Any
from fastapi import FastAPI , Query , Form
from fastapi import File, UploadFile
from fastapi.responses import FileResponse , HTMLResponse
from pydantic import BaseModel
from math import pow
from typing import List

from analyze import *
from crud import *

app = FastAPI(
    title= "School Project"
    )


def find_value(index : str , tag_len: int , data : str , close_tag : str = "$"):

    i = index + tag_len
    value = ""
    while not data[i] == close_tag:
        value += data[i]
        i+=1
        if i >= len(data):
            break

    return value

def kappa(ref_dens : float , defu : float , cp : float):
    return ref_dens * defu * cp

def kappa_calc(data):

    data_dict = {
        'REF_DENSITY' : None,
        'SAMPLE_NAME' : None,
        'Shot_number' : [],
        'Temperature_lfa' : [],
        'Diffusivity' : [],
        'Std_dev' : [],
        'Cp_calc' : [],
        'Kappa' : []
    }
    
    try:
        data_dict["REF_DENSITY"] = float(find_value(data.index("#Ref_density /(g/cm^3),")  , len("#Ref_density /(g/cm^3),"), data , close_tag = "\\"))
        data_dict["SAMPLE_NAME"] = find_value(data.index("#Sample,")  , len("#Sample,"), data , close_tag = "\\")
        data = find_value(data.index("#Cp-calc./(J/g/K)\\r\\n") , len("#Cp-calc./(J/g/K)\\r\\n") , data)
    except:
        pass
    
    for row in data.split("\\r\\n"):
        
        try:
            row = row.split(",")
            data_dict["Shot_number"].append(row[0])
            data_dict["Temperature_lfa"].append(float(row[1]) + 273.0)    
            data_dict["Diffusivity"].append(float(row[2]))    
            data_dict["Std_dev"].append(float(row[3]))    
            data_dict["Cp_calc"].append(float(row[4])) 
            data_dict["Kappa"].append(kappa(
                ref_dens = data_dict["REF_DENSITY"],
                defu = float(row[2]),
                cp = float(row[4])
            )) 
        except:
            pass
    
    return data_dict


@app.get("/download-data" , tags=["Data files"])
async def download_file():
    cell_data_file_path = "cell-data.csv"
    df = pd.DataFrame(get_all_cell_data())
    df.to_csv(cell_data_file_path , index=False)

    
    return FileResponse(cell_data_file_path , media_type='application/octet-stream',filename=cell_data_file_path)
    
@app.post("/itamar/raw-data-file")
async def zt_file_analyzer(
    lfa_file: UploadFile = File(...),
    lsr_file: UploadFile = File(...),
):

    data_dict = kappa_calc(str(lfa_file.file.read()))


    with open(lsr_file.filename, "wb") as binary_file:
    
        # Write bytes to file
        binary_file.write(lsr_file.file._file.read())
    
    df = pd.read_excel(lsr_file.filename)

    data_dict["Temperature_lsr"] = [val + 273.0 for val in df["Temperature(°C)"]]
    data_dict["Seebeck_cof"] = [val for val in df["Seebeck coefficient(µV/K)"]]
    data_dict["Resistivity"] = [val * 10**5 for val in df["Resistivity(??m)"]]
    


    kappa_func = scipy.interpolate.PchipInterpolator(data_dict["Temperature_lfa"], data_dict["Kappa"] , extrapolate=True)
    
    data_dict["ZT"] = []
    data_dict["Power_Factor"] = []
    data_dict["Kappa_Interp"] = []
    for s , t , r in zip(data_dict["Seebeck_cof"] , data_dict["Temperature_lsr"] , data_dict["Resistivity"]):
        data_dict["Kappa_Interp"].append(kappa_func.__call__(t))
        data_dict["ZT"].append(((s**2)*t)/(kappa_func.__call__(t)*r*pow(10,7)))
        data_dict["Power_Factor"].append(pow(s , 2) / (r*pow(10,7)))

    del data_dict["REF_DENSITY"]
    del data_dict["SAMPLE_NAME"]


    max_len = 0
    for key in data_dict.keys():
        try:
            if len(data_dict[key]) > max_len:
                max_len = len(data_dict[key])
        except:
            pass



    for key in data_dict.keys():
        for i in range(max_len):
            try:
               if data_dict[key][i] == None:
                pass
            except:
                data_dict[key].append("")
    
    if os.path.exists(lfa_file.filename):
        os.remove(lfa_file.filename)
    if os.path.exists(lsr_file.filename):
        os.remove(lsr_file.filename)

    df = pd.DataFrame.from_dict(data_dict)
    df.to_csv("data.csv")

    return FileResponse("data.csv" , media_type='application/octet-stream',filename=lfa_file.filename)

@app.post("/upload-folder" , tags=["Data files"])
async def upload_batch_folder(file: UploadFile = File(...),):
    
    res = {"Result": "OK", "filenames": file.filename}
    if file.filename.lower().endswith("png") or file.filename.lower().endswith("jpg") or file.filename.lower().endswith("jpg"):
        # update image info
        file_info = file.filename.split("/")
        batch_name = file_info[0]
        batch_number = int(batch_name.split("_")[1])
        encapsulation_status = file_info[1]
        filename = file_info[-1]
        update_cell_image_path(batch_number , filename.split(".")[0] , file.filename)

    if not file.filename.endswith("txt"):
        return res
    if "table" in file.filename or "results" in file.filename:
        return res
    if "all" in file.filename:
        return res
    
    file_info = file.filename.split("/")
    batch_name = file_info[0]
    batch_number = int(batch_name.split("_")[1])
    encapsulation_status = file_info[1]
    filename = file_info[-1]

    if not ("l" in filename.lower() or "d" in filename.lower()):
        print(filename)
        filename = f'{filename.split(".")[0]}-L.{filename.split(".")[1]}'
        print(filename)


    cellarea = 0.09

    data = file.file.read().decode("utf-8")

    try:
        data = get_IV_from_content(data=data)
        data = analyze_IV(I=data["I"] ,  V=data["V"] , cellarea=cellarea)
    except:
        return res


    update_cell_IV_measurement(
        fabrication_procedure_number = 0 , 
        filename = filename , 
        batch_number = batch_number,
        encapsulation_status = encapsulation_status,
        encapsulation_material = None ,
        cellarea = 0.09,

        Jsc = data["Jsc"],
        Voc = data["Voc"],
        FF = data["FF"],
        Eff = data["Eff"],
        Pmax = data["Pmax"],
        Vmp = data["Vmp"],
        Imp = data["Imp"],
    )

    return res




@app.put("/update-batch/config/{batch_number}" , tags=["Batch"])
async def update_batch_configurations(
    batch_number : int,
    fabrication_procedure : int = Query(1 , enum = [i+1 for i in range(9)]),
    encapsulation_procedure : int = Query(1 , enum = [i+1 for i in range(8)]),
    update_times : bool = False,
    fabrication_time : datetime = datetime.now(),
    encapsulation_time : datetime = datetime.now(),
):
    
    return update_batch_params(
        batch_number = batch_number,
        fabrication_procedure = fabrication_procedure,
        encapsulation_procedure = encapsulation_procedure,
        update_times = update_times,
        fabrication_time = fabrication_time,
        encapsulation_time = encapsulation_time,
    )

@app.delete("/batch/delete/{batch_number}" , tags=["Batch"])
async def delete_one_batch(
    batch_number : int,
):

    return delete_batch(batch_number=batch_number)

@app.get("/procedure/get-all" , tags=["Procedures"],)
async def get_all_procedures(
    procedure_type : str = Query("encapsulation" , enum = ("encapsulation" , "fabrication"))
):

    return get_procedures(
        procedure_type = procedure_type
    )

@app.post("/fabrication-procedure/{id}" , tags=["Procedures"],)
async def create_fabrication_procedure(
    id : int,
    name : str,
    description : str,
):

    return update_fabrication_procedure(
        id = id,
        name = name,
        description = description
    )

@app.post("/encapsulation-procedure/{id}" , tags=["Procedures"],)
async def create_encapsulation_procedure(
    id : int,
    pressure : float,
    kapton_in_gb : bool,
    encapsulation_in_gb : bool,
    encapsulation_material : str = Query(analyze.encapsulation_types[0] , enum = analyze.encapsulation_types),
    name : str = None,
):

    return update_encapsulation_procedure(
        id = id,
        name = name,
        pressure = pressure,
        kapton_in_gb = kapton_in_gb,
        encapsulation_in_gb = encapsulation_in_gb,
        encapsulation_material = encapsulation_material,
    )

@app.get("/celldata/get-all" , tags=["Cell data"])
async def get_all_cells():
    return get_all_cell_data()

# disply home page
@app.get("/" , tags=["stats"])
def display_dashboard(

):
    
    data = get_all_cell_data()
    
    batch_numbers_list , pixel_for_batch = get_pixels_in_batch(data)
    encapsulation_types_yield_data = get_encapsulations_yeild_numbers()
    

    content_replace = {

        "encapsulation_types_list" : str([""] + encapsulation_types + [""]),
        "encapsulation_types_yield_data" : str([0] + encapsulation_types_yield_data + [0]),

        "batch_list" : str(batch_numbers_list),
        "num_of_pixels_in_batch" : str(pixel_for_batch),

        # "celldata_table" : dict_to_html_table(data),
        # "procedures_table" : str(get_procedures(format="html-table"))
    }


    with open("static/index.html" , 'r') as f:    
        html_content = f.read()
        for key in content_replace.keys():
            html_content = html_content.replace(
                key , content_replace[key]
            )

    return HTMLResponse(content=html_content, status_code=200)
