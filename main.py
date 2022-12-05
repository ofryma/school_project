import os
from database import *
import pandas as pd
import numpy as np
import matplotlib


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

print(read_our_csv(datafile_url))

