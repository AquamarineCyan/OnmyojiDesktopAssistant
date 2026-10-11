from pathlib import Path

import winshell

from .application import APP_EXE_NAME, APP_NAME, APP_PATH
from .log import logger


def create_desktop_shortcut() -> bool:
    """创建桌面快捷方式，且仅指向发布目录下的 exe

    返回:
        bool: 创建成功返回 True，失败或跳过返回 False
    """

    def get_desktop_path() -> Path | None:
        """获取实际桌面路径

        返回桌面路径 (`Path`) 或在获取失败时返回 `None`。
        """
        try:
            p = Path(winshell.desktop())
            if p.exists():
                return p
        except Exception:
            return None

    try:
        desktop = get_desktop_path()
        if desktop is None:
            logger.ui_warn("无法获取桌面实际路径，已跳过创建快捷方式")
            return False

        link_path = desktop / f"{APP_NAME}.lnk"

        exe_candidate = Path(APP_PATH) / APP_EXE_NAME
        if not exe_candidate.exists():
            logger.ui_warn(f"发布目录中未找到可执行文件：{exe_candidate}，跳过创建快捷方式")
            return False

        try:
            with winshell.shortcut(str(link_path)) as sh:
                sh.path = str(exe_candidate)
                sh.working_directory = str(exe_candidate.parent)
                try:
                    sh.icon_location = str(exe_candidate)
                except Exception:
                    pass  # 图标设置失败可以降级，不影响快捷方式本身
                sh.description = f"{APP_NAME} 桌面快捷方式"
                sh.write()
        except Exception as e:
            # 写入失败（桌面被占用、权限不足、.lnk 被安全软件锁定）必须如实上报：
            # 原先这里是 pass，之后仍然打印「已创建」并 return True，
            # 用户会以为快捷方式已就绪（甚至指向旧版本 exe）
            logger.ui_warn("创建桌面快捷方式失败")
            logger.exception(e)
            return False

        logger.ui(f"桌面快捷方式已创建：{link_path}")
        return True
    except Exception:
        logger.exception("创建桌面快捷方式失败")
        return False
