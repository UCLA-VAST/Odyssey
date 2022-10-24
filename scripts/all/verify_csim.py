import os
import sys

files = [f for f in os.listdir('./logs/')]

passed_all = True
failed_designs = []
failed_compilation = []
failed_empty_fifos = []
failed_leftover_fifos = []
results = []
# sort folders
files.sort()
for log in files:
  with open(f'./logs/{log}', 'r') as f:
    lines = f.readlines()
    first_error = True
    resuls = {'design': log.split('.')[0]}
    print(f'Checking {log}:')
    for line in lines:
      if 'contains leftover data' in line:
        print(f'\tError: {log} contains leftover data')
        failed_leftover_fifos.append(log)
        passed_all = False
        resuls['leftover_fifos'] = 'failed'
      if 'read while empty' in line and first_error:
        print(f'\tError: {log} read while empty')
        failed_empty_fifos.append(log)
        passed_all = False
        first_error = False
        resuls['empty_fifos'] = 'failed'
      if 'Failed with' in line:
        print(f'\tError: {log}')
        failed_designs.append(log)
        passed_all = False
        resuls['functionality'] = 'failed'
      if 'failed: compilation error(s).' in line:
        print(f'\tError: compilation {log}')
        failed_compilation.append(log)
        passed_all = False
        resuls['compilation'] = 'failed'
      if 'Passed!' in line:
        print(f'\tPassed: {log}')
        # resuls['functionality'] = 'passed'
      
    results.append(resuls)
    print()
      

print()
if passed_all:
  print('All passed')
else:
  print('Some failed:')
  for result in results:
    if 'functionality' in result or 'compilation' in result or 'empty_fifos' in result or 'leftover_fifos' in result:
      print(result)