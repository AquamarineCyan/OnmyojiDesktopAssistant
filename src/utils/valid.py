import math

from .mysignal import global_ms as ms
from .paddleocr import RuleOcr


def valid_handle():
    ms.main.valid_listWidget_update.emit("clear", "")
    attribute_list: list = [
        "速度",
        "暴击",
        "暴击伤害",
        "攻击",
        "攻击加成",
        "生命",
        "生命加成",
        "防御",
        "防御加成",
        "效果命中",
        "效果抵抗",
    ]
    result = RuleOcr().get_raw_result()
    _list = []

    attribute: str = None
    for item in result:
        print(item)
        if item.text in attribute_list:
            attribute = item.text
            continue

        if item.text == "+15":
            attribute = None
            continue

        if attribute is not None and item.text[0] == "+":
            _list.append((attribute, item.text))
            attribute = None

        if "2件套属性" in item.text:
            break

    return _list


def score_handle():
    valid_list = valid_handle()
    first = True

    ms.main.valid_listWidget_update.emit("clear", "")
    ms.main.valid_listWidget_update.emit("add", "属性\t数值\t有效次数\n")

    for item in valid_list:
        if first:
            first = False
            text = f"{item[0]}\t{item[1]}"
            ms.main.valid_listWidget_update.emit("add", f"{text}\n")
            continue
        attribute = item[0]
        num = item[1]

        if "+" in num:
            num = num[1:]
        if "%" in num:
            num = num[:-1]

        match attribute:
            case "速度" | "暴击" | "攻击加成" | "生命加成" | "防御加成":
                score = math.ceil(float(num) / 3) - 1
            case "暴击伤害" | "效果命中" | "效果抵抗":
                score = math.ceil(float(num) / 4) - 1
            case "攻击" | "生命" | "防御":
                score = math.ceil(float(num) / 110) - 1

        if score == 0:
            text = f"{item[0]}\t{item[1]}"
        else:
            text = f"{item[0]}\t{item[1]}\t{score}"
        ms.main.valid_listWidget_update.emit("add", f"{text}\n")
