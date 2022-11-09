dims=(64)
designs=(0 1 2 3 4 5)
alphas=(1)
for i in "${dims[@]}"
do
  for d in "${designs[@]}"
  do
    for a in "${alphas[@]}"
    do
      python divisors.py            -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -d=$d -obj='latency_off_chip' -a=$a -n=10
      python non_divisors.py        -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -d=$d -obj='latency_off_chip' -a=$a -n=10       -thr=0.02
      # python odyssey.py             -w="conv" -p="{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}" -d=$d -obj='latency_off_chip' -a=$a --trials=10 -to=20 
      python exhaustive_search.py   -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -d=$d -obj='latency_off_chip' -a=$a -n=10 
    done
  done
done