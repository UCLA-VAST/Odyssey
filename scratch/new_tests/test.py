import multiprocessing as mp
import time

def work(args):
  x, y = args
  time.sleep(0.1 * (x + y))
  return (x, y)

with mp.Pool(processes=8) as p:
  args = ((x, y) for x in range(10) for y in range(10))
  res = p.imap_unordered(work, args)
  
  for r in res:
    print(r)


