import uproot
import numpy as np
import re
import os

root = uproot.open("real:/eos/user/t/tsculac/BigStuff/HGCAL/DoublePhoton_FlatPt-1To100_0PU_fromMartina/ntuple_doublePhotons_1k_OKAY.root")
tree = root.get("l1tHGCalTriggerNtuplizer/HGCalTriggerNtuple;21")
print(tree.keys())
selected_branches = ["ts_energy","ts_layer","event","ts_waferu","ts_waferv","ts_zside"]
branches = tree.arrays(selected_branches)

event = 5121

def get_index(array, layer):
    numpy_array = np.asarray(array).flatten()
    indices = np.where(numpy_array==layer)[0]
    return indices
def dict_en(layer,ts_u,ts_v,ts_en,endcap):
    dict = {}
    for i in range(len(layer)):
        if i in endcap:
            key = str((layer[i], (ts_u[i], ts_v[i])))
            if key in dict:
                print(i)    #provjerit postoji li kljuc, dodat kod
            dict[key] = str(ts_en[i])
    return dict
def extract_data(line):
    match = re.match(r'Board_(-?\d+),Channel_(-?\d+)=Layer_(-?\d+),\s*\((-?\d+),(-?\d+)\)\s*SiModule', line)
    if match:
        key = str((int(match[3]), (int(match[4]), int(match[5]))))
        return key, int(match[1])
    
    match = re.match(r'Board_(-?\d+),Channel_(-?\d+)=Layer_(-?\d+),\s*\((-?\d+),(-?\d+)\)\s*Scintillator', line)
    if match:
        key = str((int(match[3]), (int(match[4]), int(match[5]))))
        return key, int(match[1])

    # Ovdje nema dodatnih linija koda

    return np.nan, np.nan


def make_board_files(file,dict,directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(file, "r") as file:
        energies = np.array([])
        write_file = 0
        for line in file:
            line = line.replace(" ","").replace("\t", "")
            key,board = extract_data(line)            
            if key == key:
                if board == write_file:
                    
                    try:
                        energies = np.append(energies,dict[key])
                    except KeyError:
                        energies = np.append(energies,0) #nema toga kljuca u rijecniku
                        continue
                else:
                    np.savetxt(f"{directory}/Board_{write_file}.txt", energies, fmt='%s')
                    write_file = board
                    energies = np.array([])
                    try:
                        energies = np.append(energies,dict[key])
                    except KeyError:
                        energies = np.append(energies,0) #nema toga kljuca u rijecniku
                        continue
        
        np.savetxt(f"{directory}/Board_13.txt", energies, fmt='%s')

event_index = get_index(branches["event"],event)
u = np.asarray(branches["ts_waferu"][event_index]).flatten()
v = np.asarray(branches["ts_waferv"][event_index]).flatten()
energy = np.asarray(branches["ts_energy"][event_index]).flatten()
layer = np.asarray(branches["ts_layer"][event_index]).flatten()
u = u - np.min(u)
v = v - np.min(v)
index_endcap = get_index(branches["ts_zside"][event_index], 1)
dict_energy = dict_en(layer,u,v,energy,index_endcap)
make_board_files("Input_CEE_pTT.txt",dict_energy,"Outputs_CEE")
make_board_files("Input_CEH_pTT.txt",dict_energy,"Outputs_CEH")