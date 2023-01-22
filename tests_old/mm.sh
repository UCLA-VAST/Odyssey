dims=(128)
dataflows=(3)
permutations=(2)
alphas=(1)
for i in "${dims[@]}"
do
  for d in "${dataflows[@]}"
  do
    for p in "${permutations[@]}"
    do
      for a in "${alphas[@]}"
      do
        echo "Running $i $p $d $a"
        # python divisors.py            -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -d="($p, $d)" -obj='latency_off_chip' -a=$a -n=1
        python non_divisors.py        -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -d="($p, $d)" -obj='latency_off_chip' -a=$a -n=1       -thr=0.02
        # python odyssey.py             -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -d="($p, $d)" -obj='latency_off_chip' -a=$a --trials=1 -to=20 
        # python exhaustive_search.py   -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -d="($p, $d)" -obj='latency_off_chip' -a=$a -n=1000 
      done
    done
  done
done
# i=1024
# p=2
# d=2
# a=1
# python divisors.py            -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -d="($p, $d)" -obj='latency_off_chip' -a=$a -n=1
# python non_divisors.py        -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -d="($p, $d)" -obj='latency_off_chip' -a=$a -n=1       -thr=0.02

# i=64
# a=1
# dataflows=(0 1 2 3 4 5)
# permutations=(0 1 2)
# for d in "${dataflows[@]}"
# do
#   for p in "${permutations[@]}"
#   do
#     python divisors.py            -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -d="($p,$d)" -obj='latency_off_chip' -a=$a -n=10
#   done
# done
# python divisors.py            -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -d="(0,0)" -obj='latency_off_chip' -a=$a -n=10

