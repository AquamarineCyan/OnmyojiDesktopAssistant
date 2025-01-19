class GlobalParameter:
    """全局参数"""

    count: int = 0

    def add(self):
        self.count += 1

    def reset(self):
        self.count = 0

    def get(self):
        return self.count


xuanshangfengyin_count = GlobalParameter()
"""悬赏封印数量"""
