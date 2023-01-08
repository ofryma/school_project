from database import CellData , Procedure , session
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
    
    try:
        q = q.filter(
            CellData.src_filename == data["src_filename"],
            CellData.batch_number == data["batch_number"]
            )
        record = q.first()
    except:
        record = None

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
    
    record.procedure = data["procedure_name"]
    record.device_area = data["cellarea"]
    record.batch_number = data["batch_number"]
    record.encap_material = data["encapsulation_material"]
    record.procedure = data["procedure_name"]

    if new:
        session.add(record)
        
    session.commit()

    return record

def update_batch_params(
    data : dict
):
    q = session.query(CellData)
    try:
        q = q.filter(
            CellData.batch_number == data["batch_number"]
            )
        records = q.all()
    except:
        return "This batch not exsits"
    if records == None:
        return records
    
    for record in records:
        
        record.procedure = data["procedure"]
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

def get_pixels_in_batch(data : dict) -> list:

    pixel_dict = {}

    try:
        for b in data["batch_number"]:
            try:
                pixel_dict[b] += 1
            except:
                pixel_dict[b] = 1
    except:
        pass

    batch_numbers_list = []
    pixel_for_batch = []

    for key in pixel_dict.keys():
        batch_numbers_list.append(key)
        pixel_for_batch.append(pixel_dict[key])

    return batch_numbers_list , pixel_for_batch 

def get_procedures_name_list():

    try:
        records = get_procedures()
        name_list = [record.name for record in records]
        name_list.append("")
        return name_list
    except:
        return [""]

procdure_name_list = get_procedures_name_list()

def get_procedures(format : str = "python-dictionary"):

    records = session.query(Procedure).all()
    data = {}
    ignore_keys = ['_sa_instance_state']
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

def update_procedure(data : dict):
    try:
        record = session.query(Procedure).filter_by(name = data["name"]).first()
    except:
        record = None
    
    if not record == None:  
        if not data['name'] == None:
            record.name = data['name']
        if not data['device_transperacy'] == None:
            record.device_transperacy = data['device_transperacy']
        if not data['number_of_layers'] == None:
            record.number_of_layers = data['number_of_layers']
        if not data['Substrate_material'] == None:
            record.Substrate_material = data['Substrate_material']
        if not data['l1_function'] == None:
            record.l1_function = data['l1_function']
        if not data['l1_material'] == None:
            record.l1_material = data['l1_material']
        if not data['l1_fabrication_method'] == None:
            record.l1_fabrication_method = data['l1_fabrication_method']
        if not data['l1_thickness'] == None:
            record.l1_thickness = data['l1_thickness']

        if not data['l2_function'] == None:
            record.l2_function = data['l2_function']
        if not data['l2_material'] == None:
            record.l2_material = data['l2_material']
        if not data['l2_fabrication_method'] == None:
            record.l2_fabrication_method = data['l2_fabrication_method']
        if not data['l2_thickness'] == None:
            record.l2_thickness = data['l2_thickness']

        if not data['l3_function'] == None:
            record.l3_function = data['l3_function']
        if not data['l3_material'] == None:
            record.l3_material = data['l3_material']
        if not data['l3_fabrication_method'] == None:
            record.l3_fabrication_method = data['l3_fabrication_method']
        if not data['l3_thickness'] == None:
            record.l3_thickness = data['l3_thickness']

        if not data['l4_function'] == None:
            record.l4_function = data['l4_function']
        if not data['l4_material'] == None:
            record.l4_material = data['l4_material']
        if not data['l4_fabrication_method'] == None:
            record.l4_fabrication_method = data['l4_fabrication_method']
        if not data['l4_thickness'] == None:
            record.l4_thickness = data['l4_thickness']

        if not data['l4_ratio'] == None:
            record.l4_ratio = data['l4_ratio']
        if not data['Processing_solvent'] == None:
            record.Processing_solvent = data['Processing_solvent']
        if not data['Additive_1'] == None:
            record.Additive_1 = data['Additive_1']
        if not data['Additive_1_concentration'] == None:
            record.Additive_1_concentration = data['Additive_1_concentration']
        if not data['Additive_2'] == None:
            record.Additive_2 = data['Additive_2']
        if not data['Additive_2_concentration'] == None:
            record.Additive_2_concentration = data['Additive_2_concentration']
        if not data['Active_layer_treatment_from_processing'] == None:
            record.Active_layer_treatment_from_processing = data['Active_layer_treatment_from_processing']
        if not data['l5_function'] == None:
            record.l5_function = data['l5_function']
        if not data['l5_material'] == None:
            record.l5_material = data['l5_material']
        if not data['l5_fabrication_method'] == None:
            record.l5_fabrication_method = data['l5_fabrication_method']
        if not data['l5_thickness'] == None:
            record.l5_thickness = data['l5_thickness']

        if not data['l6_function'] == None:
            record.l6_function = data['l6_function']
        if not data['l6_material'] == None:
            record.l6_material = data['l6_material']
        if not data['l6_fabrication_method'] == None:
            record.l6_fabrication_method = data['l6_fabrication_method']
        if not data['l6_thickness'] == None:
            record.l6_thickness = data['l6_thickness']

        if not data['extra_description'] == None:
            record.extra_description = data['extra_description']
        session.commit()

        return record.__dict__
    else:
        return "Update failed"

def add_procedure( procedure_name : str , data : dict):

    session.add(Procedure(
        name = procedure_name,
        device_transperacy = data['device_transperacy'],
        number_of_layers = data['number_of_layers'],
        Substrate_material = data['Substrate_material'],
        l1_function = data['l1_function'],
        l1_material = data['l1_material'],
        l1_fabrication_method = data['l1_fabrication_method'],
        l1_thickness = data['l1_thickness'],
        l2_function = data['l2_function'],
        l2_material = data['l2_material'],
        l2_fabrication_method = data['l2_fabrication_method'],
        l2_thickness = data['l2_thickness'],
        l3_function = data['l3_function'],
        l3_material = data['l3_material'],
        l3_fabrication_method = data['l3_fabrication_method'],
        l3_thickness = data['l3_thickness'],
        l4_function = data['l4_function'],
        l4_material = data['l4_material'],
        l4_fabrication_method = data['l4_fabrication_method'],
        l4_thickness = data['l4_thickness'],
        
        l4_ratio = data['l4_ratio'],
        Processing_solvent = data['Processing_solvent'],
        Additive_1 = data['Additive_1'],
        Additive_1_concentration = data['Additive_1_concentration'],
        Additive_2 = data['Additive_2'],
        Additive_2_concentration = data['Additive_2_concentration'],
        Active_layer_treatment_from_processing = data['Active_layer_treatment_from_processing'],
        l5_function = data['l5_function'],
        l5_material = data['l5_material'],
        l5_fabrication_method = data['l5_fabrication_method'],
        l5_thickness = data['l5_thickness'],
        
        l6_function = data['l6_function'],
        l6_material = data['l6_material'],
        l6_fabrication_method = data['l6_fabrication_method'],
        l6_thickness = data['l6_thickness'],
        
        extra_description = data['extra_description'],

    ))

    session.commit()

    try:
        record = session.query(Procedure).filter_by(name = procedure_name).first()
    except:
        record = None
    
    
    return record