import os
import sys

folders_only = [f for f in os.listdir('.') if os.path.isdir(f)]

# sort folders
folders_only.sort()
#reverse sort
folders_only.reverse()
for folder in folders_only:
  if folder != 'design_2_mem_0':
    cmd = f'cd {folder}; make syn &> ../../mod_logs/{folder}_syn.log; cd ..'
    print('Running: ', cmd)
    os.system(cmd)
