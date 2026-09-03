from enum import StrEnum

import yaml
from pydantic import BaseModel, field_validator

from .application import APP_PATH, RESOURCE_DIR_PATH, RESOURCE_JA_DIR_PATH, USER_DATA_DIR_PATH
from .log import logger
from .log_color import DEFAULT_LOG_COLORS, LogColorLevel, normalize_color


class GameLanguage(StrEnum):
    """游戏语言"""

    CN = "国服"
    JA = "日服"


class UpdateDownload(StrEnum):
    """下载线路"""

    MIRROR = "镜像站"
    GITHUB = "GitHub"


class XuanShangFengYin(StrEnum):
    """悬赏封印处理方式"""

    ACCEPT = "接受"
    REJECT = "拒绝"
    IGNORE = "忽略"
    CLOSE = "关闭"


class ScreenshotMethod(StrEnum):
    """截图方法"""

    BITBLT = "BitBlt"
    PRINTWINDOW = "PrintWindow"


class InteractionMode(StrEnum):
    """交互模式"""

    FRONTEND = "前台"
    BACKEND = "后台"


_game_language_list = [GameLanguage.CN, GameLanguage.JA]
"""游戏语言"""
_update_download_list = [UpdateDownload.MIRROR, UpdateDownload.GITHUB]
"""下载线路"""
_xuanshangfengyin_list = [
    XuanShangFengYin.ACCEPT,
    XuanShangFengYin.REJECT,
    XuanShangFengYin.IGNORE,
    XuanShangFengYin.CLOSE,
]
"""悬赏封印"""
_shortcut_start_stop_list = [
    "无",
    "F1",
    "F2",
    "F3",
    "F4",
    "F5",
    "F6",
    "F7",
    "F8",
    "F9",
    "F10",
    "F11",
    "F12",
]
"""快捷键-开始/停止"""
_interaction_mode_list = [InteractionMode.FRONTEND, InteractionMode.BACKEND]
"""交互模式"""
# 前台/后台的子配置
_frontend_sub_config = {
    "force_window": [True, False],
}
_backend_sub_config = {
    "prevent_sleep": [True, False],
    "screenshot_method": [ScreenshotMethod.BITBLT, ScreenshotMethod.PRINTWINDOW],
}


class FrontendConfig(BaseModel):
    """前台配置"""

    force_window: bool = True


class BackendConfig(BaseModel):
    """后台配置"""

    prevent_sleep: bool = True
    screenshot_method: str = "BitBlt"


class InteractionModeConfig(BaseModel):
    """交互模式配置"""

    mode: str = InteractionMode.FRONTEND
    frontend: FrontendConfig = FrontendConfig()
    backend: BackendConfig = BackendConfig()


class LogColorConfig(BaseModel):
    """日志颜色配置"""

    info: str = DEFAULT_LOG_COLORS[LogColorLevel.INFO]
    """普通信息颜色"""
    hint: str = DEFAULT_LOG_COLORS[LogColorLevel.HINT]
    """提示信息颜色"""
    warn: str = DEFAULT_LOG_COLORS[LogColorLevel.WARN]
    """警告信息颜色"""
    error: str = DEFAULT_LOG_COLORS[LogColorLevel.ERROR]
    """错误信息颜色"""

    @field_validator("info", "hint", "warn", "error")
    @classmethod
    def _normalize_color(cls, v: str, info) -> str:
        """非法颜色回退默认值，并归一化为 #RRGGBB 格式"""
        return normalize_color(v, DEFAULT_LOG_COLORS[LogColorLevel(info.field_name)])


class DefaultConfig(BaseModel):
    """默认配置，用于UI显示选项"""

    game_language: list = _game_language_list
    """游戏服务器"""
    auto_update: bool = True
    """自动更新"""
    update_download: list = _update_download_list
    """下载线路"""
    xuanshangfengyin: list = _xuanshangfengyin_list
    """悬赏封印"""
    remember_last_choice: bool = False
    """记住上次选择"""
    shortcut_start_stop: list = _shortcut_start_stop_list
    """快捷键-开始/停止"""
    win_toast: bool = True
    """是否启用系统通知"""
    interaction_mode: dict = {
        "mode": _interaction_mode_list,
        "frontend": _frontend_sub_config,
        "backend": _backend_sub_config,
    }
    """交互模式"""
    function_order: list = []
    """功能排序默认值"""
    battle_theme_recognition: bool = False
    """战斗主题识别（识别特殊胜利/失败画面）"""
    remember_force_zoom_choice: bool = False
    """记住强制缩放的选择（不再弹窗提醒）"""
    log_color: dict = LogColorConfig().model_dump()
    """日志颜色配置"""


default_config = DefaultConfig()


class UserConfig(BaseModel):
    """用户配置"""

    game_language: str = GameLanguage.CN
    """游戏服务器"""
    auto_update: bool = True
    """自动更新"""
    update_download: str = UpdateDownload.MIRROR
    """下载线路"""
    xuanshangfengyin: str = XuanShangFengYin.ACCEPT
    """悬赏封印"""
    remember_last_choice: bool = False
    """记忆上次所选功能"""
    last_function: str = ""
    """上次选择的功能名（GameFunction.name），与remember_last_choice配合使用"""
    shortcut_start_stop: str = _shortcut_start_stop_list[0]
    """快捷键-开始/停止"""
    win_toast: bool = True
    """系统通知"""
    interaction_mode: InteractionModeConfig = InteractionModeConfig()
    """交互模式"""
    function_order: list[str] = []
    """功能排序，可通过GameFunctionSelectorWidget修改"""
    battle_theme_recognition: bool = False
    """战斗主题识别（识别特殊胜利/失败画面）"""
    remember_force_zoom_choice: bool = False
    """记住强制缩放的选择（不再弹窗提醒）"""
    force_zoom_accepted: bool = True
    """记住的强制缩放选择：True=接受缩放，False=拒绝"""
    log_color: LogColorConfig = LogColorConfig()
    """日志颜色配置"""
    announcement_id: int = 19700101
    """已读公告的最新 id"""


class XuanShangFengYinState:
    """悬赏封印运行时状态"""

    def __init__(self):
        self.count: int = 0

    def add(self):
        self.count += 1

    def reset(self):
        self.count = 0

    def get(self):
        return self.count


class RuntimeState:
    """运行时状态，不序列化保存"""

    def __init__(self):
        self.xuanshangfengyin: XuanShangFengYinState = XuanShangFengYinState()


class Config:
    """配置"""

    config_path = USER_DATA_DIR_PATH / "config.yaml"

    def __init__(self):
        self.user: UserConfig = UserConfig()
        self.is_first_run: bool = False  # 是否首次运行
        self.data_error: int = 0
        self.resource_dir = RESOURCE_DIR_PATH
        self.runtime = RuntimeState()
        self._is_gpu: bool = self._detect_gpu_mode()  # GPU 模式
        self._init()

    @property
    def is_gpu(self) -> bool:
        return self._is_gpu

    def _init(self):
        """初始化"""
        if self.config_path.is_file():
            logger.info("Find config file.")
            data = self._check_outdated(self._read())
            # 注意：isinstance(True, int) 为 True，需先排除 bool 类型
            # TODO v2.2：删除兼容代码
            val = data.get("remember_last_choice")
            if isinstance(val, int) and not isinstance(val, bool):
                data["remember_last_choice"] = val == 0
            self.user = UserConfig(**data)
            if self.data_error:
                logger.warning("Data error, reset config.")
                self._save(self.user)
        else:
            logger.ui_warn("Cannot find config file.")
            self.is_first_run = True
            self._save(self.user)
            logger.ui("create file config.yaml success.")

        if self.user.game_language == GameLanguage.JA:
            self.resource_dir = RESOURCE_JA_DIR_PATH

        from .log_color import update_log_colors

        update_log_colors(
            self.user.log_color.info,
            self.user.log_color.hint,
            self.user.log_color.warn,
            self.user.log_color.error,
        )

    def _read(self) -> dict:
        with open(self.config_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _save(self, data) -> bool:
        if isinstance(data, UserConfig):
            data = data.model_dump(mode="json")
        if isinstance(data, dict):
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, indent=4, allow_unicode=True, sort_keys=False)
        else:
            logger.ui_error("file config.yaml save failed.")
            return False
        return True

    @staticmethod
    def _detect_gpu_mode() -> bool:
        """检查是否为 GPU 版本。

        GPU 版本打包后会包含 lib/nvidia 目录，通过检查该目录是否存在来判断。
        """
        return (APP_PATH / "lib" / "nvidia").is_dir()

    def show_log(self):
        logger.info(
            f"配置更新完成\n{yaml.dump(self.user.model_dump(mode='json'), allow_unicode=True, sort_keys=False)}"
        )

    def update(self, key: str, value: str):
        """设置项更新

        参数:
            key (str): 设置项，可以是一级("xuanshangfengyin")或二级("notifications.sound")或三级("interaction_mode.frontend.force_window")
            value (str): 属性

        示例：
        ``` python
            config.update("interaction_mode.mode", "后台")
            config.update("interaction_mode.frontend.force_window", False)
            config.update("interaction_mode.backend.prevent_sleep", False)
        ```
        """
        logger.info(f"配置项 [{key}] 更新为 [{value}]")
        config_dict = self.user.model_dump(mode="json")

        keys = key.split(".")
        target = config_dict
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = value

        self.user = UserConfig.model_validate(config_dict)
        self._save(self.user)

        if key.startswith("log_color."):
            from .log_color import update_log_colors

            update_log_colors(
                self.user.log_color.info,
                self.user.log_color.hint,
                self.user.log_color.warn,
                self.user.log_color.error,
            )

    def _check_outdated(self, data: dict) -> dict:
        """仅检查不符合配置项的部分，不存在的设置项可以通过UserConfig的model_dump()方法获取默认值"""

        def validate(value, default_value):
            # 如果 default 是列表，表示候选值
            if isinstance(default_value, list):
                if value not in default_value:
                    return default_value[0], True
                return value, False
            # 如果 default 是字典，递归检查
            elif isinstance(default_value, dict):
                fixed = {}
                changed = False
                for k, v in default_value.items():
                    sub_val, sub_changed = validate(value.get(k), v) if isinstance(value, dict) else (v, True)
                    fixed[k] = sub_val
                    if sub_changed:
                        changed = True
                return fixed, changed
            # 其他类型，直接返回
            return value, False

        for key, default_value in default_config.model_dump().items():
            if key not in data:
                continue
            # function_order 是列表类型，不走候选值校验逻辑
            if key == "function_order":
                continue
            fixed_value, changed = validate(data[key], default_value)
            if changed:
                data[key] = fixed_value
                self.data_error += 1
        return data


config = Config()
