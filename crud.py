from database import CellData , session , FabricationProcedure , EncapsulationProcedure
from datetime import datetime
from pydantic import BaseModel
import pandas
import analyze
from sqlalchemy import and_


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
    image_path : str = None

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

def update_cell_image_path(batch_number : int , cell_number : int , image_path : str):



    search_term = f'%{cell_number}%'

    results = session.query(CellData).filter(
        and_(
            CellData.batch_number == batch_number,
            CellData.src_filename.like(search_term), 
            )
    ).all()

    for record in results:
        record.image_path = image_path
    
    session.commit()

    return


def update_cell_IV_measurement(
    **kwargs
):

    q = session.query(CellData)
    
    try:
        q = q.filter(
            CellData.src_filename == kwargs.get('filename'),
            CellData.batch_number == kwargs.get('batch_number')
            )
        record = q.first()
    except:
        record = None

    new = False

    if record == None:

        record = CellData(
            src_filename = kwargs.get('filename'),
        )
        new = True
    

    record.bias , record.light = analyze.get_check_criteria(kwargs.get('filename'))
    
    if kwargs.get("encapsulation_status") == "before":
        record.Jsc_before = kwargs.get("Jsc")
        record.Uoc_before = kwargs.get("Voc")
        record.FF_before = kwargs.get("FF")
        record.Eff_before = kwargs.get("Eff")
        record.pass_cell = analyze.is_pass(kwargs.get("Eff"))
        

        try:
            record.Pmax_before = kwargs.get("Pmax")
            record.Vmp_before = kwargs.get("Vmp")
            record.Imp_before = kwargs.get("Imp")
        except:
            pass
    
    elif kwargs.get('encapsulation_status') == "after":
        record.Jsc_after = kwargs.get("Jsc")
        record.Uoc_after = kwargs.get("Voc")
        record.FF_after = kwargs.get("FF")
        record.Eff_after = kwargs.get("Eff")

        try:
            record.yeild_cell = analyze.is_yield(record.Eff_before , kwargs.get("Eff"))
        except Exception as e:
            print(e)
        
        record.encap_prod_date = datetime.now()
        try:
            record.Pmax_after =  kwargs.get("Pmax")
            record.Vmp_after = kwargs.get("Vmp")
            record.Imp_after = kwargs.get("Imp")
        except:
            pass

    try:
        if not kwargs.get("extra_notes") == "":
            try:
                if new:
                    old_notes = record.extra_notes + " | "
                else:
                    old_notes = ""
            except:
                old_notes = ""
            record.extra_notes = old_notes + kwargs.get("extra_notes")
    except:
        pass

    
    record.device_area = kwargs.get("cellarea")
    record.batch_number = kwargs.get("batch_number" , 0)

    if new:
        session.add(record)
        
    session.commit()

    return record

def update_batch_params(
    **kwargs
):
    q = session.query(CellData)
    try:
        q = q.filter(
            CellData.batch_number == kwargs.get("batch_number")
            )
        records = q.all()
    except:
        return "This batch not exsits"
    if records == None:
        return records
    


    for record in records:
        
        record.encap_procedure_number = kwargs.get("encapsulation_procedure")
        record.fabrication_procedure_number = kwargs.get("fabrication_procedure")

        if kwargs.get("update_times"):
            record.encap_prod_date = kwargs.get("encapsulation_time")
            record.prod_date = kwargs.get("production_time")
        
    session.commit()

def delete_batch(batch_number : int):

    try:
        records = session.query(CellData).filter_by(batch_number = batch_number).all()

        for record in records:
            session.delete(record)

        session.commit()

        msg_res = "Batch Deleted"
    except:
        msg_res = "There was a problem with deleting this batch"
    return msg_res

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

def update_fabrication_procedure(**kwargs):

    q = session.query(FabricationProcedure)
    
    q = q.filter(
        FabricationProcedure.id == kwargs.get("id")
        )
    record = q.first()
    try:
        record.id = kwargs.get("id")
        record.name = kwargs.get("name")
        record.description = kwargs.get("description")
    except:
        record = FabricationProcedure(
            id = kwargs.get("id"),
            name = kwargs.get("name"),
            description = kwargs.get("description")
        )
        session.add(record)
    
    
    session.commit()

    return session.query(FabricationProcedure).filter_by(id = kwargs.get("id")).first()

def update_encapsulation_procedure(**kwargs):
    
    q = session.query(EncapsulationProcedure)

    q = q.filter(
        EncapsulationProcedure.id == kwargs.get("id")
        )
    record = q.first()



    try:
        record.id = kwargs.get("id")
        record.name = kwargs.get("name")
        record.pressure = kwargs.get("pressure")
        record.kapton_in_gb = kwargs.get("kapton_in_gb")
        record.encapsulation_in_gb = kwargs.get("encapsulation_in_gb")
        record.encapsulation_material = kwargs.get("encapsulation_material")
    except:
        record = EncapsulationProcedure(
            id = kwargs.get("id"),
            name = kwargs.get("name"),
            pressure = kwargs.get("pressure"),
            kapton_in_gb = kwargs.get("kapton_in_gb"),
            encapsulation_in_gb = kwargs.get("encapsulation_in_gb"),
            encapsulation_material = kwargs.get("encapsulation_material"),
        )
        session.add(record)
    
    
    session.commit()

    return session.query(EncapsulationProcedure).filter_by(id = kwargs.get("id")).first()

def get_procedures(**kwargs):


    if kwargs.get("procedure_type") == "fabrication":
        q = session.query(FabricationProcedure)
    elif kwargs.get("procedure_type") == "encapsulation":
        q = session.query(EncapsulationProcedure)
    
    return q.all()

def get_encapsulations_yeild_numbers():
    
    yeild_data_list = []
    number_list_for_material = {}

    for material in analyze.encapsulation_types:
        records = session.query(EncapsulationProcedure).filter_by(encapsulation_material = material).all()
        for record in records:
            try:
                number_list_for_material[material] += [record.id]
            except:
                number_list_for_material[material] = [record.id]

        
    for material in analyze.encapsulation_types:

        pass_records = []
        yeild_records = []

        for encap_num in number_list_for_material[material]:

            pass_records += session.query(CellData).filter_by(
                pass_cell = True,
                encap_procedure_number = encap_num,
                bias = "R",
                light = "L",
            ).all()

            yeild_records += session.query(CellData).filter_by(
                yeild_cell = True,
                encap_procedure_number = encap_num,
                bias = "R",
                light = "L",
            ).all()
            
        try:
            yeild_data_list.append(len(yeild_records) / len(pass_records) * 100)
        except:
            yeild_data_list.append(0)
        
    return yeild_data_list