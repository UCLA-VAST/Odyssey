# python mm_scratch.py   mm "{'i': 64, 'j' : 64, 'k' : 64}" 1
# python mm_scratch.py   mm "{'i': 128, 'j' : 128, 'k' : 128}" 1
# python mm_scratch.py   mm "{'i': 256, 'j' : 256, 'k' : 256}" 1
# python mm_scratch.py   mm "{'i': 512, 'j' : 512, 'k' : 512}" 1
# python mm_scratch.py   mm "{'i': 1024, 'j' : 1024, 'k' : 1024}" 1
# python conv_scratch.py   conv "{'i': 256, 'o': 256, 'r': 256, 'c': 256, 'p': 3, 'q': 3}" 7
# python conv_scratch.py   conv "{'i': 256, 'o': 256, 'r': 256, 'c': 256, 'p': 3, 'q': 3}" 7
python conv_scratch.py   conv "{'i': 64, 'o': 64, 'r': 64, 'c': 64, 'p': 3, 'q': 3}" 7

# python conv_scratch.py conv "{'i': 64, 'o': 64, 'r': 288, 'c': 288, 'p': 3, 'q': 3}" 1
# python conv_scratch.py conv "{'i': 256, 'o': 256, 'r': 64, 'c': 64, 'p': 3, 'q': 3}" 1
# python conv_scratch.py conv "{'i': 512, 'o': 512, 'r': 512, 'c': 512, 'p': 3, 'q': 3}"
# python conv_scratch.py conv "{'i': 1024, 'o': 1024, 'r': 1024, 'c': 1024, 'p': 3, 'q': 3}"