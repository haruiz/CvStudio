import itertools
import json
import os
import random
from xml.etree import ElementTree

import cv2
import dask
from PyQt5 import QtCore
from PyQt5.QtCore import QThreadPool,QSize,QObject,pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QScrollArea,QWidget,QMessageBox,QDialog,QTabWidget,QFileDialog,QMenu
from hurry.filesize import size,alternative
from mako.template import Template
import xml.etree.ElementTree as ET

from dao import AnnotaDao,LabelDao
from dao.dataset_dao import DatasetDao
from decor import gui_exception,work_exception
from util import GUIUtilities,Worker,FileUtilities,ColorUtilities,ColorFormat
from view.forms import DatasetForm
from vo import DatasetVO,AnnotaVO,LabelVO
from .image_button import ImageButton
from .loading_dialog import QLoadingDialog
from .response_grid import GridCard
from .response_grid import ResponseGridLayout
from .tab_media import MediaTabWidget


class DatasetGridWidget(QWidget,QObject):
    new_dataset_action_signal=pyqtSignal()
    open_dataset_action_signal=pyqtSignal(DatasetVO)
    delete_dataset_action_signal=pyqtSignal(DatasetVO)
    refresh_dataset_action_signal=pyqtSignal(DatasetVO)
    edit_dataset_action_signal=pyqtSignal(DatasetVO)
    download_anno_action_signal=pyqtSignal(DatasetVO)
    import_anno_action_signal=pyqtSignal(DatasetVO)

    def __init__(self,parent=None):
        super(DatasetGridWidget,self).__init__(parent)
        self.grid_layout=ResponseGridLayout()
        self.grid_layout.cols=8
        self.setLayout(self.grid_layout)
        self._entries=None
        self.layout().setAlignment(QtCore.Qt.AlignTop)

    @property
    def data_source(self):
        return self._entries

    @data_source.setter
    def data_source(self,value):
        self._entries=value

    def build_ds_card(self,ds: DatasetVO):
        card_widget: GridCard=GridCard(debug=False)
        card_widget.label="{} \n {}".format(ds.name,size(ds.size,system=alternative) if ds.size else "0 MB")
        btn_delete=ImageButton(GUIUtilities.get_icon("delete.png"),size=QSize(15,15))
        btn_delete.setToolTip("Delete dataset")
        btn_edit=ImageButton(GUIUtilities.get_icon("edit.png"),size=QSize(15,15))
        btn_edit.setToolTip("Edit dataset")
        btn_refresh=ImageButton(GUIUtilities.get_icon("refresh.png"),size=QSize(15,15))
        btn_refresh.setToolTip("Refresh dataset")
        btn_export_annotations=ImageButton(GUIUtilities.get_icon("download.png"),size=QSize(15,15))
        btn_export_annotations.setToolTip("Export annotations")
        btn_import_annotations=ImageButton(GUIUtilities.get_icon("upload.png"),size=QSize(15,15))
        btn_import_annotations.setToolTip("Import annotations")

        card_widget.add_buttons([btn_delete,btn_edit,btn_refresh,btn_export_annotations,btn_import_annotations])
        icon_file="folder_empty.png"
        icon=GUIUtilities.get_icon(icon_file)
        # events
        btn_delete.clicked.connect(lambda: self.delete_dataset_action_signal.emit(ds))
        btn_edit.clicked.connect(lambda: self.edit_dataset_action_signal.emit(ds))
        btn_export_annotations.clicked.connect(lambda: self.download_anno_action_signal.emit(ds))
        btn_import_annotations.clicked.connect(lambda: self.import_anno_action_signal.emit(ds))
        card_widget.body=ImageButton(icon)
        btn_refresh.clicked.connect(lambda: self.refresh_dataset_action_signal.emit(ds))
        card_widget.body.doubleClicked.connect(lambda evt: self.open_dataset_action_signal.emit(ds))

        return card_widget

    def build_new_button(self):
        new_dataset_widget: GridCard=GridCard(with_actions=False,with_title=False)
        btn_new_dataset=ImageButton(GUIUtilities.get_icon("new_folder.png"))
        new_dataset_widget.body=btn_new_dataset
        btn_new_dataset.clicked.connect(lambda: self.new_dataset_action_signal.emit())

        return new_dataset_widget

    def bind(self) -> None:
        cards_list=[]
        new_dataset_button=self.build_new_button()
        cards_list.append(new_dataset_button)
        for ds in self.data_source:
            card_widget=self.build_ds_card(ds)
            cards_list.append(card_widget)
        self.grid_layout.widgets=cards_list
        super(DatasetGridWidget,self).update()


class DatasetTabWidget(QScrollArea):
    JSON="JSON"
    PASCAL_VOC="Pascal VOC"
    TENSORFLOW_OBJECT_DETECTION="TensorFlow Object Detection"
    YOLO="YOLO"

    def __init__(self,parent=None):
        super(DatasetTabWidget,self).__init__(parent)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_grid=DatasetGridWidget()
        self.data_grid.new_dataset_action_signal.connect(self.btn_new_dataset_on_slot)
        self.data_grid.delete_dataset_action_signal.connect(self.btn_delete_dataset_on_slot)
        self.data_grid.refresh_dataset_action_signal.connect(self.refresh_dataset_action_slot)
        self.data_grid.edit_dataset_action_signal.connect(self.edit_dataset_action_slot)
        self.data_grid.open_dataset_action_signal.connect(self.open_dataset_action_slot)
        self.data_grid.download_anno_action_signal.connect(self.download_annot_action_slot)
        self.data_grid.import_anno_action_signal.connect(self.import_annot_action_slot)

        self.setWidget(self.data_grid)
        self.setWidgetResizable(True)
        self.thread_pool=QThreadPool()
        self.loading_dialog=QLoadingDialog()
        self._ds_dao=DatasetDao()
        self._labels_dao = LabelDao()
        self._annot_dao=AnnotaDao()
        self.load()

    @gui_exception
    def load(self):
        @work_exception
        def do_work():
            results=self._ds_dao.fetch_all_with_size()
            return results,None

        @gui_exception
        def done_work(result):
            data,error=result
            if error:
                raise error
            self.data_grid.data_source=data
            self.data_grid.bind()

        worker=Worker(do_work)
        worker.signals.result.connect(done_work)
        self.thread_pool.start(worker)

    def _close_tab(self,tab_class):
        tab_widget_manager: QTabWidget=self.window().tab_widget_manager
        for i in range(tab_widget_manager.count()):
            curr_tab_widget=tab_widget_manager.widget(i)
            if isinstance(curr_tab_widget,tab_class):
                tab_widget_manager.removeTab(i)

    @QtCore.pyqtSlot()
    @gui_exception
    def btn_new_dataset_on_slot(self):
        form=DatasetForm()
        if form.exec_() == QDialog.Accepted:
            vo: DatasetVO=form.value
            self._ds_dao.save(vo)
            self.load()

    @QtCore.pyqtSlot(DatasetVO)
    @gui_exception
    def btn_delete_dataset_on_slot(self,vo: DatasetVO):
        reply=QMessageBox.question(self,'Confirmation',"Are you sure?",QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._ds_dao.delete(vo.id)
            usr_folder=FileUtilities.get_usr_folder()
            ds_folder=os.path.join(usr_folder,vo.folder)
            FileUtilities.delete_folder(ds_folder)
            self.load()

    @QtCore.pyqtSlot(DatasetVO)
    @gui_exception
    def edit_dataset_action_slot(self,vo: DatasetVO):
        form=DatasetForm(vo)
        if form.exec_() == QDialog.Accepted:
            vo: DatasetVO=form.value
            self._ds_dao.save(vo)
            self.load()

    @QtCore.pyqtSlot(DatasetVO)
    def refresh_dataset_action_slot(self,vo: DatasetVO):
        self.load()

    @QtCore.pyqtSlot(DatasetVO)
    def open_dataset_action_slot(self,vo: DatasetVO):
        tab_widget_manager: QTabWidget=self.window().tab_widget_manager
        tab_widget=MediaTabWidget(vo)
        # self._close_tab(MediaTabWidget)
        for i in range(tab_widget_manager.count()):
            tab_widget_manager.removeTab(i)
        index=tab_widget_manager.addTab(tab_widget,vo.name)
        tab_widget_manager.setCurrentIndex(index)

    def annotations2json(self,images,selected_folder):
        def export_template(img_path,img_annotations):
            str_template='''
            {
              "path": "${path}",
              "regions": [
                % for i, region in enumerate(annotations):
                    {
                        "kind": "${region["annot_kind"]}",
                        "points": "${region["annot_points"]}",
                        "label": "${region["label_name"]}",
                        "color": "${region["label_color"]}"
                    } 
                    % if i < len(annotations) - 1:
                    ,
                    % endif
                % endfor
              ]
            }
            '''
            json_str=Template(str_template).render(path=img_path,annotations=list(img_annotations))
            filename=os.path.split(img_path)[1]
            file_name,_=os.path.splitext(filename)
            output_file=os.path.join(selected_folder,"{}.json".format(file_name))
            with open(output_file,'w') as f:
                json.dump(json.loads(json_str),f,indent=3)

        delayed_tasks=[]
        for img_path,img_annotations in images:
            delayed_tasks.append(dask.delayed(export_template)(img_path,img_annotations))
        dask.compute(*delayed_tasks)

    def annotations2pascal(self,images,selected_folder):
        def export_template(img_path,img_annotations):
            str_template='''
            <annotation>
                <folder>${folder}</folder>
                <filename>${filename}</filename>
                <path>${path}</path>
                <source>
                    <database>Unknown</database>
                </source>
                <size>
                    <width>${width}</width>
                    <height>${height}</height>
                    <depth>${depth}</depth>
                </size>
                <segmented>0</segmented>
                % for i, region in enumerate(annotations):
                    <object>
                        <name>${region["name"]}</name>
                        <pose>Unspecified</pose>
                        <truncated>0</truncated>
                        <difficult>0</difficult>
                        <bndbox>
                            <xmin>${region["xmin"]}</xmin>
                            <ymin>${region["ymin"]}</ymin>
                            <xmax>${region["xmax"]}</xmax>
                            <ymax>${region["ymax"]}</ymax>
                        </bndbox>
                    </object>
                % endfor
            </annotation>
            '''
            filename=os.path.split(img_path)[1]
            folder=os.path.split(os.path.dirname(img_path))[1]
            h,w,c=cv2.imread(img_path).shape

            xml_str=Template(str_template).render(
                path=img_path,
                folder=folder,
                filename=filename,
                width=w,
                height=h,
                depth=c,
                annotations=img_annotations)

            file_name,_=os.path.splitext(filename)
            output_file=os.path.join(selected_folder,"{}.xml".format(file_name))
            with open(output_file,'w') as f:
                f.write(xml_str)

        delayed_tasks=[]
        for img_path,img_annotations in images:
            boxes=[]
            for annot in img_annotations:
                if annot["annot_kind"] == "box":
                    points=list(map(int,annot["annot_points"].split(",")))
                    box=dict()
                    box["name"]=annot["label_name"]
                    box["xmin"]=points[0]
                    box["ymin"]=points[1]
                    box["xmax"]=points[2]
                    box["ymax"]=points[3]
                    boxes.append(box)
            if len(boxes) > 0:
                delayed_tasks.append(dask.delayed(export_template)(img_path,boxes))
        dask.compute(*delayed_tasks)

    def annotations2Yolo(self,images,selected_folder):
        pass

    @gui_exception
    def download_annot_action_slot(self,vo: DatasetVO):
        menu=QMenu()
        menu.setCursor(QtCore.Qt.PointingHandCursor)
        menu.addAction(self.JSON)
        menu.addAction(self.PASCAL_VOC)
        # menu.addAction(self.TENSORFLOW_OBJECT_DETECTION)
        # menu.addAction(self.YOLO)
        action=menu.exec_(QCursor.pos())
        if action:

            selected_folder=str(QFileDialog.getExistingDirectory(None,"select the folder"))
            if selected_folder:
                action_text=action.text()

                @work_exception
                def do_work():
                    results=self._annot_dao.fetch_all_by_dataset(vo.id)
                    return results,None

                @gui_exception
                def done_work(result):
                    data,error=result
                    if error:
                        raise error
                    images=itertools.groupby(data,lambda x: x["image"])
                    if action_text == self.JSON:
                        self.annotations2json(images,selected_folder)
                    elif action_text == self.PASCAL_VOC:
                        self.annotations2pascal(images,selected_folder)

                    GUIUtilities.show_info_message("Annotations exported successfully","Done")

                worker=Worker(do_work)
                worker.signals.result.connect(done_work)
                self.thread_pool.start(worker)

    @gui_exception
    def import_annot_action_slot(self,dataset_vo: DatasetVO):
        menu=QMenu()
        menu.setCursor(QtCore.Qt.PointingHandCursor)
        menu.addAction(self.PASCAL_VOC)
        action=menu.exec_(QCursor.pos())
        if action:
            action_text=action.text()
            if action_text == self.PASCAL_VOC:
                colors = ColorUtilities.rainbow_gradient(1000)["hex"]
                files=GUIUtilities.select_files(".xml","Select the annotations files")
                if len(files) > 0:
                    @work_exception
                    def do_work():
                        annotations = []
                        for xml_file in files:
                            tree=ET.parse(xml_file)
                            root=tree.getroot()
                            objects=root.findall('object')
                            image_path=root.find('path').text
                            image_vo=self._ds_dao.find_by_path(dataset_vo.id,image_path)
                            if image_vo:
                                for roi in objects:
                                    label_name = roi.find('name').text
                                    label_vo = self._labels_dao.find_by_name(dataset_vo.id,label_name)
                                    if label_vo is None:
                                        label_vo = LabelVO()
                                        label_vo.name = label_name
                                        label_vo.dataset = dataset_vo.id
                                        label_vo.color = colors[random.randint(0, len(colors))]
                                        label_vo = self._labels_dao.save(label_vo)
                                    box = roi.find("bndbox")
                                    if box:
                                        x1 = int(box.find('xmin').text)
                                        y1 = int(box.find('ymin').text)
                                        x2 = int(box.find('xmax').text)
                                        y2 = int(box.find('ymax').text)
                                        box=AnnotaVO()
                                        box.label= label_vo.id
                                        box.entry=image_vo.id
                                        box.kind="box"
                                        box.points=",".join(map(str,[x1,y1,x2,y2]))
                                        annotations.append(box)
                        if len(annotations) > 0:
                            self._annot_dao.save(dataset_vo.id, annotations)
                        return annotations, None

                    @gui_exception
                    def done_work(result):
                        data,error=result
                        if error:
                            raise error
                        if len(data) > 0:
                            GUIUtilities.show_info_message("Annotations imported successfully",
                                                           "Import annotations status")
                        else:
                            GUIUtilities.show_info_message("No annotations found", "Import annotations status")

                    worker=Worker(do_work)
                    worker.signals.result.connect(done_work)
                    self.thread_pool.start(worker)
