from PySide6.QtCore import QPoint
from qfluentwidgets import InfoBar, InfoBarManager, InfoBarPosition


class BelowTitleBarInfoBarManager(InfoBarManager):
    """右上角提示条定位：父窗口有标题栏时整体下移，避免压住标题栏并保持堆叠间距"""

    top_gap = 8

    def _top_offset(self, parent) -> int:
        """父窗口标题栏占用的高度，无标题栏时不需要偏移"""
        title_bar = getattr(parent, "titleBar", None)
        return title_bar.height() + self.top_gap if title_bar is not None else 0

    def _pos(self, infoBar: InfoBar, parentSize=None) -> QPoint:
        p = infoBar.parent()
        parentSize = parentSize or p.size()

        x = parentSize.width() - infoBar.width() - self.margin
        y = max(self.margin, self._top_offset(p))
        index = self.infoBars[p].index(infoBar)
        for bar in self.infoBars[p][0:index]:
            y += bar.height() + self.spacing

        return QPoint(x, y)

    def _slideStartPos(self, infoBar: InfoBar) -> QPoint:
        return QPoint(infoBar.parent().width(), self._pos(infoBar).y())


# InfoBarManager.register 对已存在的定位不会覆盖，这里直接替换右上角定位
InfoBarManager.managers[InfoBarPosition.TOP_RIGHT] = BelowTitleBarInfoBarManager
