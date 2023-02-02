import re

string = "This string contains 2 positive integers: 10 and 20, and 3 positive floats: 1.5, 2.0, and 3.14. It also contains -1 negative integer and -1.5 negative float."


negative_floats = [x for x in re.findall(r"[-]?\d*\.\d+|[-]?\d+",string)]
print(negative_floats)