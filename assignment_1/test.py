import numpy as np
import pandas as pd

input_file_name = 'hw1_input_example.txt.txt'

f = open(input_file_name , 'r')

# \n 기준으로 짤라서 list에 저장
lines = f.readlines()

for line in lines:
    line = line.strip()
# 줄 끝의 줄 바꿈 문자를 제거한다.

print(lines)

print(type(lines))

f.close()