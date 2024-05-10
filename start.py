import uproot
import numpy as np
import matplotlib.pyplot as plt
import os

root = uproot.open("ntuple_doublePhotons_1k_OKAY.root")
tree = root.get("l1tHGCalTriggerNtuplizer/HGCalTriggerNtuple;21")
print(tree.keys())
selected_branches = ["ts_x", "ts_y", "ts_energy","ts_layer","event","gen_eta","gen_phi","gen_energy","gen_pt",'ts_zside']
branches = tree.arrays(selected_branches)

# Function for getting the layer index (will also be used for getting the event index)
def get_index(array, layer):
    numpy_array = np.asarray(array)
    indices = np.where(numpy_array==layer)[0]
    return indices

def eta_index(array): # Function to find the index where gen_eta > 0, there are only two elements in gen_eta for each event
    numpy_array = np.asarray(array)
    if numpy_array[0] > 0:
        return 0
    else:
        return 1

def delete_files_from_directory(directory_path):
    for file in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file)
        os.remove(file_path)
        
def add_to_lists(list_x, list_y, list_e, x, y, e): # Function to sum energies of all layers
    overlap = False
    for i in range(len(list_x)):
        if abs(list_x[i] - x) <= 10.5 and abs(list_y[i] - y) <= 10.5: # Checking for overlap 
            list_e[i] += e
            overlap = True
            break
    if not overlap: # If there was no overlap, simply add the coordinates to the lists
        list_x.append(x)
        list_y.append(y)
        list_e.append(e)
                    
    return list_x, list_y, list_e

def plot_hexagon(list_x, list_y, list_e, i):
    # Creating hexagonal plot
    if len(list_e) > 1:
        ht = plt.hexbin(list_y, list_x, C=list_e, cmap='plasma', gridsize=23, vmax=(np.max(list_e)), vmin=np.min(list_e),extent=[-125,125,-125,125])
    else:
        ht = plt.hexbin(list_y, list_x, C=list_e, cmap='plasma', gridsize=23, vmax=(np.max(list_e)), vmin=np.min(list_e) - 0.05,extent=[-125,125,-125,125])
    #print(f"{i}. : {list_x},{list_y}")
    plt.plot(y, x, 'rx')  # 'rx' specifies red color ('r') and 'x' marker
    cb = plt.colorbar(ht)  
    cb.set_label("Energy value")
    plt.xlabel("ts_y")
    plt.ylabel("ts_x")
    plt.title(f"ts_y:ts_x:ts_energy   |   ts_layer == {i}, event == {event} \n gen_energy = {gen_energy:.4f}    |    gen_pt = {gen_pt:.4f} \n Coordinates of photon entry (mm): ({x},{y})", fontsize=9)
    plt.savefig(f"Plots/plot{i}.png")
    plt.clf()
        
def find_coord(eta, phi, z): # Determining the position of photon entry
    theta = 2 * np.arctan(np.exp(-eta))
    r = z * np.tan(theta)
    x = np.round(r * np.cos(phi), 2)
    y = np.round(r * np.sin(phi), 2)
    
    return x, y     
    
delete_files_from_directory("Plots")
delete_files_from_directory("Overlaps")

event = 5332
z_0 = 321.947 # Distance of the 1st layer from the origin of the HGCal detector
z = z_0
event_index = get_index(branches["event"], event)[0] # Getting the layer index, which is unique in the layers branch
ts_layer = np.asarray(branches["ts_layer"][event_index]) # Converting to numpy array

# Finding photon energy value for a specific event 
gen_eta_index = eta_index(branches["gen_eta"][event_index])
gen_energy = branches["gen_energy"][event_index][gen_eta_index]
gen_pt = branches["gen_pt"][event_index][gen_eta_index]

# Calculating coordinates of photon entry 
eta = branches["gen_eta"][event_index][gen_eta_index]
phi = branches["gen_phi"][event_index][gen_eta_index]

# Calculating minimum and maximum
min_layer = np.min(ts_layer)
max_layer = np.max(ts_layer)

sum_list_x = []
sum_list_y = []
sum_list_e = []

# Finding eta to be greater than 0
index_endcap = get_index(branches["ts_zside"][event_index], 1)

# Iterating through layers
for i in range(min_layer, max_layer+1):
    layer_index = get_index(branches["ts_layer"][event_index], i) # Getting all indices where a specific layer is located
    layer_index_endcap = []
    for j in layer_index:
        if j in index_endcap:
            layer_index_endcap.append(j)
    list_x = np.array([])
    list_y = np.array([])
    list_e = np.array([])
    if len(layer_index_endcap) != 0 : # Checking if the indices are empty, expected for even layers
        for j in layer_index_endcap: # Creating lists of coordinates and energies for a specific layer
            list_x = np.append(list_x, [branches["ts_x"][event_index][j]]) 
            list_y = np.append(list_y, [branches["ts_y"][event_index][j]]) 
            list_e = np.append(list_e, [branches["ts_energy"][event_index][j]])
            sum_list_x, sum_list_y, sum_list_e = add_to_lists(sum_list_x, sum_list_y, sum_list_e, branches["ts_x"][event_index][j],
                                                                branches["ts_y"][event_index][j], branches["ts_energy"][event_index][j])  
        
        f = open(f"Overlaps/overlaps_layer_{i}.txt", "w")
        # Checking for coordinate overlaps
        for j in range(len(list_x)):
            for k in range(j + 1, len(list_x)):
                try:
                    if abs(list_x[k] - list_x[j]) <= 10.5 and abs(list_y[k] - list_y[j]) <= 10.5: # 10.5 is approximately the apothem of the hexagon for the plot parameters we use
                        f.write(f"Overlap at coordinates ({list_x[j], list_y[j]}),({list_x[k], list_y[k]}) - summed energies {list_e[j]} and {list_e[k]} \n")
                        # Adding energies at the location of overlap
                        list_e[j] += list_e[k]
                        # Removing one coordinate of the overlap, these are these points. We cannot remove them in the loop, so we set them to a value that will not affect the loop
                        list_x[k] = np.nan
                        list_y[k] = np.nan
                        list_e[k] = np.nan
                except: # Case when subtracting a number and np.nan
                    continue
        
        # Removing overlapped values, i.e., removing np.nan elements from the list 
        list_x = list_x[~np.isnan(list_x)]
        list_y = list_y[~np.isnan(list_y)]
        list_e = list_e[~np.isnan(list_e)]
        f.close()
        
        # Deleting empty files - layers where there was no overlap
        if os.path.getsize(f"Overlaps/overlaps_layer_{i}.txt") == 0:
            os.remove(f"Overlaps/overlaps_layer_{i}.txt")
        x, y = find_coord(eta, phi, z)
        plot_hexagon(list_x, list_y, list_e, i)
        
        z += 0.42 #increse of z distance beetween layers

x, y = find_coord(eta, phi, z_0)
plot_hexagon(sum_list_x, sum_list_y, sum_list_e, "sum of all")  
  