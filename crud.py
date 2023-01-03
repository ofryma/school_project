from database import CellData , session
from datetime import datetime


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