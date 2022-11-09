# python search_method_2.py   -w="conv" -p="{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}" -n=10 -d=0 -t=10 -obj='latency'
# python exhaustive_search.py -w="conv" -p="{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}" -n=10 -d=0
dims=(64 128 256 512 1024)
designs=(0 1 2 3 4 5 6 7 8 9)
for i in "${dims[@]}" 
do
  for d in "${designs[@]}" 
  do
    python search_method_2.py   -w="conv" -p="{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}" -n=10 -d=$d -t=10 -obj='latency'
    python exhaustive_search.py -w="conv" -p="{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}" -n=10 -d=$d
  done
done

