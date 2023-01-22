i=1024
p=2
d=3
a=1
python odyssey.py             -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -d="($p, $d)" -obj='latency' -a=$a --trials=1 -to=20 
i=1024
p=1
d=5
a=1
python odyssey.py             -w="conv" -p="{'i': $i, 'o': $i, 'r': $i, 'c': $i, 'p':3, 'q':3}" -d="($p, $d)" -obj='latency' -a=$a --trials=1 -to=20 
