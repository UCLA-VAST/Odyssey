# dims=(64 128 256 512 1024)
# designs=(0 1 2 3 4 5)
# for i in "${dims[@]}" 
# do
#   for d in "${designs[@]}" 
#   do
#     python search_method_2.py   -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=100 -d=$d -t=10 -obj='latency'
#   done
# done
# i=1024
# d=3
# python search_method_2.py           -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=100 -d=$d -obj='latency_off_chip' -a=0.0 -t=5
# python search_method_2.py           -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=100 -d=$d -obj='latency_off_chip' -a=0.01 -t=5
# python search_method_2.py           -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=100 -d=$d -obj='latency_off_chip' -a=0.1 -t=5
# python search_method_2.py           -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=100 -d=$d -obj='latency_off_chip' -a=0.5 -t=5
# python search_method_2.py           -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=100 -d=$d -obj='latency_off_chip' -a=0.9 -t=5
# python search_method_2.py           -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=100 -d=$d -obj='latency_off_chip' -a=0.99 -t=5
# python search_method_2.py           -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=100 -d=$d -obj='latency_off_chip' -a=1 -t=5

# python exhaustive_search.py         -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=100 -d=$d -obj='latency_off_chip' -a=0.0
# python exhaustive_search.py         -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=100 -d=$d -obj='latency_off_chip' -a=0.01
# python exhaustive_search.py         -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=100 -d=$d -obj='latency_off_chip' -a=0.1
# python exhaustive_search.py         -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=100 -d=$d -obj='latency_off_chip' -a=0.5
# python exhaustive_search.py         -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=100 -d=$d -obj='latency_off_chip' -a=0.9
# python exhaustive_search.py         -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=100 -d=$d -obj='latency_off_chip' -a=0.99
# python exhaustive_search.py         -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=100 -d=$d -obj='latency_off_chip' -a=1
# i=1024
# d=3
# python search_method_2.py           -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=10 -d=$d -t=10 -obj='latency'
# python odyssey.py           mm "{'i': $i, 'j': $i, 'k': $i}"

# python pruned_exhaustive_search.py  -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=10 -d=$d


# i=1024
# # python odyssey.py           mm "{'i': $i, 'j': $i, 'k': $i}"
# python odyssey.py           conv "{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}"
