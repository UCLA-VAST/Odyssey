import os
import sys
import re
import pandas as pd

prj_path = os.environ['PRJ_PATH']
folders_only = [f for f in os.listdir('.') if os.path.isdir(f)]
# sort folders
folders_only.sort()
# hls::stream<(.+)> (.+);
expr = re.compile(r'hls::stream<(.+)> (.+);')
for folder in folders_only:
  if folder != 'logs': 
    src_file = f'{folder}/src/kernel_kernel.cpp'
    # if file exists
    if os.path.isfile(src_file):
      # replace using regex
      with open(src_file, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
          # if expr in line:
          if match := expr.search(line):
            # print(match.group(1))
            # print(match.group(2))
            # lines[i] = f'hls::stream<{match.group(1)}>& {match.group(2)}'
            lines[i] = expr.sub(r'hls::stream<\1> \2("\2");', line)
      with open(src_file, 'w') as f:
        f.writelines(lines)
    else:
      print(f'Error: {src_file} does not exist')