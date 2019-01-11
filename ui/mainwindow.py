# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

from PyQt5.QtCore import pyqtSlot,  QTimer
from PyQt5.QtWidgets import QMainWindow,  QFileDialog
from PyQt5.QtGui import QIcon, QPixmap,  QImage

from .Ui_mainwindow import Ui_MainWindow

import __init__
import demo
import cv2
import numpy as np

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        
        
    def openCamera(self):
        self.camera = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.runCamera) 
        self.timer.start(100)  
        
    @pyqtSlot()
    def runCamera(self):
        if self.camera.isOpened():
            rval , frame = self.camera.read()
            self.img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.label.setPixmap(QPixmap(self.convertMatToQImage(self.img)))
            
            detect = demo.demo(frame)
            detect = cv2.cvtColor(detect, cv2.COLOR_BGR2RGB)
            self.label_2.setPixmap(QPixmap(self.convertMatToQImage(detect)))
        else:
            rval = False
         


    def openFileNameDialog(self):
        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","JPG (*.jpg)", options=options)
        if fileName:
            img = cv2.imread(fileName)
            self.img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.label.setPixmap(QPixmap(self.convertMatToQImage(self.img)))
            print(fileName)
            
    
    def convertQImageToMat(self, qImg):
        '''  Converts a QImage into an opencv MAT format  '''

        qImg = qImg.convertToFormat(4)

        width = qImg.width()
        height = qImg.height()

        ptr = qImg.bits()
        ptr.setsize(qImg.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)  #  Copies the data
        return arr
    
    def convertMatToQImage(self,  cvImg):
        cvImg = cv2.resize(cvImg,(400, 400), interpolation=cv2.INTER_CUBIC )
        height, width, channel = cvImg.shape
        bytesPerLine = 3 * width
        qImg = QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888)
        return qImg

    @pyqtSlot()
    def on_pushButton_clicked(self):
        """
        Slot documentation goes here.
        """
        self.openFileNameDialog()
    
    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        """
        Slot documentation goes here.
        """
        detect = demo.demo(self.img)
        self.label.setPixmap(QPixmap(self.convertMatToQImage(detect)))
    
    @pyqtSlot()
    def on_openCamera_btn_clicked(self):
        """
        Slot documentation goes here.
        """
        self.openCamera()
