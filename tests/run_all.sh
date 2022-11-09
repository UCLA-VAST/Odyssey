dims=(64 128 256 512 1024)
designs=(0 1 2 3 4 5)
# search_method_2.py
for i in "${dims[@]}" 
do
  for d in "${designs[@]}" 
  do
    python search_method_2.py   -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=10 -d=$d -t=5 -obj='latency'
  done
done

# odyssey
for i in "${dims[@]}" 
do
  python odyssey.py           mm "{'i': $i, 'j': $i, 'k': $i}"
done

# search_method_2.py
dims=(64 128 256 512 1024)
designs=(0 1 2 3 4 5 6 7 8 9)
for i in "${dims[@]}" 
do
  for d in "${designs[@]}" 
  do
    python search_method_2.py   -w="conv" -p="{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}" -n=10 -d=$d -t=5 -obj='latency'
  done
done

# odyssey
for i in "${dims[@]}" 
do
  python odyssey.py           conv "{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}"
done


dims=(64 128 256 512 1024)
designs=(0 1 2 3 4 5)
for i in "${dims[@]}" 
do
  for d in "${designs[@]}" 
  do
    python search_method_2.py   -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=10 -d=$d -t=10 -obj='latency'
  done
done

dims=(64 128 256 512 1024)
designs=(0 1 2 3 4 5 6 7 8 9)
for i in "${dims[@]}" 
do
  for d in "${designs[@]}" 
  do
    python search_method_2.py   -w="conv" -p="{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}" -n=10 -d=$d -t=10 -obj='latency'
  done
done

dims=(64 128 256 512 1024)
designs=(0 1 2 3 4 5)
for i in "${dims[@]}" 
do
  for d in "${designs[@]}" 
  do
    python search_method_2.py   -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=100 -d=$d -t=5 -obj='latency'
  done
done

dims=(64 128 256 512 1024)
designs=(0 1 2 3 4 5 6 7 8 9)
for i in "${dims[@]}" 
do
  for d in "${designs[@]}" 
  do
    python search_method_2.py   -w="conv" -p="{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}" -n=100 -d=$d -t=5 -obj='latency'
  done
done

dims=(64 128 256 512 1024)
designs=(0 1 2 3 4 5)
for i in "${dims[@]}" 
do
  for d in "${designs[@]}" 
  do
    python search_method_2.py   -w="mm" -p="{'i': $i, 'j': $i, 'k': $i}" -n=100 -d=$d -t=10 -obj='latency'
  done
done

dims=(64 128 256 512 1024)
designs=(0 1 2 3 4 5 6 7 8 9)
for i in "${dims[@]}" 
do
  for d in "${designs[@]}" 
  do
    python search_method_2.py   -w="conv" -p="{'i': $i, 'o' : $i, 'r' : $i, 'c' : $i, 'p' : 3, 'q' : 3}" -n=100 -d=$d -t=10 -obj='latency'
  done
done