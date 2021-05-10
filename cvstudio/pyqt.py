from enum import Enum


class QT_API(Enum):
    QT_API_PYQT5 = 1
    QT_API_PYSIDE2 = 2


QT_API_BACKEND = QT_API.QT_API_PYQT5
if QT_API_BACKEND == QT_API.QT_API_PYSIDE2:

    from PySide2 import QtCore, QtGui, QtWidgets

    from PySide2.QtCore import (
        QFile,
        QTextStream,
        QDir,
        QItemSelection,
        QThreadPool,
        QSize,
        Signal,
        Slot,
        QRunnable,
        QObject,
        Property,
        QPoint,
        QModelIndex,
        QFileInfo,
        Qt,
        QPointF,
        QRectF,
        QRect,
        QAbstractTableModel,
        QVariant,
        QEvent,
        QRegExp,
        QLineF,
    )
    from PySide2.QtGui import (
        QRegExpValidator,
        QFont,
        QPalette,
        QColor,
        QMovie,
        QWindow,
        QContextMenuEvent,
        QPixmap,
        QIcon,
        QWheelEvent,
        QImage,
        QBrush,
        QPainter,
        QMouseEvent,
        QCursor,
        QDragMoveEvent,
        QDragEnterEvent,
        QDropEvent,
        QCloseEvent,
        QShowEvent,
        QPen,
        QKeyEvent,
        QStandardItem,
        QFontMetrics,
        qRgb,
        QStandardItemModel,
    )

    from PySide2.QtWidgets import (
        QTableWidgetItem,
        QCompleter,
        QGraphicsObject,
        QButtonGroup,
        QHeaderView,
        QMainWindow,
        QMenuBar,
        QVBoxLayout,
        QRubberBand,
        QApplication,
        QFileSystemModel,
        QTabWidget,
        QWidget,
        QHBoxLayout,
        QLabel,
        QProgressBar,
        QFrame,
        QPushButton,
        QDockWidget,
        QFileDialog,
        QListView,
        QAbstractItemView,
        QTreeView,
        QMessageBox,
        QDialog,
        QTableWidget,
        QAbstractScrollArea,
        QMenu,
        QDesktopWidget,
        QAction,
        QWizard,
        QWizardPage,
        QGridLayout,
        QFormLayout,
        QGraphicsDropShadowEffect,
        QGroupBox,
        QSplitter,
        QGraphicsView,
        QGraphicsScene,
        QGraphicsPixmapItem,
        QTreeWidgetItem,
        QTreeWidget,
        QListWidgetItem,
        QDoubleSpinBox,
        QSpinBox,
        QLineEdit,
        QCheckBox,
        QToolBox,
        QListWidget,
        QComboBox,
        QGraphicsLineItem,
        QSizePolicy,
        QGraphicsSceneMouseEvent,
        QStyleOptionGraphicsItem,
        QGraphicsEllipseItem,
        QGraphicsRectItem,
        QTableView,
        QTextEdit,
        QRadioButton,
        QSlider,
        QStyledItemDelegate,
        QStatusBar,
        QScrollArea,
        QLayout,
        QToolBar,
        QPlainTextEdit,
        QDialogButtonBox,
        QGraphicsItem,
        QAbstractGraphicsShapeItem,
        QGraphicsSceneHoverEvent,
        QGraphicsSceneContextMenuEvent,
        QStyleOptionViewItem,
        QColorDialog,
    )
else:

    from PyQt5 import QtCore, QtGui, QtWidgets

    from PyQt5.QtCore import (
        QFile,
        QTextStream,
        QDir,
        QItemSelection,
        QEvent,
        QThreadPool,
        QSize,
        pyqtSignal as Signal,
        pyqtSlot as Slot,
        QRunnable,
        QObject,
        pyqtProperty as Property,
        QPoint,
        QModelIndex,
        QFileInfo,
        Qt,
        QPointF,
        QRectF,
        QRect,
        QAbstractTableModel,
        QVariant,
        QRegExp,
        QLineF,
    )
    from PyQt5.QtGui import (
        QFont,
        QPalette,
        QColor,
        QMovie,
        QWindow,
        QContextMenuEvent,
        QPixmap,
        QIcon,
        QWheelEvent,
        QImage,
        QBrush,
        QPainter,
        QMouseEvent,
        QCursor,
        QDragMoveEvent,
        QDragEnterEvent,
        QDropEvent,
        QCloseEvent,
        QShowEvent,
        QPen,
        QKeyEvent,
        QStandardItem,
        QFontMetrics,
        qRgb,
        QRegExpValidator,
        QStandardItemModel,
    )

    from PyQt5.QtWidgets import (
        QTableWidgetItem,
        QButtonGroup,
        QHeaderView,
        QMainWindow,
        QMenuBar,
        QVBoxLayout,
        QRubberBand,
        QApplication,
        QFileSystemModel,
        QTabWidget,
        QWidget,
        QHBoxLayout,
        QLabel,
        QProgressBar,
        QFrame,
        QPushButton,
        QDockWidget,
        QFileDialog,
        QListView,
        QAbstractItemView,
        QTreeView,
        QMessageBox,
        QDialog,
        QTableWidget,
        QSizePolicy,
        QAbstractScrollArea,
        QMenu,
        QDesktopWidget,
        QAction,
        QWizard,
        QWizardPage,
        QGridLayout,
        QFormLayout,
        QGraphicsDropShadowEffect,
        QGroupBox,
        QSplitter,
        QGraphicsView,
        QGraphicsScene,
        QGraphicsPixmapItem,
        QTreeWidgetItem,
        QTreeWidget,
        QListWidgetItem,
        QDoubleSpinBox,
        QSpinBox,
        QLineEdit,
        QCheckBox,
        QToolBox,
        QListWidget,
        QComboBox,
        QGraphicsLineItem,
        QGraphicsSceneMouseEvent,
        QStyleOptionGraphicsItem,
        QGraphicsEllipseItem,
        QGraphicsRectItem,
        QTableView,
        QTextEdit,
        QRadioButton,
        QSlider,
        QStyledItemDelegate,
        QStatusBar,
        QScrollArea,
        QLayout,
        QToolBar,
        QPlainTextEdit,
        QDialogButtonBox,
        QGraphicsObject,
        QCompleter,
        QGraphicsItem,
        QAbstractGraphicsShapeItem,
        QGraphicsSceneHoverEvent,
        QGraphicsSceneContextMenuEvent,
        QStyleOptionViewItem,
        QColorDialog,
    )
