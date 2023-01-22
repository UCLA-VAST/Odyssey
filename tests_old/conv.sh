# dims=(64 128 256 512 1024)
# designs=(0 1 2 3 4 5 6 7 8 9)
# for i in "${dims[@]}" 
# do
#   for d in "${designs[@]}" 
#   do
#     python search_method_2.py   -w="conv" -p="{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}" -n=100 -d=$d -t=10 -obj='latency'
#   done
# done
dims=(64)
designs=(7)
alphas=(0)
for i in "${dims[@]}"
do
  for d in "${designs[@]}"
  do
    for a in "${alphas[@]}"
    do
      # python divisors.py            -w="conv" -p="{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}" -d=$d -obj='latency_off_chip' -a=$a -n=10
      # python non_divisors.py        -w="conv" -p="{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}" -d="(2,$d)" -obj='latency_off_chip' -a=$a -n=10       -thr=0.02
      # python odyssey.py             -w="conv" -p="{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}" -d=$d -obj='latency_off_chip' -a=$a --trials=10 -to=20 
      python exhaustive_search.py   -w="conv" -p="{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}" -d="(2,$d)" -obj='latency_off_chip' -a=$a -n=1000 
    done
  done
done


# python search_method_2.py   -w="conv" -p="{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}" -n=10 -d=$d -t=10 -obj='latency'
# python search_method_2.py   -w="conv" -p="{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}" -n=10 -d=$d -a=0 -obj='latency_off_chip' -t=5
# python odyssey.py  conv "{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}"

# python search_method_2.py   -w="conv" -p="{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}" -n=100 -d=$d -t=10 -obj='latency'
# python exhaustive_search.py -w="conv" -p="{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}" -n=100 -d=$d

