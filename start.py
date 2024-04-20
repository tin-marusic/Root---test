import uproot
import numpy as np
import matplotlib.pyplot as plt

root = uproot.open("ntuple_doublePhotons_1k_OKAY.root")
tree = root["l1tHGCalTriggerNtuplizer/HGCalTriggerNtuple;20"]
print(tree.keys())
branches = tree.arrays()
for i in range(len(branches["ts_energy"][0])):
    print(branches["ts_x"][0][i])

for i in range(len(branches["ts_x"])):
    plt.hexbin(branches["ts_x"][i], branches["ts_y"][i], C=branches["ts_energy"][i], cmap='plasma', gridsize=35, vmax=(np.max(branches["ts_energy"][i])+np.mean((branches["ts_energy"][i])))/3, vmin=np.min(branches["ts_energy"][i]))
    plt.colorbar(label='Vrijednost energije')
    plt.xlabel("ts_x")
    plt.ylabel("ts_y")
    plt.title(f"ts_x:ts_y:ts_energy - tc_layer == {i+1}")
    plt.savefig(f"Plotovi/plot{i+1}.png")
    plt.clf()