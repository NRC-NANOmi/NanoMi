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

# TODO:
# - use gphoto2 api for live and single acquisition
#

__version__ = '0.2'

LOGLEVEL= { 'CRITICAL': logging.CRITICAL,
            'ERROR': logging.ERROR,
            'WARNING': logging.WARNING,
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG }

log = logging.getLogger()
        
class CameraDialog(QtWidgets.QWidget):
    
    dtypes = { 'uint8': np.uint8,
               'int8': np.int8,
               'uint16': np.uint16,
               'int16': np.int16,
               'uint32': np.uint32,
               'int32': np.int32 }
    
    def __init__(self, live, single):
        super().__init__()
        # this is the file path for monitored file handels
        self.live_name, self.live_path = live
        self.single_name, self.single_path = single
        # dtype of ndarray finally copied to repository
        self.dtype = list(self.dtypes.keys())[0]
        # expose/repetition time for image acquistion
        # (at the moment it is not claer if exposure time is meaningful here)
        self.tacq = 500
        log.info('Image acquistion via GPhoto2 Vers. %s', __version__)
        log.info('Name and path (Live): %s %s', *live)
        log.info('Name and path (Acquire): %s %s', *single)
        self.setup_ui()
        self.update_ui()
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
        
    def setup_ui(self):
        layout = QtWidgets.QGridLayout()
        self.tacq_sb = QtWidgets.QSpinBox()
        # adjust range and stepsize for exposure/repetition time here
        self.tacq_sb.setRange(100, 1000)
        self.tacq_sb.setSingleStep(100)
        self.tacq_sb.setSuffix(' ms')
        self.dtype_cb = QtWidgets.QComboBox()
        self.dtype_cb.addItems(list(self.dtypes.keys()))
        self.live_pb = QtWidgets.QPushButton('Live')
        self.live_pb.setCheckable(True)
        self.single_pb = QtWidgets.QPushButton('Acquire')
        self.single_pb.setCheckable(True)
        layout.addWidget(QtWidgets.QLabel('T(acq):'),0,0)
        layout.addWidget(self.tacq_sb,0,1)
        layout.addWidget(QtWidgets.QLabel('DType:'),0,2)
        layout.addWidget(self.dtype_cb,0,3)
        layout.addWidget(self.live_pb,1,0,1,2)
        layout.addWidget(self.single_pb,1,2,1,2)
        self.setLayout(layout)

    def update_ui(self):
        with BlockedSignals(self.tacq_sb) as tacq_sb,\
             BlockedSignals(self.dtype_cb) as dtype_cb:
            tacq_sb.setValue(self.tacq)
            idx = dtype_cb.findText(self.dtype)
            if idx>=0:
                dtype_cb.setCurrentIndex(idx)

    def set_tacq(self, value=None):
        self.tacq = self.tacq_sb.value()

    def set_dtype(self, value=None):
        self.dtype = self.dtype_cb.currentText()
                
    def connect_ui(self):
        self.tacq_sb.valueChanged.connect(self.set_tacq)
        self.dtype_cb.currentIndexChanged.connect(self.set_dtype)
        self.live_pb.toggled.connect(self.on_toggle_live)
        self.single_pb.toggled.connect(self.on_toggle_single)
        
    def copy_data(self, name, fpath):
        # adapt to actual format of image data from gphoto2
        # img: ndarray  meta: {'key': value, ...}
        print(fpath)
        img, meta = load_from_file(fpath)
        # use dtype as selected in combobox for output (optional)
        img = img.astype(self.dtypes[self.dtype])
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
        camera = gp.Camera()
        camera.init()
        self.live_view = pr.display_image(self.live_name)
        while self.live:
            capture = camera.capture_preview()
            filedata = capture.get_data_and_size()
            data = memoryview(filedata)
            self.copy_data(self.live_name, io.BytesIO(data))
        camera.exit()
        
    def stop_live(self):
        self.live = False
        self.live_thread.join(0)
        self.live_thread = threading.Thread(name="live_thread", target=self.stream)


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
            self.take_single()

    @QtCore.pyqtSlot()        
    def take_single(self):
        fileName = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')+'.jpg'
        run(['gphoto2', '--capture-image-and-download', '--filename='+fileName], input=b'y\n')
        self.copy_data(self.single_name, fileName)
        pr.display_image(self.single_name)
        with BlockedSignals(self.single_pb): 
            self.single_pb.setChecked(False)     
        self.single = False
        if self.hold_live:
            self.hold_live = False
            self.start_live()


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
