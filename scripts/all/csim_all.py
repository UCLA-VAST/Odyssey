import os
import sys

folders_only = [f for f in os.listdir('.') if os.path.isdir(f)]

# sort folders
folders_only.sort()

for folder in folders_only:
  if folder != 'logs': 
    cmd = f'screen -S {folder} -dm bash -c  "cd {folder}; make csim_all &> ../logs/{folder}.log; cd .."'
    print('Running: ', cmd)
    os.system(cmd)
