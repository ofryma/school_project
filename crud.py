from database import CellData , session
from datetime import datetime
from pydantic import BaseModel
import pandas


class CellDataCreate(BaseModel):

    src_filename : str
    batch_number : int
    prod_date : datetime
    
    Jsc_before : float
    Uoc_before : float
    FF_before : float
    Eff_before : float
    
    Jsc_after : float
    Uoc_after : float
    FF_after : float
    Eff_after : float
    
    device_area : float

    device_transperacy : int
    number_of_layers : int
    Substrate_material : str

    # Layer 1
    l1_function : str
    l1_material : str
    l1_fabrication_method : str
    l1_thickness : float
    l1_prod_date : datetime

    # Layer 2
    l2_function : str
    l2_material : str
    l2_fabrication_method : str
    l2_thickness : float
    l2_prod_date : datetime

    # Layer 3
    l3_function : str
    l3_material : str
    l3_fabrication_method : str
    l3_thickness : float
    l3_prod_date : datetime

    # Layer 4
    l4_function : str
    l4_material : str
    l4_fabrication_method : str
    l4_thickness : float
    l4_prod_date : datetime
    l4_ratio : str
    Processing_solvent : str
    Additive_1 : str
    Additive_1_concentration  : float
    Additive_2   : str
    Additive_2_concentration : float
    Active_layer_treatment_from_processing : str
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
    l5_function : str
    l5_material : str
    l5_fabrication_method : str
    l5_thickness : float
    l5_prod_date : datetime
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
    l6_function : str
    l6_material : str
    l6_fabrication_method : str
    l6_thickness : float
    l6_prod_date : datetime
    # Growth rate 1
    # Growth rate 2
    # Base pressure
    # Substrate temperature
    # Co-deposition (yes/no)
    # Ratio (if co-deposited)
    # Annealing temperature (if used)
    # Annealing solvent (if used)  
    # Annealing time (if used)

    # Encap
    
    encap_prod_date : datetime
    encap_in_GB : int
    encap_stored_location : str
    encap_material : str
    applied_presure : int
    process_time_interval : datetime
    extra_notes : str

def dict_to_html_table(data : dict):
    columns = ""
    for key in data.keys():
        columns += f'<th scope="col">{key}</th>'
    table_head = "<thead><tr>" + columns + "</tr></thead>"

    table_body = "<tbody>"
    for i in range(len(data[list(data.keys())[0]])):
        table_body += "<tr>"
        scope = 'scope="row"'
        for key in data.keys():
            table_body += f'<th {scope}>{data[key][i]}</th>'
            scope = ""
        table_body += '</tr>'
    
    table_body += '</tbody>'

    table = '<table class="table table-striped table-bordered">' + table_head + table_body + '</table>'

    return table

def get_all_cell_data(format = 'python-dictionary'):

    ignore_keys = ['_sa_instance_state']

    records = session.query(CellData).all()

    data = {}

    for row in records:
        row_dict = dict(row.__dict__)

        for k in row_dict.keys():
            if k in ignore_keys:
                continue
            try:
                data[k] += [row_dict[k]]
            except:
                data[k] = [row_dict[k]]

    if format == "html-table":
        data = dict_to_html_table(data)

    return data

def update_cell_IV_measurement(
    data : dict,
):
    q = session.query(CellData)
    q = q.filter(
        CellData.src_filename == data["src_filename"],
        CellData.batch_number == data["batch_number"]
        )
    record = q.first()

    new = False

    if record == None:

        record = CellData(
            src_filename = data["src_filename"],
        )
        new = True
    
    
    if data["encapsulation_status"] == "before":
        record.Jsc_before = data["Jsc"]
        record.Uoc_before = data["Voc"]
        record.FF_before = data["FF"]
        record.Eff_before = data["Eff"]
    elif data["encapsulation_status"] == "after":
        record.Jsc_after = data["Jsc"]
        record.Uoc_after = data["Voc"]
        record.FF_after = data["FF"]
        record.Eff_after = data["Eff"]
        record.encap_prod_date = datetime.now()


    if not data["extra_notes"] == "":
        try:
            if new:
                old_notes = record.extra_notes + " | "
            else:
                old_notes = ""
        except:
            old_notes = ""
        record.extra_notes = old_notes + data["extra_notes"]
    
    record.device_area = data["cellarea"]
    record.batch_number = data["batch_number"]
    record.encap_material = data["encapsulation_material"]

    if new:
        session.add(record)
        
    session.commit()

    return record

def update_batch_params(
    data : dict
):
    q = session.query(CellData)
    q = q.filter(
        CellData.batch_number == data["batch_number"]
        )
    records = q.all()

    if records == None:
        return records
    
    for record in records:
        
        record.encap_material = data["encapsulation_material"]
        record.encap_in_GB = data["encapsulation_in_GB"]
        record.encap_stored_location = data["encapsulation_stored_location"]
        if data["update_times"]:
            record.encap_prod_date = data["encapsulation_time"]
            record.prod_date = data["production_time"]
        
        record.applied_presure = data["applied_presure"]
        
        if not data["extra_notes"] == "":
            try:
                old_notes = record.extra_notes + " | "
            except:
                old_notes = ""

            record.extra_notes = old_notes + data["extra_notes"]
    
    session.commit()

def get_pixels_is_batch(data : dict) -> list:

    pixel_dict = {}

    for b in data["batch_number"]:
        try:
            pixel_dict[b] += 1
        except:
            pixel_dict[b] = 1
        
    print(pixel_dict)

    batch_numbers_list = []
    pixel_for_batch = []

    for key in pixel_dict.keys():
        batch_numbers_list.append(key)
        pixel_for_batch.append(pixel_dict[key])

    return batch_numbers_list , pixel_for_batch 