import panta_rhei_path

import sys
import os
import logging
import datetime
import time
import io

import numpy as np

from argparse import ArgumentParser
from PyQt5 import QtWidgets, QtCore
from pathlib import Path

from panta_rhei.gui.blocked_signals import BlockedSignals
from panta_rhei.scripting import PRScriptingInterface
from panta_rhei.repository.image_array import ImageArray
from panta_rhei.repository.repository import Repository
from panta_rhei.image_io.image_loader import load_from_file
import threading

import gphoto2 as gp
from subprocess import Popen, PIPE, run
# this connects via ZMQ REQ/REP to running PR ImageViewer application
# PR SCripting Server must be activated in PR Viewer on the same host
pr = PRScriptingInterface()

from PIL import Image
import shutil
import zmq
import json
import csv
import signal
import concurrent.futures

__version__ = '0.2'

LOGLEVEL= { 'CRITICAL': logging.CRITICAL,
            'ERROR': logging.ERROR,
            'WARNING': logging.WARNING,
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG }

log = logging.getLogger()

class CameraDialog(QtWidgets.QWidget):


    def __init__(self, live, single):
        super().__init__()
        # this is the file path for monitored file handels
        self.live_name, self.live_path = live
        self.single_name, self.single_path = single
        self.isoSettings = ['Auto', '100', '125', '160', '200', '250', '320', '400', '500', '640', '800', '1000', '1250', '1600', '2000', '2500', '3200', '4000', '5000', '6400', '8000', '10000', '12800', '16000', '20000', '25000']
        self.shutterspeedSettings = ['bulb', '30', '25', '20', '15', '13', '10.3', '8', '6.3', '5', '4', '3.2', '2.5', '1.6', '1.3','1','0.8','0.6','0.5','0.4','0.3','1/4','1/5','1/6','1/8','1/10','1/13','1/15','1/20','1/25','1/30','1/40','1/50','1/60','1/80','1/100','1/125','1/160','1/200','1/250','1/320','1/400','1/500','1/640','1/800','1/1000','1/1250','1/1600','1/2000','1/2500','1/3200','1/4000']
        self.setup_ui()
        self.connect_ui()
        self.repo = Repository()
        if self.repo.connect():
            self.repo.get_all_names()
        else:
            log.error("Couldn't connect to Repository.")
        self.repo.connect()
        #self.watcher = FileWatcher(self.repo)
        #self.watcher.add_file(self.live_name, self.live_path)
        #self.watcher.add_file( self.single_name, self.single_path)
        #self.watcher.register_handler(self.copy_data)
        self.live = False
        self.hold_live = False
        self.single = False
        self.live_view = None
        self.single_view = None
        self.live_thread = threading.Thread(name="live_thread", target=self.stream)
        self.camera_init()
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:8888")

    def setup_ui(self):
        layout = QtWidgets.QGridLayout()
        self.isoBox = QtWidgets.QComboBox()
        self.isoBox.addItems(self.isoSettings)
        self.shutterspeedBox = QtWidgets.QComboBox()
        self.shutterspeedBox.addItems(self.shutterspeedSettings)
        self.shutterspeedBox.setCurrentIndex(33)
        self.imageCount = QtWidgets.QSpinBox()
        self.imageCount.setRange(1, 100)
        self.imageCount.setSingleStep(1)
        self.live_pb = QtWidgets.QPushButton('Live')
        self.live_pb.setCheckable(True)
        self.single_pb = QtWidgets.QPushButton('Acquire')
        self.single_pb.setCheckable(True)

        layout.addWidget(QtWidgets.QLabel('ISO'),0,0)
        layout.addWidget(self.isoBox,0,1)
        layout.addWidget(QtWidgets.QLabel('Shutter Speed'),0,2)
        layout.addWidget(self.shutterspeedBox,0,3)
        layout.addWidget(QtWidgets.QLabel('#Image'), 0, 4)
        layout.addWidget(self.imageCount, 0, 5)
        layout.addWidget(self.live_pb,1,0,1,2)
        layout.addWidget(self.single_pb,1,4,1,2)
        self.setLayout(layout)


    def connect_ui(self):
        self.live_pb.toggled.connect(self.on_toggle_live)
        self.single_pb.toggled.connect(self.on_toggle_single)
        self.isoBox.currentIndexChanged.connect(self.update_iso)
        self.shutterspeedBox.currentIndexChanged.connect(self.update_shutter_speed)

    def camera_init(self):
        self.camera = gp.Camera()
        self.camera.init()
        self.config = self.camera.get_config()
        OK, self.shutterspeed = gp.gp_widget_get_child_by_name(self.config, 'shutterspeed')
        OK, self.iso = gp.gp_widget_get_child_by_name(self.config, 'iso')
        self.update_iso()
        self.update_shutter_speed()

    def update_shutter_speed(self):
        if self.live:
            self.stop_live()
            self.hold_live = True
        try:
            self.shutterspeed.set_value(self.shutterspeedSettings[self.shutterspeedBox.currentIndex()])
            self.camera.set_config(self.config)
            print("shutterspeed is updated to", self.shutterspeed.get_value())
        except Exception:
            print("Failed to change shutter speed, there was IO process in camera, please retry")
            QtWidgets.QMessageBox.question(self,'I/O in progress', 'Failed to change shutter speed, there was IO process in camera, please retry', QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        if self.hold_live:
            self.hold_live = False
            self.start_live()

    def update_iso(self):
        if self.live:
            self.stop_live()
            self.hold_live = True
        try:
            self.iso.set_value(self.isoSettings[self.isoBox.currentIndex()])
            self.camera.set_config(self.config)
            print("iso is updated to", self.iso.get_value())
        except Exception:
            print("Failed to change ISO, there was IO process in camera, please retry")
            QtWidgets.QMessageBox.question(self,'I/O in progress', 'Failed to change ISO, there was IO process in camera, please retry', QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        if self.hold_live:
            self.hold_live = False
            self.start_live()

    def copy_data(self, name, fpath):
        # adapt to actual format of image data from gphoto2
        # img: ndarray  meta: {'key': value, ...}
        print(fpath)
        img, meta = load_from_file(fpath)
        dtype = img.dtype
        shape = img.shape
        # checkout shared memeory object by name
        nda = self.repo.new_or_update(name, shape, dtype)
        # copy data to shared memory
        np.copyto(nda, img)
        # submit the update repository
        self.repo.commit(nda, meta)

    @QtCore.pyqtSlot(bool)
    def on_toggle_live(self, checked):
        if checked:
            self.start_live()
        else:
            self.stop_live()

    def start_live(self):
        if not self.live:
            self.live = True
            if not self.live_thread.is_alive():
                self.live_thread.start()


    def stream(self):
        self.live_view = pr.display_image(self.live_name)
        while self.live:
            capture = self.camera.capture_preview()
            filedata = capture.get_data_and_size()
            data = memoryview(filedata)
            self.copy_data(self.live_name, io.BytesIO(data))

    def stop_live(self):
        self.live = False
        self.live_thread.join(0)
        self.live_thread = threading.Thread(name="live_thread", target=self.stream)
        time.sleep(1)


    @QtCore.pyqtSlot(bool)
    def on_toggle_single(self, checked):
        if not checked:
            with BlockedSignals(self.single_pb):
                self.single_pb.setChecked(True)
        else:
            self.single = True
            if self.live:
                self.stop_live()
                self.hold_live = True
            if self.imageCount.value() == 1:
                self.take_single()
            else:
                self.take_multiple(self.imageCount.value())

    @QtCore.pyqtSlot()
    def take_single(self):
        time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
        target = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')+'.jpg'
        try:
            file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE)
            camera_file = self.camera.file_get(
                file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
            camera_file.save(target)
            self.copy_data(self.single_name, target)
            pr.display_image(self.single_name)
            self.save_settings(time)
        except:
            print("Failed to take a picture, there was IO process in camera, please retry")
            QtWidgets.QMessageBox.question(self,'I/O in progress', 'Failed to take a picture, there was IO process in camera, please retry', QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        with BlockedSignals(self.single_pb):
            self.single_pb.setChecked(False)
        self.single = False
        if self.hold_live:
            self.hold_live = False
            self.start_live()

    def take_multiple(self, n):
        folderName = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
        os.mkdir(folderName)
        for i in range(n):
            file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE)
            target = os.path.join(folderName, file_path.name)
            print(target)
            camera_file = self.camera.file_get(
                file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
            camera_file.save(target)
        self.stack_image(folderName)
        shutil.rmtree(folderName)
        self.copy_data(self.single_name, folderName+'.npz')
        pr.display_image(self.single_name)
        self.save_settings(folderName)
        with BlockedSignals(self.single_pb):
            self.single_pb.setChecked(False)
        self.single = False
        if self.hold_live:
            self.hold_live = False
            self.start_live()


    def stack_image(self, directory):
        data = []
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            img = Image.open(f).convert('L')
            data.append(np.asarray(img))
        data = np.asarray(data)
        meta = [{'repo_id': '', 'type': 'Stack', 'ref_size': data[0].shape, 'filename': directory+'.npz'}]
        data_model = [{'type': 'Stack'}]
        kwargs = {}
        kwargs['data'] = data
        kwargs['meta'] = meta
        kwargs['data_model'] = data_model
        np.savez(directory, **kwargs)
    
    def receive_settings(self):
        self.socket.send_json(json.dumps({'request':'get'}))
        # Set a receive timeout (in milliseconds)
        self.socket.setsockopt(zmq.RCVTIMEO, 15000) 
        try:
            data = self.socket.recv_json()
            return data
        except zmq.error.Again:
            raise TimeoutError()

        return data
    
    def save_settings(self, filename):
        try:
            data = self.receive_settings()
        except TimeoutError:
            QtWidgets.QMessageBox.question(self,'Time Out', 'Time out when recieve microscope settings, please check NanoMi control software see if ZMQ server is enabled', QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            print("Time out when recieve microscope settings, please check NanoMi control software see if ZMQ server is enabled!")
            return -1
        dataDict = json.loads(data)
        write = []
        write.append(["Module", "SubModule","Variable Name", "Value"])
        for module in dataDict:
            if module == 'Stigmators' or module == 'Deflectors':
                for subModule in dataDict[module]:
                    for variable in dataDict[module][subModule]:
                        val = dataDict[module][subModule][variable]
                        write.append([module, subModule, variable, val])
            else:
                for variable in dataDict[module]:
                    val = dataDict[module][variable]
                    write.append([module, 'N/A', variable, val])
        with open(filename+'.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(write)
    def closeEvent(self,event):
        #generate a popup message box asking the user if they REALLY meant to shut down the software
        #note that unless they've saved variable presets etc, they would lose a lot of data if they accidentally shut down the program
        reply = QtWidgets.QMessageBox.question(self,'Closing?', 'Are you sure you want to shut down the program?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        #respond according to the user reply
        if reply == QtWidgets.QMessageBox.Yes:
            if self.live:
                self.stop_live()
            event.accept()
        else:
            event.ignore()

# def signal_handler(signum, frame):
#     raise Exception("Timed out!")


if __name__ == '__main__':

    parser = ArgumentParser(description='PR Interface for GPhoto2')
    parser.add_argument('--single', action="store", type=str, nargs=2, default=('Single','single.jpg'),
                        help='repository name and path for single acquisition data')
    parser.add_argument('--live', action="store", type=str, nargs=2, default=('Live', 'live.jpg'),
                        help='repository name and path for live acquisition data')
    parser.add_argument('--quite', action='store_true', help='suppress logging to console')
    parser.add_argument('--logfile', action='store', type=str, help='Log to file', default=None)
    parser.add_argument('--loglevel', action='store', choices=LOGLEVEL.keys(), default='INFO',
                        help='Select log level (default: INFO)')
    args = parser.parse_args()

    fmt = logging.Formatter('%(asctime)s %(levelname)s %(process)d#%(thread)d %(module)s:%(lineno)d %(message)s')
    std = logging.StreamHandler()

    log.setLevel(LOGLEVEL[args.loglevel])

    if not args.quite:
        std.setFormatter(fmt)
        log.addHandler(std)

    if args.logfile is not None:
        hdl = logging.FileHandler()
        hdl.setFormatter(fmt)
        log.addHandler(hdl)

    app  =  QtWidgets.QApplication(sys.argv)

    dialog = CameraDialog(live=args.live, single=args.single)
    dialog.show()

    sys.exit(app.exec_())
