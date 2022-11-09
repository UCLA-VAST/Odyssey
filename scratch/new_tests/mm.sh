# dims = [64, 128, 256, 512, 1024]
# make an array of dims
# dims=(64 128 256 512 1024)
# designs=(0 1 2 3 4 5)
# for i in "${dims[@]}" 
# do
#   for d in "${designs[@]}" 
#   do
#     python search_method_2.py   -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=10 -d=$d -t=10 -obj='latency'
#     python exhaustive_search.py -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=10 -d=$d
#   done
# done
i=64
python exhaustive_search_optimized.py   -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=10 -d=3
# python pruned_exhaustive_search.py    -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=10 -d=3
# python exhaustive_search.py           -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=10 -d=3

# python exhaustive_search_pruned.py    -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=10 -d=3 -t=10 -obj='latency'
# python exhaustive_search_.py          -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=10 -d=3 -t=10 -obj='latency'

# python exhaustive_search.py -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=10 -d=3



