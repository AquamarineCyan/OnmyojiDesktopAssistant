#!/usr/bin/env python3
# log.py
"""
日志保存
"""
import os
import time

# 获取当前目录的父目录
fpath = os.getcwd()

def logInit():
    print("目录为: %s" % os.listdir(fpath))
    if 'log' not in os.listdir(fpath):
        try:
            os.mkdir(fr'{fpath}\log')
            print('log succend')
            return True
        except:
            print('log failed')
            return False
    else:
        print('log already has')
        return True


def logWrite(text):
    # 获取当前系统时间
    t = time.localtime()
    timenow = time.strftime("%Y-%m-%d %H:%M:%S", t)
    timenowday = time.strftime("%Y%m%d", t)
    print(timenow)
    # 生成日志
    f = open(fr'{fpath}\log\log-{timenowday}.txt', mode='a', encoding='utf-8')
    f.write(f'{timenow} {text}\n')
    f.close()
