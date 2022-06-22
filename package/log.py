#!/usr/bin/env python3
# log.py
"""
日志
"""

import time
from pathlib import Path


class Log:
    def __init__(self):
        self.fpath = Path.cwd()

    def log_init(self):
        """日志初始化"""
        if self.fpath.joinpath('log') not in self.fpath.iterdir():
            try:
                Path(fr'{self.fpath}\log').mkdir()
                print('log succend')
                return True
            except:
                print('log failed')
                return False
        else:
            print('log already has')
            return True

    def log_write(self, text):
        """日志写入"""
        # 生成日志
        try:
            f = open(fr'{self.fpath}\log\log-{time.strftime("%Y%m%d")}.txt', mode='a', encoding='utf-8')
            f.write(text + '\n')
            f.close()
        except:
            print(f'FileNotFoundError {self.fpath}\log\log-{time.strftime("%Y%m%d")}.txt')

    def log_remove(self):
        """日志清理"""
        if Path('log').exists():
            for filename in Path('log').iterdir():
                print(filename)
                try:
                    Path(filename).unlink()
                    print(f'remove {filename} successfully')
                except:
                    print(f'FileNotFoundError {filename}')
            Path('log').rmdir()
