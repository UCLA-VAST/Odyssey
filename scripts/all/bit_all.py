import os
import sys

folders_only = [f for f in os.listdir('.') if os.path.isdir(f)]

# sort folders
folders_only.sort()

for folder in folders_only:
  cmd = f'screen -S {folder} -dm bash -c  "cd {folder}; source env.sh; make hw_all &> xclbin.log; cd .."'
  print('Running: ', cmd)
  os.system(cmd)
