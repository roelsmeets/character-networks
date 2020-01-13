# #!/usr/bin/env python
# # -*- coding: utf-8 -*-

import csv
import pandas as pd
import glob

path = r'/Users/roelsmeets/Desktop/Libris_networks/character-networks/character-networks/permutations' 
all_files = glob.glob(path + "/*.txt")

file_list = []

for filename in all_files:
    df = pd.read_csv(filename, header=None)
    file_list.append(df)

frame = pd.concat(file_list)
frame.columns = ['gender_assortativity', 'age_assortativity', 'education_assortativity', 'descent_assortativity']

print (frame.mean())




