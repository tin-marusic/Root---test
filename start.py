import uproot
import numpy as np
import matplotlib.pyplot as plt
import os

root = uproot.open("ntuple_doublePhotons_1k_OKAY.root")
tree = root["l1tHGCalTriggerNtuplizer/HGCalTriggerNtuple;20"]
print(tree.keys())
selected_branches = ["ts_x", "ts_y", "ts_energy","ts_layer","event","gen_eta","gen_energy","gen_pt"]
branches = tree.arrays(selected_branches)

#Funkcija za dobivanje indeksa layera(koristit ce se i za dobivanje indeksa eventa)
def get_index(array,layer):
    numpy_array = np.asarray(array)
    indeksi = np.where(numpy_array==layer)[0]
    return indeksi

def eta_index(array): #Funkcija koja trazi na kojem je indeksu gen_eta>0, u gen_eta postoje samo dva elementa za svaki event
    numpy_array = np.asarray(array)
    if numpy_array[0] > 0:
        return 0
    else:
        return 1

def obrisi_datoteke_iz_mape(putanja_do_mape):
    for datoteka in os.listdir(putanja_do_mape):
        putanja_do_datoteke = os.path.join(putanja_do_mape, datoteka)
        os.remove(putanja_do_datoteke)
        
def dodaj_u_liste(list_x,list_y,list_e,x,y,e): #funkcija koja ce sluziti za sumiranje eneragija svih layera
    preklapanje = False
    for i in range(len(list_x)):
        if abs(list_x[i] - x) <= 10.5 and abs(list_y[i] - y) <= 10.5: #provjera imamo li preklapanje 
            list_e[i] += e
            preklapanje = True
            break
    if not preklapanje: #ako nismo imali preklapanje samo dodajemo tu koordinatu u liste
        list_x.append(x)
        list_y.append(y)
        list_e.append(e)
                    
    return list_x,list_y,list_e

def plot_hexagon(list_x,list_y,list_e,i):
    #izrada heksagonskog plota
    if len(list_e) > 1:
        ht = plt.hexbin(list_y,list_x, C=list_e, cmap='plasma', gridsize=23, vmax=(np.max(list_e)), vmin=np.min(list_e),extent=[-125,125,-125,125])
    else:
        ht = plt.hexbin(list_y,list_x, C=list_e, cmap='plasma', gridsize=23, vmax=(np.max(list_e)), vmin=np.min(list_e) - 0.05,extent=[-125,125,-125,125])
    #print(f"{i}. : {list_x},{list_y}")
    cb = plt.colorbar(ht)  
    cb.set_label("vrijednost energije")
    plt.xlabel("ts_y")
    plt.ylabel("ts_x")
    plt.title(f"ts_y:ts_x:ts_energy   |   ts_layer == {i}, event == {event} \n gen_energy = {gen_energy:.4f}    |    gen_pt = {gen_pt:.4f}")
    plt.savefig(f"Plotovi/plot{i}.png")
    plt.clf()
        
obrisi_datoteke_iz_mape("Plotovi")
obrisi_datoteke_iz_mape("Preklapanja")

event = 4674

event_indeks = get_index(branches["event"],event)[0] #dobivamo indeks layera, on je jedinstven u banchu layers
ts_layer = np.asarray(branches["ts_layer"][event_indeks]) #prebacujemo se u numpy oblik podataka

#trazimo vrijednost energije fotona za odredeni event 
gen_eta_index = eta_index(branches["gen_eta"][event_indeks])
gen_energy = branches["gen_energy"][event_indeks][gen_eta_index]
gen_pt = branches["gen_pt"][event_indeks][gen_eta_index]

# Izračuni minimum i maksimum
min_layer = np.min(ts_layer)
max_layer = np.max(ts_layer)

suma_list_x = []
suma_list_y = []
suma_list_e = []

# Iteracija kroz layere
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
            suma_list_x,suma_list_y,suma_list_e = dodaj_u_liste(suma_list_x,suma_list_y,suma_list_e,branches["ts_x"][event_indeks][j],
                                                                branches["ts_y"][event_indeks][j],branches["ts_energy"][event_indeks][j])  
        
        f = open(f"Preklapanja/preklapanja_layer_{i}.txt","w")
        #provjera preklapanja koordinata tocaka
        for j in range(len(list_x)):
            for k in range(j + 1, len(list_x)):
                try:
                    if abs(list_x[k] - list_x[j]) <= 10.5 and abs(list_y[k] - list_y[j]) <= 10.5: #10.5 je priblizna apotema heksagona za parametre plota koje koristimo
                        f.write(f"preklapanje na koordinatama ({list_x[j],list_y[j]}),({list_x[k],list_y[k]}) - zbrojene energije {list_e[j]} i {list_e[k]} \n")
                        #zbrajamo energije na mjestu gdje je nastalo preklapanje
                        list_e[j] += list_e[k]
                        # Jednu koordinatu preklapanja brisemo, to su ove tocke. Ne mozemo ih brisati u petlji pa ih postavljamo na vrijednost koja nece utjecati na petlju
                        list_x[k] = np.nan
                        list_y[k] = np.nan
                        list_e[k] = np.nan
                except: #slucaj kada se oduzima broj i np.nan
                    continue
        
        #Uklanjamo preklopljene vrijednosti, tj uklanjamo np.nan elemente iz liste 
        list_x = list_x[~np.isnan(list_x)]
        list_y = list_y[~np.isnan(list_y)]
        list_e = list_e[~np.isnan(list_e)]
        f.close()
        
        #brisemo prazne datoteke - layeri u kojima nije bilo preklapanja
        if os.path.getsize(f"Preklapanja/preklapanja_layer_{i}.txt") == 0:
            os.remove(f"Preklapanja/preklapanja_layer_{i}.txt")
        
        plot_hexagon(list_x,list_y,list_e,i)
        
plot_hexagon(suma_list_x,suma_list_y,suma_list_e,"suma svih")        