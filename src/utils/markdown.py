"""Markdown 文本处理工具"""

import re

# 匹配裸 URL（排除已处于 markdown 链接或尖括号内的 URL）
_BARE_URL_PATTERN = re.compile(r'(?<![\(\<\["`])(https?://[^\s<>]+)')


def autolink_urls(text: str) -> str:
    """将裸 URL 转换为 Markdown 超链接，与 GitHub 的自动链接行为保持一致"""
    return _BARE_URL_PATTERN.sub(lambda m: f"[{m.group(0)}]({m.group(0)})", text)


def downgrade_headings(text: str) -> str:
    """
    将Markdown文本中的所有标题降一级（如# 标题 → ## 标题）
    最多处理到六级标题，超过六级保持不变
    """
    lines = text.split("\n")
    processed_lines = []
    for line in lines:
        stripped = line.lstrip("#")
        # 计算原标题级别
        level = len(line) - len(stripped)

        if level > 0 and stripped.startswith(" "):
            # 降级处理（但不超过6级）
            new_level = min(level + 1, 6)
            processed_lines.append("#" * new_level + stripped)
        else:
            processed_lines.append(line)
    return "\n".join(processed_lines)
