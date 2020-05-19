import json
import math
import os
from collections import OrderedDict

import cv2
import dask
import imutils
import more_itertools
import numpy as np
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QSize, QThreadPool, QPointF, QPoint, QRectF, QItemSelection, QModelIndex
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget, QAbstractItemView, QDialog, QAction, \
    QLabel, QGraphicsScene, QMenu, QGraphicsDropShadowEffect, QFrame, QFormLayout, \
    QSpinBox, QMessageBox

from core import HubClientFactory, Framework
from dao import DatasetDao, AnnotaDao
from dao.hub_dao import HubDao
from dao.label_dao import LabelDao
from decor import gui_exception, work_exception
from util import GUIUtilities, Worker
from view.forms import NewRepoForm
from view.forms.label_form import NewLabelForm
from view.widgets.common import CustomNode
from view.widgets.common.custom_list import CustomListWidgetItem
from view.widgets.double_slider import DoubleSlider
from view.widgets.image_viewer import ImageViewer
from view.widgets.image_viewer.selection_mode import SELECTION_TOOL
from view.widgets.labels_tableview import LabelsTableView
from view.widgets.loading_dialog import QLoadingDialog
from view.widgets.models_treeview import ModelsTreeview
from vo import LabelVO, DatasetEntryVO, AnnotaVO, HubVO
from .base_image_viewer import Ui_Image_Viewer_Widget
from .items import EditableBox, EditablePolygon, EditableItem, EditableEllipse
from ..image_button import ImageButton


class SeparatorWidget(QFrame):
    def __init__(self, parent=None):
        super(SeparatorWidget, self).__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet('''
            QFrame{
                background-color: black;
            }
        ''')


class ImageViewerWidget(QWidget, Ui_Image_Viewer_Widget):
    def __init__(self, parent=None):
        super(ImageViewerWidget, self).__init__(parent)
        self.setupUi(self)

        self.image_viewer = ImageViewer()
        # self.image_viewer.scene().itemAdded.connect(self._scene_item_added)
        # self.image_viewer.key_press_sgn.connect(self.viewer_keyPressEvent)
        self.image_viewer.points_selection_sgn.connect(self.extreme_points_selection_done_slot)
        self.center_layout.addWidget(self.image_viewer, 0, 0)

        self._class_label = QLabel()
        self._class_label.setVisible(False)
        self._class_label.setMargin(5)
        self._class_label.setStyleSheet('''
            QLabel{
            font: 12pt;
            border-radius: 25px;
            margin: 10px;
            color: black; 
            background-color: #FFFFDC;
            }
        ''')
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setColor(QtGui.QColor(94, 93, 90).lighter())
        shadow.setOffset(2)
        self._class_label.setGraphicsEffect(shadow)
        self.center_layout.addWidget(self._class_label, 0, 0, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        self.actions_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        self.actions_layout.setContentsMargins(0, 5, 0, 0)
        self.images_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.images_list_widget.currentItemChanged.connect(self.image_list_sel_changed_slot)
        self.images_list_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.images_list_widget.customContextMenuRequested.connect(self.image_list_context_menu)
        self.images_list_widget.setCursor(QtCore.Qt.PointingHandCursor)

        self.treeview_models = ModelsTreeview()
        self.treeview_models.setColumnWidth(0, 300)
        self.tree_view_models_layout.addWidget(self.treeview_models)
        self.treeview_models.action_click.connect(self.trv_models_action_click_slot)

        self.treeview_labels = LabelsTableView()
        self.treeview_labels.action_click.connect(self.trv_labels_action_click_slot)
        self.tree_view_labels_layout.addWidget(self.treeview_labels)
        self.treeview_labels.selectionModel().selectionChanged.connect(self.default_label_changed_slot)

        # image adjustment controls
        img_adjust_controls_layout = QFormLayout()
        self.img_adjust_page.setLayout(img_adjust_controls_layout)
        self._brightness_slider = DoubleSlider()
        self._brightness_slider.setMinimum(0.0)
        self._brightness_slider.setMaximum(100.0)
        self._brightness_slider.setSingleStep(0.5)
        self._brightness_slider.setValue(self.image_viewer.img_brightness)
        self._brightness_slider.setOrientation(QtCore.Qt.Horizontal)

        self._contrast_slider = DoubleSlider()
        self._contrast_slider.setMinimum(1.0)
        self._contrast_slider.setMaximum(3.0)
        self._contrast_slider.setSingleStep(0.1)
        self._contrast_slider.setValue(self.image_viewer.img_contrast)
        self._contrast_slider.setOrientation(QtCore.Qt.Horizontal)

        self._gamma_slider = DoubleSlider()
        self._gamma_slider.setMinimum(1.0)
        self._gamma_slider.setMaximum(5.0)
        self._gamma_slider.setSingleStep(0.1)
        self._gamma_slider.setValue(self.image_viewer.img_gamma)
        self._gamma_slider.setOrientation(QtCore.Qt.Horizontal)
        self._number_of_clusters_spin = QSpinBox()
        self._number_of_clusters_spin.setMinimum(2)
        self._number_of_clusters_spin.setValue(5)

        self._contrast_slider.doubleValueChanged.connect(self._update_contrast_slot)
        self._brightness_slider.doubleValueChanged.connect(self._update_brightness_slot)
        self._gamma_slider.doubleValueChanged.connect(self._update_gamma_slot)

        img_adjust_controls_layout.addRow(QLabel("Brightness:"), self._brightness_slider)
        img_adjust_controls_layout.addRow(QLabel("Contrast:"), self._contrast_slider)
        img_adjust_controls_layout.addRow(QLabel("Gamma:"), self._gamma_slider)
        img_adjust_controls_layout.addRow(QLabel("Clusters:"), self._number_of_clusters_spin)

        self.img_adjust_page.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.img_adjust_page.customContextMenuRequested.connect(self._image_processing_tools_ctx_menu)

        self._ds_dao = DatasetDao()
        self._hub_dao = HubDao()
        self._labels_dao = LabelDao()
        self._ann_dao = AnnotaDao()
        self._thread_pool = QThreadPool()
        self._loading_dialog = QLoadingDialog()
        self._tag = None
        self._curr_channel = 0
        self._channels = []
        self._toolbox = []
        self.build_toolbox()

    @property
    def image(self):
        return self.image_viewer.image

    @image.setter
    def image(self, value):
        self.image_viewer.image = value

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value
        if self._tag:
            dataset_id = self._tag.dataset
            self.image_viewer.dataset = dataset_id

    @property
    def channels(self):
        return self._channels

    @property
    def curr_channel(self):
        return self._curr_channel

    @curr_channel.setter
    def curr_channel(self, value):
        self._curr_channel = value

    def build_toolbox(self):
        icon_size = QSize(28, 28)
        self._toolbox = [
            ImageButton(icon=GUIUtilities.get_icon("polygon.png"), size=icon_size, tag="polygon"),
            ImageButton(icon=GUIUtilities.get_icon("square.png"), size=icon_size, tag="box"),
            ImageButton(icon=GUIUtilities.get_icon("circle.png"), size=icon_size, tag="ellipse"),
            ImageButton(icon=GUIUtilities.get_icon("highlighter.png"), size=icon_size, tag="free"),
            ImageButton(icon=GUIUtilities.get_icon("robotic-hand.png"), size=icon_size, tag="points"),
            ImageButton(icon=GUIUtilities.get_icon("cursor.png"), size=icon_size, tag="pointer"),
            ImageButton(icon=GUIUtilities.get_icon("save-icon.png"), size=icon_size, tag="save"),
            ImageButton(icon=GUIUtilities.get_icon("clean.png"), size=icon_size, tag="clean")]
        for button in self._toolbox:
            self.actions_layout.addWidget(button)
            self.actions_layout.addWidget(SeparatorWidget())
            button.clicked.connect(self._action_toolbox_clicked_slot)

    def _action_toolbox_clicked_slot(self):
        button: ImageButton = self.sender()
        action_tag = button.tag
        tools_dict = {
            "polygon": SELECTION_TOOL.POLYGON,
            "box": SELECTION_TOOL.BOX,
            "ellipse": SELECTION_TOOL.ELLIPSE,
            "free": SELECTION_TOOL.FREE,
            "points": SELECTION_TOOL.EXTREME_POINTS,
            "pointer": SELECTION_TOOL.POINTER
        }
        if action_tag in tools_dict:
            self.image_viewer.current_tool = tools_dict[action_tag]
        else:
            if action_tag == "save":
                @gui_exception
                def done_work(result):
                    _, err = result
                    if err:
                        raise err
                    GUIUtilities.show_info_message("Annotations saved successfully", "Information")

                self.save_annotations(done_work)
            elif action_tag == "clean":
                self.image_viewer.remove_annotations()

    @gui_exception
    def bind(self):
        @work_exception
        def do_work():
            return dask.compute(*[
                self.load_images(),
                self.load_models(),
                self.load_labels()
            ]), None

        @gui_exception
        def done_work(args):
            result, error = args
            if result:
                images, models, labels = result
                if models:
                    for model in models:
                        self.treeview_models.add_node(model)
                if labels:
                    for entry in labels:
                        self.treeview_labels.add_row(entry)
                selected_image = None
                icon = GUIUtilities.get_icon("image.png")
                for img in images:
                    if os.path.isfile(img.file_path):
                        item = CustomListWidgetItem(img.file_path, tag=img)
                        item.setIcon(icon)
                        self.images_list_widget.addItem(item)
                        if img.file_path == self.tag.file_path:
                            selected_image = item
                    self.images_list_widget.setCurrentItem(selected_image)

        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)

    @dask.delayed
    def load_images(self) -> [DatasetEntryVO]:
        dataset_id = self.tag.dataset
        return self._ds_dao.fetch_entries(dataset_id)

    @dask.delayed
    def load_models(self) -> [HubVO]:
        return self._hub_dao.fetch_all()

    @dask.delayed
    def load_labels(self):
        dataset_id = self.tag.dataset
        return self._labels_dao.fetch_all(dataset_id)

    @gui_exception
    def image_list_sel_changed_slot(self, curr: CustomListWidgetItem, prev: CustomListWidgetItem):
        self.image, self.tag = cv2.imread(curr.tag.file_path, cv2.IMREAD_COLOR), curr.tag
        self.load_image()

    @gui_exception
    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        row = self.images_list_widget.currentRow()
        last_index = self.images_list_widget.count() - 1
        if event.key() == QtCore.Qt.Key_A:
            @gui_exception
            def done_work(result):
                _, err = result
                if err:
                    raise err
                if row > 0:
                    self.images_list_widget.setCurrentRow(row - 1)
                else:
                    self.images_list_widget.setCurrentRow(last_index)

            self.save_annotations(done_work)
        elif event.key() == QtCore.Qt.Key_D:
            @gui_exception
            def done_work(result):
                _, err = result
                if err:
                    raise err
                if row < last_index:
                    self.images_list_widget.setCurrentRow(row + 1)
                else:
                    self.images_list_widget.setCurrentRow(0)

            self.save_annotations(done_work)
        super(ImageViewerWidget, self).keyPressEvent(event)

    def _update_contrast_slot(self, val):
        self.image_viewer.img_contrast = val
        self.image_viewer.update_viewer(fit_image=False)

    def _update_gamma_slot(self, val):
        self.image_viewer.img_gamma = val
        self.image_viewer.update_viewer(fit_image=False)

    def _update_brightness_slot(self, val):
        self.image_viewer.img_brightness = val
        self.image_viewer.update_viewer(fit_image=False)

    def _reset_sliders(self):
        self._gamma_slider.setValue(1.0)
        self._brightness_slider.setValue(50.0)
        self._contrast_slider.setValue(1.0)

    @gui_exception
    def _image_processing_tools_ctx_menu(self, pos: QPoint):
        menu = QMenu(self)
        action1 = QAction("Reset Image")
        action1.setData("reset")
        action2 = QAction("Equalize Histogram")
        action2.setData("equalize_histo")
        action3 = QAction("Correct Lightness")
        action3.setData("correct_l")
        action4 = QAction("Cluster Image")
        action4.setData("clustering")
        menu.addActions([action1, action2, action3, action4])
        action = menu.exec_(self.img_adjust_page.mapToGlobal(pos))
        if action:
            self._process_image_adjust_oper(action)

    def _process_image_adjust_oper(self, action: QAction):
        curr_action = action.data()
        k = self._number_of_clusters_spin.value()
        @work_exception
        def do_work():
            if curr_action == "reset":
                self._reset_sliders()
                self.image_viewer.reset_viewer()
            elif curr_action == "equalize_histo":
                self.image_viewer.equalize_histogram()
            elif curr_action == "correct_l":
                self.image_viewer.correct_lightness()
            elif curr_action == "clustering":
                self.image_viewer.clusterize(k=k)

            return None, None

        @gui_exception
        def done_work(result):
            out, err = result
            if err:
                return
            self._loading_dialog.hide()
            self.image_viewer.update_viewer()

        self._loading_dialog.show()
        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)

    def default_label_changed_slot(self, selection: QItemSelection):
        selected_rows = self.treeview_labels.selectionModel().selectedRows(2)
        if len(selected_rows) > 0:
            index: QModelIndex = selected_rows[0]
            current_label: LabelVO = self.treeview_labels.model().data(index)
            self.image_viewer.current_label = current_label

    @gui_exception
    def extreme_points_selection_done_slot(self, points: []):
        self.predict_annotations_using_extr_points(points)

    @gui_exception
    def trv_labels_action_click_slot(self, action: QAction):
        model = self.treeview_labels.model()
        if action.text() == self.treeview_labels.CTX_MENU_ADD_LABEL:
            form = NewLabelForm()
            if form.exec_() == QDialog.Accepted:
                label_vo: LabelVO = form.result
                label_vo.dataset = self.tag.dataset
                label_vo = self._labels_dao.save(label_vo)
                self.treeview_labels.add_row(label_vo)
        elif action.text() == self.treeview_labels.CTX_MENU_DELETE_LABEL:
            reply = QMessageBox.question(self, 'Delete Label',
                                         "Are you sure?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
            index: QModelIndex = action.data()
            if index:
                label_vo = model.index(index.row(), 2).data()
                self._labels_dao.delete(label_vo.id)  # TODO: this method should be call from other thread
                self.image_viewer.remove_annotations_by_label(label_vo.name)
                model.removeRow(index.row())

    @gui_exception
    def add_repository(self, repo_path):

        @work_exception
        def do_work():
            hub_client = HubClientFactory.create(Framework.PyTorch)
            hub = hub_client.fetch_model(repo_path, force_reload=True)
            id = self._hub_dao.save(hub)
            hub.id = id
            return hub, None

        @gui_exception
        def done_work(result):
            self._loading_dialog.close()
            hub, error = result
            if error:
                raise error
            self.treeview_models.add_node(hub)

        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)
        self._loading_dialog.exec_()

    @gui_exception
    def update_repository(self, hub: HubVO):
        hub_path = hub.path
        hub_id = hub.id

        @work_exception
        def do_work():
            hub_client = HubClientFactory.create(Framework.PyTorch)
            hub = hub_client.fetch_model(hub_path, force_reload=True)
            hub.id = hub_id
            self._hub_dao.update(hub)
            return hub, None

        @gui_exception
        def done_work(result):
            self._loading_dialog.close()
            hub, error = result
            if error:
                raise error
            self.treeview_models.add_node(hub)

        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)
        self._loading_dialog.exec_()

    @gui_exception
    def trv_models_action_click_slot(self, action: QAction):
        model = self.treeview_models.model()
        if action.text() == self.treeview_models.CTX_MENU_ADD_REPOSITORY_ACTION:
            form = NewRepoForm()
            if form.exec_() == QDialog.Accepted:
                repository = form.result
                self.add_repository(repository)
        elif action.text() == self.treeview_models.CTX_MENU_UPDATE_REPO_ACTION:
            index: QModelIndex = action.data()
            node: CustomNode = index.internalPointer()
            hub: HubVO = node.tag
            if hub and hub.id:
                model.removeChild(index)
                self.update_repository(hub)
        elif action.text() == self.treeview_models.CTX_MENU_AUTO_LABEL_ACTION:
            index: QModelIndex = action.data()
            node: CustomNode = index.internalPointer()
            parent_node = node.parent  # repo
            repo, model_name = parent_node.get_data(0), node.get_data(0)
            self.predict_annotations_using_pytorch_thub_model(repo, model_name)
        if action.text() == self.treeview_models.CTX_MENU_DELETE_REPO_ACTION:
            reply = QMessageBox.question(self, 'Delete Repository',
                                         "Are you sure?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
            index: QModelIndex = action.data()
            node: CustomNode = index.internalPointer()
            hub: HubVO = node.tag
            if hub:
                self._hub_dao.delete(hub.id)  # TODO: this method should be call from other thread
                model.removeChild(index)

    def image_list_context_menu(self, pos: QPoint):
        menu = QMenu()
        result = self._labels_dao.fetch_all(self.tag.dataset)
        if len(result) > 0:
            labels_menu = menu.addMenu("labels")
            for vo in result:
                action = labels_menu.addAction(vo.name)
                action.setData(vo)
        action = menu.exec_(QCursor.pos())
        if action and isinstance(action.data(), LabelVO):
            label = action.data()
            self.change_image_labels(label)

    def change_image_labels(self, label: LabelVO):
        items = self.images_list_widget.selectedItems()
        selected_images = []
        for item in items:
            vo = item.tag
            selected_images.append(vo)

        @work_exception
        def do_work():
            self._ds_dao.tag_entries(selected_images, label)
            return 1, None

        @gui_exception
        def done_work(result):
            status, err = result
            if err:
                raise err

        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)

    @dask.delayed
    def load_image_label(self):
        return self._ann_dao.get_label(self.tag.id)

    @dask.delayed
    def load_image_annotations(self):
        return self._ann_dao.fetch_all(self.tag.id)

    def load_image(self):
        @work_exception
        def do_work():
            return dask.compute(*[
                self.load_image_label(),
                self.load_image_annotations()
            ]), None

        @gui_exception
        def done_work(args):
            result, error = args
            if result:
                label, annotations = result
                if label:
                    self._class_label.setVisible(True)
                    self._class_label.setText(label)
                else:
                    self._class_label.setVisible(False)
                    self._class_label.setText("")

                if annotations:
                    img_bbox: QRectF = self.image_viewer.pixmap.sceneBoundingRect()
                    offset = QPointF(img_bbox.width() / 2, img_bbox.height() / 2)
                    for entry in annotations:
                        try:
                            vo: AnnotaVO = entry
                            points = map(float, vo.points.split(","))
                            points = list(more_itertools.chunked(points, 2))
                            if vo.kind == "box" or vo.kind == "ellipse":
                                x = points[0][0] - offset.x()
                                y = points[0][1] - offset.y()
                                w = math.fabs(points[0][0] - points[1][0])
                                h = math.fabs(points[0][1] - points[1][1])
                                roi: QRectF = QRectF(x, y, w, h)
                                if vo.kind == "box":
                                    item = EditableBox(roi)
                                else:
                                    item = EditableEllipse()
                                item.tag = self.tag.dataset
                                item.setRect(roi)
                                item.label = vo.label
                                self.image_viewer.scene().addItem(item)
                            elif vo.kind == "polygon":
                                item = EditablePolygon()
                                item.label = vo.label
                                item.tag = self.tag.dataset
                                self.image_viewer.scene().addItem(item)
                                for p in points:
                                    item.addPoint(QPoint(p[0] - offset.x(), p[1] - offset.y()))
                        except Exception as ex:
                            GUIUtilities.show_error_message("Error loading the annotations: {}".format(ex), "Error")

        self.image_viewer.remove_annotations()
        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)

    @gui_exception
    def save_annotations(self, done_work_callback):
        scene: QGraphicsScene = self.image_viewer.scene()
        annotations = []
        for item in scene.items():
            image_rect: QRectF = self.image_viewer.pixmap.sceneBoundingRect()
            image_offset = QPointF(image_rect.width() / 2, image_rect.height() / 2)
            if isinstance(item, EditableItem):
                a = AnnotaVO()
                a.label = item.label.id if item.label else None
                a.entry = self.tag.id
                a.kind = item.shape_type
                a.points = item.coordinates(image_offset)
                annotations.append(a)

        @work_exception
        def do_work():
            self._ann_dao.save(self.tag.id, annotations)
            return None, None

        worker = Worker(do_work)
        worker.signals.result.connect(done_work_callback)
        self._thread_pool.start(worker)

    @staticmethod
    def invoke_tf_hub_model(image_path, repo, model_name):
        from PIL import Image
        from torchvision import transforms
        import torch
        gpu_id = 0
        device = torch.device("cuda:" + str(gpu_id) if torch.cuda.is_available() else "cpu")
        model = torch.hub.load(repo, model_name, pretrained=True)
        model.eval()
        input_image = Image.open(image_path)
        preprocess = transforms.Compose([
            transforms.Resize(480),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        input_tensor = preprocess(input_image)
        input_batch = input_tensor.unsqueeze(0)  # create a mini-batch as expected by the model
        # # move the param and model to GPU for speed if available
        if torch.cuda.is_available():
            input_batch = input_batch.to(device)
            model.to(device)
        with torch.no_grad():
            output = model(input_batch)
        if isinstance(output, OrderedDict):
            output = output["out"][0]
            predictions_tensor = output.argmax(0)
            # move predictions to the cpu and convert into a numpy array
            predictions_arr: np.ndarray = predictions_tensor.byte().cpu().numpy()
            classes_ids = np.unique(predictions_arr).tolist()
            classes_idx = list(filter(lambda x: x != 0, classes_ids))  ## ignore
            predictions_arr = Image.fromarray(predictions_arr).resize(input_image.size)
            predictions_arr = np.asarray(predictions_arr)
            # 0 value
            predicted_mask = {c: [] for c in classes_idx}

            for idx in classes_idx:
                class_mask = np.zeros(predictions_arr.shape, dtype=np.uint8)
                class_mask[np.where(predictions_arr == idx)] = 255
                contour_list = cv2.findContours(class_mask.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                contour_list = imutils.grab_contours(contour_list)
                for contour in contour_list:
                    points = np.vstack(contour).squeeze().tolist()
                    predicted_mask[idx].append(points)
                return "mask", predicted_mask
        else:
            class_map = json.load(open("./data/imagenet_class_index.json"))
            max, argmax = output.data.squeeze().max(0)
            class_id = argmax.item()
            predicted_label = class_map[str(class_id)]
            return "label", predicted_label

        return None

    @staticmethod
    def invoke_dextr_pascal_model(image_path, points):
        import torch
        from collections import OrderedDict
        from PIL import Image
        import numpy as np
        from torch.nn.functional import upsample
        from contrib.dextr import deeplab_resnet  as resnet
        from contrib.dextr import helpers
        modelName = 'dextr_pascal-sbd'
        pad = 50
        thres = 0.8
        gpu_id = 0
        device = torch.device("cuda:" + str(gpu_id) if torch.cuda.is_available() else "cpu")
        #  Create the network and load the weights
        model = resnet.resnet101(1, nInputChannels=4, classifier='psp')
        model_path = os.path.abspath("./models/{}.pth".format(modelName))
        state_dict_checkpoint = torch.load(model_path, map_location=lambda storage, loc: storage)
        if 'module.' in list(state_dict_checkpoint.keys())[0]:
            new_state_dict = OrderedDict()
            # remove `module.` from multi-gpu training
            for k, v in state_dict_checkpoint.items():
                name = k[7:]
                new_state_dict[name] = v
        else:
            new_state_dict = state_dict_checkpoint
        model.load_state_dict(new_state_dict)
        model.eval()
        model.to(device)
        #  Read image and click the points
        image = np.array(Image.open(image_path))
        extreme_points_ori = np.asarray(points).astype(np.int)
        with torch.no_grad():
            #  Crop image to the bounding box from the extreme points and resize
            bbox = helpers.get_bbox(image, points=extreme_points_ori, pad=pad, zero_pad=True)
            crop_image = helpers.crop_from_bbox(image, bbox, zero_pad=True)
            resize_image = helpers.fixed_resize(crop_image, (512, 512)).astype(np.float32)

            #  Generate extreme point heat map normalized to image values
            extreme_points = extreme_points_ori - [np.min(extreme_points_ori[:, 0]),
                                                   np.min(extreme_points_ori[:, 1])] + [pad,
                                                                                        pad]
            extreme_points = (512 * extreme_points * [1 / crop_image.shape[1], 1 / crop_image.shape[0]]).astype(np.int)
            extreme_heatmap = helpers.make_gt(resize_image, extreme_points, sigma=10)
            extreme_heatmap = helpers.cstm_normalize(extreme_heatmap, 255)

            #  Concatenate inputs and convert to tensor
            input_dextr = np.concatenate((resize_image, extreme_heatmap[:, :, np.newaxis]), axis=2)
            inputs = torch.from_numpy(input_dextr.transpose((2, 0, 1))[np.newaxis, ...])

            # Run a forward pass
            inputs = inputs.to(device)
            outputs = model.forward(inputs)
            outputs = upsample(outputs, size=(512, 512), mode='bilinear', align_corners=True)
            outputs = outputs.to(torch.device('cpu'))

            pred = np.transpose(outputs.data.numpy()[0, ...], (1, 2, 0))
            pred = 1 / (1 + np.exp(-pred))
            pred = np.squeeze(pred)
            result = helpers.crop2fullmask(pred, bbox, im_size=image.shape[:2], zero_pad=True, relax=pad) > thres
            binary = np.zeros_like(result, dtype=np.uint8)
            binary[result] = 255
            contour_list = cv2.findContours(binary.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            contour_list = imutils.grab_contours(contour_list)
            contours = []
            for contour in contour_list:
                c_points = np.vstack(contour).squeeze().tolist()
                contours.append(c_points)
        return contours

    @staticmethod
    def invoke_cov19_model(image_path, repo, model_name):
        from PIL import Image
        from torchvision import transforms
        import torch

        model = torch.hub.load(repo, model_name, pretrained=True, force_reload=False)
        model.eval()
        input_image = Image.open(image_path)
        input_image = input_image.convert("RGB")
        preprocess = transforms.Compose([
            transforms.Resize(255),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        input_tensor = preprocess(input_image)
        input_batch = input_tensor.unsqueeze(0)
        output = model(input_batch)
        _, preds_tensor = torch.max(output, 1)
        top_pred = np.squeeze(preds_tensor.numpy())
        labels_map = {0: "conv19", 1: "normal"}
        class_idx = top_pred.item()
        # show top class
        return "label", [class_idx, labels_map[class_idx]]

    @gui_exception
    def predict_annotations_using_pytorch_thub_model(self, repo, model_name):
        @work_exception
        def do_work():
            if model_name == "covid19":
                pred_result = self.invoke_cov19_model(self.tag.file_path, repo, model_name)
            else:
                pred_result = self.invoke_tf_hub_model(self.tag.file_path, repo, model_name)
            return pred_result, None

        @gui_exception
        def done_work(result):
            self._loading_dialog.hide()
            pred_out, err = result
            if err:
                raise err
            if pred_out:
                pred_type, pred_res = pred_out
                if pred_type == "mask":
                    for class_idx, contours in pred_res.items():
                        if len(contours) > 0:
                            for c in contours:
                                points = []
                                for i in range(0, len(c), 10):
                                    points.append(c[i])
                                if len(points) > 5:
                                    polygon = EditablePolygon()
                                    polygon.tag = self.tag.dataset
                                    self.image_viewer._scene.addItem(polygon)
                                    bbox: QRectF = self.image_viewer.pixmap.boundingRect()
                                    offset = QPointF(bbox.width() / 2, bbox.height() / 2)
                                    for point in points:
                                        if isinstance(point, list) and len(point) == 2:
                                            polygon.addPoint(QPoint(point[0] - offset.x(), point[1] - offset.y()))
                else:
                    class_id, class_name = pred_res
                    GUIUtilities.show_info_message("predicted label : `{}`".format(class_name), "prediction result")

        self._loading_dialog.show()
        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)

    @gui_exception
    def predict_annotations_using_extr_points(self, points):
        pass

        @work_exception
        def do_work():
            contours = self.invoke_dextr_pascal_model(self.tag.file_path, points)
            return contours, None

        @gui_exception
        def done_work(result):
            self._loading_dialog.hide()
            pred_out, err = result
            if err:
                raise err
            if pred_out:
                for c in pred_out:
                    c_points = []
                    for i in range(0, len(c), 10):
                        c_points.append(c[i])
                    if len(c_points) > 5:
                        polygon = EditablePolygon()
                        polygon.tag = self.tag.dataset
                        self.image_viewer._scene.addItem(polygon)
                        bbox: QRectF = self.image_viewer.pixmap.boundingRect()
                        offset = QPointF(bbox.width() / 2, bbox.height() / 2)
                        for point in c_points:
                            polygon.addPoint(QPoint(point[0] - offset.x(), point[1] - offset.y()))

        self._loading_dialog.show()
        worker = Worker(do_work)
        worker.signals.result.connect(done_work)
        self._thread_pool.start(worker)
