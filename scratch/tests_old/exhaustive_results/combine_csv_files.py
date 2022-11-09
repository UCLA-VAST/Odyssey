import os
import sys
import pandas as pd

dir_path = './mm/'
csv_files = os.listdir(dir_path)
# combine csv files into one csv file
combined_csv = pd.concat([pd.read_csv(dir_path + f) for f in csv_files ])
# sort results by cycles
combined_csv = combined_csv.sort_values(by=['cycles'])
# export to csv
combined_csv.to_csv( "combined_csv.csv", index=False, encoding='utf-8-sig')
