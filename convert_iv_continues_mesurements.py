import os
import pandas as pd
from datetime import datetime

source_dir = "."

for folder in os.listdir(source_dir):

    if folder.endswith("exe"):
        continue


    print(folder)
    
    data = {
        "name" : [],
        "Voc" : [],
        "Isc" : [],
        "FF" : [],
        "timestamp" : []
    }
    try:

        for filename in os.listdir(os.path.join(source_dir , folder)):
            
            with open(os.path.join(source_dir , folder , filename)) as f:
                file_data = f.read()

            sec_row = file_data.split("\n")[1]
            sec_row = sec_row.split("\t")
            
            data['name'].append(filename)
            data["Voc"].append(sec_row[0])
            data["Isc"].append(sec_row[1])
            data["FF"].append(sec_row[2])
            ts = filename.split("_")
            timestamp = f"{ts[2]}-{ts[3]}-{ts[4]} {ts[5]}:{ts[6]}:{ts[7]}"
            data["timestamp"].append(timestamp)
        
    except:
        pass

    df = pd.DataFrame.from_dict(data)

    df.to_csv(f"{folder}.csv" , index=False)



input("\n\nPress Enter to exit...")