import uproot
import numpy as np
import matplotlib.pyplot as plt

root = uproot.open("ntuple_doublePhotons_1k_OKAY.root")
tree = root["l1tHGCalTriggerNtuplizer/HGCalTriggerNtuple;20"]
print(tree.keys())
selected_branches = ["ts_x", "ts_y", "ts_energy","ts_layer","event"]
branches = tree.arrays(selected_branches)
print(len(branches["event"]))
print(len(branches["ts_layer"]))
print(min(branches["ts_layer"][1]))
print(max(branches["ts_layer"][1]))

#Funkcija za dobivanje indeksa layera(koristit ce se i za dobivanje indeksa eventa)
def get_index(array,layer):
    numpy_array = np.asarray(array)
    indeksi = np.where(numpy_array==layer)[0]
    return indeksi

event = 4674

event_indeks = get_index(branches["event"],event)[0] #dobivamo indeks layera, on je jedinstven u banchu layers
ts_layer = np.asarray(branches["ts_layer"][event_indeks]) #prebacujemo se u numpy oblik podataka

# Izračuna minimum i maksimum
min_layer = np.min(ts_layer)
max_layer = np.max(ts_layer)

# Iteriracija kroz layere
for i in range(min_layer, max_layer+1):
    layer_indeks = get_index(branches["ts_layer"][event_indeks],i) #dobivanje svih indeksa na kojima se nalazi određeni layer
    list_x = np.array([])
    list_y = np.array([])
    list_e = np.array([])
    if layer_indeks.size != 0 : #Provjera jesu li indeksi prazni, ocekivano za parne layere
        for j in layer_indeks: #stvaramo liste koordinata i energija za odredeni layer
            list_x = np.append(list_x,[branches["ts_x"][event_indeks][j]]) 
            list_y = np.append(list_y,[branches["ts_y"][event_indeks][j]]) 
            list_e = np.append(list_e,[branches["ts_energy"][event_indeks][j]])  
        
        ht = plt.hexbin(list_x,list_y, C=list_e, cmap='plasma', gridsize=35, vmax=(np.max(list_e)), vmin=np.min(list_e),extent=[-125,125,-125,125])
        #print(f"{i}. : {list_x},{list_y}")
        cb = plt.colorbar(ht)  
        cb.set_label("vrijednost energije")
        plt.xlabel("ts_x")
        plt.ylabel("ts_y")
        plt.title(f"ts_x:ts_y:ts_energy - ts_layer = {i}, event = {event}")
        plt.savefig(f"Plotovi/plot{i}.png")
        plt.clf()