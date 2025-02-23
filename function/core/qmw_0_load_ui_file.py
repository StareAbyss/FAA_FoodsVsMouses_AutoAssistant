import os
import sys

from PyQt6 import uic, QtGui, QtCore, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QListWidgetItem, QListWidget, QSystemTrayIcon, QMenu

from function.common.get_system_dpi import get_system_dpi
from function.globals import EXTRA
from function.globals.get_paths import PATHS
from function.globals.thread_action_queue import T_ACTION_QUEUE_TIMER
# noinspection PyUnresolvedReferences
from function.qrc import test_rc, theme_rc, GTRONICK_rc
# 虽然ide显示上面这行没用，但实际是用来加载相关资源的，不可删除,我用奇妙的方式强制加载了
from function.widget.CusIcon import create_qt_icon
from function.widget.SearchableComboBox import SearchableComboBox



ZOOM_RATE = None


class QMainWindowLoadUI(QtWidgets.QMainWindow):
    """读取.ui文件创建类 并加上一些常用方法"""

    # 注意：
    # 若ui界面文件是个对话框，那么MyApp就必须继承 QDialog
    # 若ui界面文件是个MainWindow，那么MyApp就必须继承 QMainWindow
    def __init__(self):
        # 继承父方法
        super().__init__()

        # 加载 ui文件
        uic.loadUi(PATHS["root"] + '\\resource\\ui\\FAA_3.0.ui', self)

        # 设置窗口名称
        self.setWindowTitle("FAA - 本软件免费且开源")

        # 设置系统图标
        self.setWindowIcon(QIcon(PATHS["logo"] + "\\圆角-FetDeathWing-256x-AllSize.ico"))

        # 设置显示版本号
        self.Title_Version.setText(EXTRA.VERSION)

        # 获取 dpi & zoom 仅能在类中调用
        self.zoom_rate = get_system_dpi() / 96
        T_ACTION_QUEUE_TIMER.set_zoom_rate(self.zoom_rate)

        # 获取系统样式(日夜)
        self.theme = self.get_theme()

        # 获取系统样式(高亮颜色)
        self.theme_highlight_color = QtWidgets.QApplication.palette().color(QtGui.QPalette.ColorRole.Highlight).name()

        # 配置 进阶设置 导航栏交互
        self.adv_opt_synchronizing = None
        self.adv_opt_sections:list = []
        self.init_advanced_settings_connection()

        # 添加系统托盘功能
        self.tray_icon = None
        self.init_tray_icon()

        # 绑定最小化按钮
        self.Button_Minimized.clicked.connect(self.minimize_to_tray)

    def get_theme(self):
        if self.palette().color(QtGui.QPalette.ColorRole.Window).lightness() < 128:
            theme = "dark"
        else:
            theme = "light"
        return theme

    """任何ui都要设置的样式表"""

    def set_theme_common(self):
        """
        在应用皮肤样式表之前设定
        """
        # 进行特殊的无边框和阴影处理
        self.set_no_border()

        # 设置logo阴影
        self.set_logo_shadow()

        # 根据系统样式,设定开关图标
        self.set_exit_and_minimized_btn_icon()

        # 根据系统样式, 设置自定义控件的样式
        self.set_customize_widget_style()

        # 部分图片元素的加载
        self.set_image_resource()

    def set_common_theme(self):
        """
        在应用皮肤样式表之后设定
        :return:
        """

        style_sheet = self.styleSheet()

        # 增加边框
        style_sheet += "#MainFrame{border-radius: 8px; border: 1px solid #3c3d3e;} "

        style_sheet = self.styleSheet()

        # 获取当前样式表 然后在此基础上增加背景色, 根据白天黑夜主题为不同颜色
        match self.theme:
            case "dark":
                style_sheet += "#MainFrame{background-color: #1e1e1e;}"
            case "light":
                style_sheet += "#MainFrame{background-color: #FFFFFF;}"

        self.setStyleSheet(style_sheet)

    def set_logo_shadow(self):
        effect_shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        effect_shadow.setOffset(0, 0)  # 偏移
        effect_shadow.setBlurRadius(6)  # 阴影半径
        effect_shadow.setColor(QtCore.Qt.GlobalColor.gray)  # 阴影颜色
        self.Title_Logo.setGraphicsEffect(effect_shadow)  # 将设置套用到widget窗口中

    def set_no_border(self):
        # 设置无边框窗口
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)

        # 设背景为透明
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_exit_and_minimized_btn_icon(self):
        """
        设置退出按钮和最小化按钮样式，需已获取主题
        :return:
        """
        # 根据系统样式,设定开关图标
        q_color = QtGui.QColor(240, 240, 240) if self.theme == "dark" else QtGui.QColor(15, 15, 15)
        self.Button_Exit.setIcon(create_qt_icon(q_color=q_color, mode="x"))
        self.Button_Minimized.setIcon(create_qt_icon(q_color=q_color, mode="-"))

    def set_customize_widget_style(self):
        # 查找所有 SearchableComboBox 实例
        searchable_comboboxes = self.findChildren(SearchableComboBox)

        # 给他们全都改一改
        for combobox in searchable_comboboxes:
            combobox.set_style(theme=self.theme)

    def set_image_resource(self):

        # title - logo
        cus_path = PATHS["root"] + "\\resource\\logo\\圆角-FetDeathWing-450x.png"
        cus_path = cus_path.replace("\\", "/")  # pyqt 使用正斜杠

        pixmap = QtGui.QPixmap(cus_path).scaled(
            40,
            40,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        )
        self.Title_Logo.setPixmap(pixmap)
        self.Title_Logo.setFixedSize(40, 40)
        self.Title_Logo.setScaledContents(True)  # 确保图片自适应控件大小

        # 背景图
        cus_path = PATHS["root"] + "\\resource\\ui\\firefly.png"
        cus_path = cus_path.replace("\\", "/")  # pyqt 使用正斜杠
        style_sheet = f"""
            #SkinWidget{{
            background-image: url({cus_path});
            background-repeat: no-repeat;
            background-position: center;
            background-size: contain;  
            border: none;  
            }}
        """

        self.SkinWidget.setStyleSheet(style_sheet)

    """仅默认ui需要设置的样式表"""

    def set_theme_default(self):

        # 初始化样式表
        self.MainFrame.setStyleSheet("")

        # 设置箭头特殊样式
        self.set_arrow_btn_icon()

        # 设置tab栏特殊样式
        self.set_tab_bar_style()

    def set_main_window_shadow(self):
        # 添加阴影
        effect_shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        effect_shadow.setOffset(0, 0)  # 偏移
        effect_shadow.setBlurRadius(8)  # 阴影半径
        effect_shadow.setColor(QtCore.Qt.GlobalColor.black)  # 阴影颜色
        self.MainFrame.setGraphicsEffect(effect_shadow)  # 将设置套用到widget窗口中

    def set_tab_bar_style(self):

        style_sheet = self.MainFrame.styleSheet()
        selected_text_color = "#FFFFFF" if self.theme == "dark" else "#000000"

        style_sheet += f"""
            QTabBar::tab {{
                min-width: 136px;  /* 最小宽度 */
                height: 20px;
                border-style: solid;
                border-top-color: transparent;
                border-right-color: transparent;
                border-left-color: transparent;
                border-bottom-color: transparent;
                border-bottom-width: 1px;
                border-style: solid;
                color: #808086;
                padding: 3px;
                margin-left:3px;
            }}
            QTabBar::tab:selected, QTabBar::tab:last:selected, QTabBar::tab:hover {{
                border-style: solid;
                border-top-color: transparent;
                border-right-color: transparent;
                border-left-color: transparent;
                border-bottom-color: {self.theme_highlight_color};
                border-bottom-width: 2px;
                border-style: solid;
                color: {selected_text_color};
                padding-left: 3px;
                padding-bottom: 2px;
                margin-left:3px;
            }}
            QTabWidget::tab-bar {{
                alignment: center;
            }}
            QTabWidget::pane{{
                border:none;
            }}
            """

        self.MainFrame.setStyleSheet(style_sheet)

    def set_arrow_btn_icon(self):

        # 设置图标
        color = QtGui.QColor(240, 240, 240) if self.theme == "dark" else QtGui.QColor(15, 15, 15)
        prev_icon = create_qt_icon(q_color=color, mode="<-")
        next_icon = create_qt_icon(q_color=color, mode="->")

        # 找到前后月份按钮
        prev_month_button = self.DateSelector.findChild(QtWidgets.QToolButton, "qt_calendar_prevmonth")
        next_month_button = self.DateSelector.findChild(QtWidgets.QToolButton, "qt_calendar_nextmonth")

        prev_month_button.setIcon(prev_icon)
        next_month_button.setIcon(next_icon)

    """重写拖动窗口"""
    def init_tray_icon(self):
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(PATHS["logo"] + "\\圆角-FetDeathWing-256x-AllSize.ico"))
        self.tray_icon.setToolTip("FAA - 正在后台运行")

        # 创建托盘菜单
        tray_menu = QMenu()
        restore_action = tray_menu.addAction("一键启动")
        quit_action = tray_menu.addAction("退出程序")

        # 连接菜单动作
        restore_action.triggered.connect(self.todo_click_btn)
        quit_action.triggered.connect(self.close)

        # 设置托盘菜单
        self.tray_icon.setContextMenu(tray_menu)

        # 双击托盘图标恢复
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def minimize_to_tray(self):
        # 隐藏主窗口
        self.hide()
        self.tray_icon.showMessage(
            "FAA 已最小化",
            "程序正在后台运行",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def restore_from_tray(self):
        # 恢复窗口显示
        self.show()
        self.setWindowState(Qt.WindowState.WindowActive)

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.restore_from_tray()

    def closeEvent(self, event):
        """
        对MainWindow的函数closeEvent进行重构, 退出软件时弹窗提醒 并且结束所有进程(和内部的线程)
        """
        self.tray_icon.hide()
        event.accept()
        # 用过sys.exit(0)和sys.exit(app.exec())，但没起效果
        os._exit(0)

    # 切换最大化与正常大小
    def maxOrNormal(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    # 弹出警告提示窗口确认是否要关闭
    def queryExit(self):
        QtCore.QCoreApplication.instance().exit()

    _startPos = None
    _endPos = None
    _isTracking = None

    # 鼠标移动事件
    def mouseMoveEvent(self, a0: QtGui.QMouseEvent):
        if self._startPos:
            self._endPos = a0.pos() - self._startPos
            # 移动窗口
            self.move(self.pos() + self._endPos)

    # 鼠标按下事件
    def mousePressEvent(self, a0: QtGui.QMouseEvent):
        # 根据鼠标按下时的位置判断是否在QFrame范围内
        if self.childAt(a0.pos().x(), a0.pos().y()).objectName() == "FrameTitle":
            # 判断鼠标按下的是左键
            if a0.button() == QtCore.Qt.MouseButton.LeftButton:
                self._isTracking = True
                # 记录初始位置
                self._startPos = QtCore.QPoint(a0.pos().x(), a0.pos().y())

    # 鼠标松开事件
    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent):
        if a0.button() == QtCore.Qt.MouseButton.LeftButton:
            self._isTracking = False
            self._startPos = None
            self._endPos = None

    """进阶设定 导航栏交互 初始化"""

    def init_advanced_settings_connection(self):

        # 初始化同步标志
        self.adv_opt_synchronizing = False

        # 获取实际内容布局
        content_layout = self.AdvancedSettingsArea.widget().layout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)

        # 列表内容 -> 对应的元素
        self.adv_opt_sections = {
            "日常任务": self.DailyTasksSettingsGroup,
            "外部控制": self.ControlSettingsGroup,
            "战斗设置": self.BattleSettingsGroup,
            "其它设置": self.OtherSettingsGroup
        }

        # 添加导航项和内容块
        for title, tar_item in self.adv_opt_sections.items():
            # 添加导航项
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, tar_item)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.AdvancedSettingsNavigationList.addItem(item)

        # 设置样式
        self.AdvancedSettingsNavigationList.setStyleSheet("""
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #ddd;
            }
            QListWidget::item:selected {
                background-color: #e0f0ff;
                color: #0066cc;
                font-weight: bold;
            }
        """)

        # 连接信号
        self.AdvancedSettingsNavigationList.itemClicked.connect(self.on_nav_item_clicked)
        self.AdvancedSettingsArea.verticalScrollBar().valueChanged.connect(self.on_settings_scroll)

    def on_nav_item_clicked(self, item):

        if self.adv_opt_synchronizing:
            return

        # 获取关联的组件 (一个布局)
        section = item.data(Qt.ItemDataRole.UserRole)

        # 计算滚动位置（滚动到区块中间）
        scroll_bar = self.AdvancedSettingsArea.verticalScrollBar()
        widget_position = section.y()
        viewport_height = self.AdvancedSettingsArea.viewport().height()
        widget_height = section.size().height()

        # 计算目标滚动位置
        target_y = widget_position + (widget_height - viewport_height) // 2
        scroll_bar.setValue(target_y)

    def on_settings_scroll(self):

        if self.adv_opt_synchronizing:
            return

        # 获取当前滚动信息
        scroll_bar = self.AdvancedSettingsArea.verticalScrollBar()
        current_position = scroll_bar.value()
        viewport_height = self.AdvancedSettingsArea.viewport().height()
        middle_position = current_position + viewport_height // 2

        # 查找最接近的区块
        closest_item = None
        min_distance = float('inf')

        for i in range(self.AdvancedSettingsNavigationList.count()):
            item = self.AdvancedSettingsNavigationList.item(i)
            section = item.data(Qt.ItemDataRole.UserRole)

            # 计算区块中间位置
            section_top = section.y()
            section_height = section.size().height()
            section_middle = section_top + section_height // 2

            # 计算距离差值
            distance = abs(section_middle - middle_position)
            if distance < min_distance:
                min_distance = distance
                closest_item = item

        # 更新导航选中状态
        if closest_item:
            self.adv_opt_synchronizing = True
            self.AdvancedSettingsNavigationList.setCurrentItem(closest_item)
            self.AdvancedSettingsNavigationList.scrollToItem(
                closest_item,
                QListWidget.ScrollHint.PositionAtCenter
            )
            self.adv_opt_synchronizing = False


if __name__ == "__main__":
    def main():
        # 实例化 PyQt后台管理
        app = QtWidgets.QApplication(sys.argv)

        # 实例化 主窗口
        my_main_window = QMainWindowLoadUI()

        my_main_window.show()

        # 运行主循环，必须调用此函数才可以开始事件处理
        app.exec()

        sys.exit()


    main()
