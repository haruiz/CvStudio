from cvstudio.gui.tabs import DatasetTabWidget
from cvstudio.gui.widgets import LateralMenu, ItemLocation
from cvstudio.pyqt import (
    QMainWindow,
    QHBoxLayout,
    QWidget,
    Qt,
    QTabWidget,
    QStatusBar,
    QtGui,
    QtCore,
    QSplitter,
    QSizePolicy,
    QDesktopWidget,
)
from cvstudio.util import GUIUtils


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("CVStudio")
        self.resize(1600, 900)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # define central widget layout
        self.central_widget_layout = QHBoxLayout(self.central_widget)
        self.central_widget_layout.setSpacing(0)
        self.central_widget_layout.setContentsMargins(0, 0, 0, 0)

        # create lateral menu
        self.lateral_menu = LateralMenu(width=80)
        self.lateral_menu.item_click.connect(self.lateral_menu_on_click_item)
        icon = GUIUtils.get_icon("data.png")
        self.lateral_menu.add_item(icon, "Datasets", name="datasets")
        icon = GUIUtils.get_icon("logout.png")
        self.lateral_menu.add_item(icon, "Exit", loc=ItemLocation.BOTTOM, name="exit")

        # tabs manager
        self.tabs_manager = QTabWidget()
        self.tabs_manager.setTabShape(QTabWidget.Rounded)
        self.tabs_manager.setDocumentMode(False)
        self.tabs_manager.setTabsClosable(True)
        self.tabs_manager.setTabBarAutoHide(False)
        self.tabs_manager.tabCloseRequested.connect(self.close_tab_event)
        self.tabs_manager.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.lateral_menu)
        splitter.addWidget(self.tabs_manager)
        self.central_widget_layout.addWidget(splitter)

        # status bar
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.set_current_tab("datasets")

        # center window
        windows_roi = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        windows_roi.moveCenter(center_point)
        self.move(windows_roi.topLeft())

    def set_current_tab(self, item_name):
        self.tabs_manager.clear()
        if item_name == "datasets":
            tab_widget = DatasetTabWidget()
            self.tabs_manager.addTab(tab_widget, "Datasets")

    def close_tab_event(self, index):
        self.tabs_manager.removeTab(index)

    def lateral_menu_on_click_item(self, item_name: str):
        self.set_current_tab(item_name)

    def close_tab_by_type(self, tab_class):
        for i in range(self.tabs_manager.count()):
            curr_tab_widget = self.tabs_manager.widget(i)
            if isinstance(curr_tab_widget, tab_class):
                self.tabs_manager.removeTab(i)
