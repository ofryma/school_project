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
import scipy
from math import pow
import openpyxl
import io

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



@app.post("/datafile/upload-data/{batch_number}" , tags=["Data files"])
async def create_file(
    batch_number : int,
    procedure_name : str = Query(procdure_name_list[0] , enum = procdure_name_list),
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
            cur_cell_data["procedure_name"] = procedure_name
            cur_cell_data["batch_number"] = batch_number
            cur_cell_data["encapsulation_status"] = encapsulation_status
            cur_cell_data["encapsulation_material"] = encapsulation_material
            cur_cell_data["extra_notes"] = extra_notes

            res.append(cur_cell_data)
            update_cell_IV_measurement(cur_cell_data)

    elif file_type == "IV mesure":
        data = get_IV_from_content(data=data)
        data = analyze_IV(I=data["I"] ,  V=data["V"] , cellarea=cellarea)

        data["procedure_name"] = procedure_name
        data["src_filename"] = filename
        data["batch_number"] = batch_number
        data["encapsulation_status"] = encapsulation_status
        data["encapsulation_material"] = encapsulation_material
        data["extra_notes"] = extra_notes

        res.append(data)
        update_cell_IV_measurement(data)


    return res




@app.put("/update-batch/config/{batch_number}" , tags=["Batch"])
async def update_batch_configurations(
    batch_number : int,
    procedure : str = Query(procdure_name_list[0] , enum = procdure_name_list),
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
    data["procedure"] = procedure
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


@app.delete("/batch/delete/{batch_number}" , tags=["Batch"])
async def delete_one_batch(
    batch_number : int,
):

    return delete_batch(batch_number=batch_number)


@app.post("/procedure/add-new/{procedure_name}" , tags=["Procedures"])
async def add_new_procedure(
    procedure_name : str,
    device_transperacy : int = None,
    number_of_layers : int = None,
    Substrate_material : str = None,

    # Layer 1
    l1_function : str = Query(layers_functions[0] ,enum = layers_functions),
    l1_material : str = None,
    l1_fabrication_method : str = None,
    l1_thickness : float = None,
    

    # Layer 2
    l2_function : str = Query(layers_functions[0] ,enum = layers_functions),
    l2_material : str = None,
    l2_fabrication_method : str = None,
    l2_thickness : float = None,
    

    # Layer 3
    l3_function : str = Query(layers_functions[0] ,enum = layers_functions),
    l3_material : str = None,
    l3_fabrication_method : str = None,
    l3_thickness : float = None,
    

    # Layer 4
    l4_function : str = Query(layers_functions[0] ,enum = layers_functions),
    l4_material : str = None,
    l4_fabrication_method : str = None,
    l4_thickness : float = None,
    
    l4_ratio : str = None,
    Processing_solvent : str = None,
    Additive_1 : str = None,
    Additive_1_concentration  : float = None,
    Additive_2   : str = None,
    Additive_2_concentration : float = None,
    Active_layer_treatment_from_processing : str = None,
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
    l5_function : str = Query(layers_functions[0] ,enum = layers_functions),
    l5_material : str = None,
    l5_fabrication_method : str = None,
    l5_thickness : float = None,
    
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
    l6_function : str = Query(layers_functions[0] ,enum = layers_functions),
    l6_material : str = None,
    l6_fabrication_method : str = None,
    l6_thickness : float = None,
    
    # Growth rate 1
    # Growth rate 2
    # Base pressure
    # Substrate temperature
    # Co-deposition (yes/no)
    # Ratio (if co-deposited)
    # Annealing temperature (if used)
    # Annealing solvent (if used)  
    # Annealing time (if used)

    extra_description : str = None,
):

    data = {}
    
    data['device_transperacy'] = device_transperacy
    data['number_of_layers'] = number_of_layers
    data['Substrate_material'] = Substrate_material
    data['l1_function'] = l1_function
    data['l1_material'] = l1_material
    data['l1_fabrication_method'] = l1_fabrication_method
    data['l1_thickness'] = l1_thickness
    
    data['l2_function'] = l2_function
    data['l2_material'] = l2_material
    data['l2_fabrication_method'] = l2_fabrication_method
    data['l2_thickness'] = l2_thickness
    
    data['l3_function'] = l3_function
    data['l3_material'] = l3_material
    data['l3_fabrication_method'] = l3_fabrication_method
    data['l3_thickness'] = l3_thickness
    
    data['l4_function'] = l4_function
    data['l4_material'] = l4_material
    data['l4_fabrication_method'] = l4_fabrication_method
    data['l4_thickness'] = l4_thickness
    
    data['l4_ratio'] = l4_ratio
    data['Processing_solvent'] = Processing_solvent
    data['Additive_1'] = Additive_1
    data['Additive_1_concentration'] = Additive_1_concentration
    data['Additive_2'] = Additive_2
    data['Additive_2_concentration'] = Additive_2_concentration
    data['Active_layer_treatment_from_processing'] = Active_layer_treatment_from_processing
    data['l5_function'] = l5_function
    data['l5_material'] = l5_material
    data['l5_fabrication_method'] = l5_fabrication_method
    data['l5_thickness'] = l5_thickness
    
    data['l6_function'] = l6_function
    data['l6_material'] = l6_material
    data['l6_fabrication_method'] = l6_fabrication_method
    data['l6_thickness'] = l6_thickness
    
    data['extra_description'] = extra_description


    return add_procedure(procedure_name=procedure_name , data=data)

@app.put("/procedure/update" , tags=["Procedures"])
async def update_one_procedure(
    procedure_name : str = Query(procdure_name_list[0] , enum=procdure_name_list),
    device_transperacy : int = None,
    number_of_layers : int = None,
    Substrate_material : str = None,

    # Layer 1
    l1_function : str = None,
    l1_material : str = None,
    l1_fabrication_method : str = None,
    l1_thickness : float = None,
    

    # Layer 2
    l2_function : str = None,
    l2_material : str = None,
    l2_fabrication_method : str = None,
    l2_thickness : float = None,
    

    # Layer 3
    l3_function : str = None,
    l3_material : str = None,
    l3_fabrication_method : str = None,
    l3_thickness : float = None,
    

    # Layer 4
    l4_function : str = None,
    l4_material : str = None,
    l4_fabrication_method : str = None,
    l4_thickness : float = None,
    
    l4_ratio : str = None,
    Processing_solvent : str = None,
    Additive_1 : str = None,
    Additive_1_concentration  : float = None,
    Additive_2   : str = None,
    Additive_2_concentration : float = None,
    Active_layer_treatment_from_processing : str = None,
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
    l5_function : str = None,
    l5_material : str = None,
    l5_fabrication_method : str = None,
    l5_thickness : float = None,
    
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
    l6_function : str = None,
    l6_material : str = None,
    l6_fabrication_method : str = None,
    l6_thickness : float = None,
    
    # Growth rate 1
    # Growth rate 2
    # Base pressure
    # Substrate temperature
    # Co-deposition (yes/no)
    # Ratio (if co-deposited)
    # Annealing temperature (if used)
    # Annealing solvent (if used)  
    # Annealing time (if used)

    extra_description : str = None,
):

    
    data = {}
    
    data["name"] = procedure_name
    data['device_transperacy'] = device_transperacy
    data['number_of_layers'] = number_of_layers
    data['Substrate_material'] = Substrate_material
    data['l1_function'] = l1_function
    data['l1_material'] = l1_material
    data['l1_fabrication_method'] = l1_fabrication_method
    data['l1_thickness'] = l1_thickness
    
    data['l2_function'] = l2_function
    data['l2_material'] = l2_material
    data['l2_fabrication_method'] = l2_fabrication_method
    data['l2_thickness'] = l2_thickness
    
    data['l3_function'] = l3_function
    data['l3_material'] = l3_material
    data['l3_fabrication_method'] = l3_fabrication_method
    data['l3_thickness'] = l3_thickness
    
    data['l4_function'] = l4_function
    data['l4_material'] = l4_material
    data['l4_fabrication_method'] = l4_fabrication_method
    data['l4_thickness'] = l4_thickness
    
    data['l4_ratio'] = l4_ratio
    data['Processing_solvent'] = Processing_solvent
    data['Additive_1'] = Additive_1
    data['Additive_1_concentration'] = Additive_1_concentration
    data['Additive_2'] = Additive_2
    data['Additive_2_concentration'] = Additive_2_concentration
    data['Active_layer_treatment_from_processing'] = Active_layer_treatment_from_processing
    data['l5_function'] = l5_function
    data['l5_material'] = l5_material
    data['l5_fabrication_method'] = l5_fabrication_method
    data['l5_thickness'] = l5_thickness
    
    data['l6_function'] = l6_function
    data['l6_material'] = l6_material
    data['l6_fabrication_method'] = l6_fabrication_method
    data['l6_thickness'] = l6_thickness
    
    data['extra_description'] = extra_description

    

    return update_procedure(data=data)

@app.get("/procedure/get-all" , tags=["Procedures"])
async def get_all_procedures(

):

    return get_procedures()


@app.get("/celldata/get-all" , tags=["Cell data"])
async def get_all_cells(
):
    
    return get_all_cell_data()

@app.get("/" , tags=["stats"])
def display_dashboard(

):
    
    data = get_all_cell_data()
    
    batch_numbers_list , pixel_for_batch = get_pixels_in_batch(data)
    encapsulation_types_yield_data = get_incapsulations_yeild_numbers()
    

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



if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)