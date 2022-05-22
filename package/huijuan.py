#!usr/bin/env python3
# huijuan.py
"""
绘卷查分
"""


def run_huijuan():
    sum: int
    print('请及时提交绘卷')
    a = int(input("大绘卷数量："))
    b = int(input("中绘卷数量："))
    c = int(input("小绘卷数量："))
    sum = a * 100 + b * 20 + c * 10
    print(f'绘卷总分：{sum}')
