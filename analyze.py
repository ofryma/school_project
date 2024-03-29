

# const 
EFF_PASS_TH = 1 # %
DIFF_EFF_FOR_YIELD = 20 # %

encapsulation_types = ["Boom apoxy" , "UV glue"]
layers = [1,2,3,4,5,6]
datafiles_types = ["all" , "IV mesure" , "xlsx"]
layers_functions = [
    "FTO" , 
    "C-TiO2" , 
    "m-TiO2 doped Li" , 
    "Perovskite" , 
    "Spiro-OMeTAD" , 
    "Au" , 
    "KW peptide" , 
    "RK peptide"
    ]


def convert_to_num(number : str) -> float:
    base_num , ten_pow = number.split("E")
    if base_num[0] == "+":
        mul = 1
    else:
        mul = -1
    
    base_num = float(base_num[1:]) * mul

    if ten_pow[0] == "+":
        mul=1
    else:
        mul=-1
    
    ten_pow = pow(10 , float(ten_pow[1:]) * mul)

    return base_num * ten_pow
        
def analyze_IV( I : list , V : list , cellarea : float , Pin : float = 1):


    # I - the current
    # V - voltage
    # Voc - The voltage where I = 0
    # Jsc - The current where V = 0
    # Pmax - max of I*V
    # FF - Pmax / (Vox * Isc)
    # Eff - ( Pmax * 1000) / cellarea
    # cellarea - the area on the cell that is under light

    # find the colsest value to zero
    I_abs = [abs(i) for i in I]
    V_abs = [abs(v) for v in V]
    Voc = V[I_abs.index(min(I_abs))]
    Isc = I[V_abs.index(min(V_abs))]
    Jsc = abs(Isc / cellarea)

    P = [i*v for i , v in zip(I , V)]
    Pmax = min(P)
    Vmp = V[P.index(Pmax)]
    Imp = I[P.index(Pmax)]

    FF = (Vmp * Imp) / (Isc * Voc)
    Eff = ( Pmax * 1000) / cellarea

    change_unit = 1000 # change from V to mV and from A to mA

    data = {
        "Pmax" : abs(Pmax) * change_unit**2 , # [mV * mA]
        "Voc" : Voc * change_unit, # [mV]
        "Jsc" : Jsc * change_unit, # [mA / cm^2]
        "Isc" : Isc * change_unit, # [mA]
        "Vmp" : Vmp * change_unit,
        "Imp" : Imp * change_unit,
        "FF" : abs(FF) * 100, # [%]
        "Eff" : abs(Eff) , # [%]
        "cellarea" : cellarea, # [cm^2]
    }

    return data

def get_IV_from_content(data : str) -> dict:

    """
    This function extracts the I and V vectors from the content 
    of the txt files

    returns: dictionary with two arrays of numbers - I and V
    {
        "I" : [],
        "V" : []
    }
    """
    data = data.split("\n")
    data = data[2:]
    I = []
    V = []

    for row in data:
        try:
            v , i = row.split("\t")

            I.append(convert_to_num(i))
            V.append(convert_to_num(v))
        except Exception as e:
            print(e)
    
    return {"I" : I , "V" : V}

def read_from_all_file(txt : str) -> any:
    
    txt_lines = txt.split("\n")

    # first line is the headers:
    txt_lines.pop(0)
    data_dict = {
        "filename" : [] ,
        "Uoc" : [],
        "Jsc" : [] ,
        "FF" : [] ,
        "Eff" : [] ,
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
        data_dict["Uoc"].append(line_list[1])
        data_dict["Jsc"].append(line_list[2])
        data_dict["FF"].append(line_list[3])
        data_dict["Eff"].append(line_list[4])
        data_dict["cellarea"].append(line_list[5])
    
    return data_dict

def read_our_csv(csv_url : str) -> any:
    
    with open(csv_url , "r") as datafile:
        txt = datafile.read()
    
    txt_lines = txt.split("\n")

    # first line is the headers:
    txt_lines.pop(0)
    data_dict = {
        "filename" : [] ,
        "Uoc" : [],
        "Jsc" : [] ,
        "FF" : [] ,
        "Eff" : [] ,
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
        data_dict["Uoc"].append(line_list[1])
        data_dict["Jsc"].append(line_list[2])
        data_dict["FF"].append(line_list[3])
        data_dict["Eff"].append(line_list[4])
        data_dict["cellarea"].append(line_list[5])
    
    return data_dict

def is_pass(pixel_eff : float) -> bool:

    if float(pixel_eff) > EFF_PASS_TH:
        return True
    return False

def is_yield(before_encap_eff : float , after_encap_eff : float ) -> bool:

    """
        If the different between the efficiancy before and after
        encapsulation is greater than 20 % change, than this pixel
        is not count as good encapsulated cell
    """
    before_encap_eff = float(before_encap_eff)
    after_encap_eff = float(after_encap_eff)

    if after_encap_eff >= before_encap_eff:
        return True

    delta_eff = abs(before_encap_eff - after_encap_eff)

    if  (delta_eff / before_encap_eff) * 100 <  DIFF_EFF_FOR_YIELD:
        return True
    
    return False

def get_check_criteria(src_filename : str):

    bias = "R"
    light = "L"

    if "f" in src_filename.lower():
        bias = "F"
    elif "r" in src_filename.lower():
        bias = "R"
    
    if "l" in src_filename.lower():
        light = "L"
    elif "d" in src_filename.lower():
        light = "D"
        
    return bias , light



