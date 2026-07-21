VERSION: str = "2.1.2"
"""版本号"""

try:
    from .debug_version import DEBUG_VERSION  # noqa: F401
except ImportError:
    DEBUG_VERSION: str = "0"
    """调试版本号，本地发包时设置，不影响自动化打包"""
