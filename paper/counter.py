
all_refs = {}
with open('refs.txt', 'r') as f:
  for line in f:
    if '@' in line:
      tokens = line.split('{')
      ref = tokens[1].strip(',\n')
      # print(ref)
      all_refs[ref] = 0

# remove duplicates
# all_refs = list(set(all_refs))

with open('main.txt', 'r') as f:
  for line in f:
    if '%' not in line:
      for ref in all_refs.keys():
        if ref in line:
          all_refs[ref] += 1

# sort by value
all_refs = sorted(all_refs.items(), key=lambda x: x[1], reverse=True)
# if value is 0, remove it
all_refs = [ref for ref in all_refs if ref[1] != 0]
for ref in all_refs:
  print(ref)
exit()
with open('main.txt', 'r') as f:
  for line in f:
    if '%' not in line:
      for ref in all_refs:
        if ref[0] in line:
          if ref[1] <= 1:
            # print 50 characters before and after the ref
            start = line.find(ref[0]) - 50
            end = line.find(ref[0]) + 50
            print(ref, line[start:end])