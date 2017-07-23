
#install sudo apt-get install tesseract-ocr
# import the necessary packages
from PIL import Image
import pytesseract
import argparse
import cv2
import os
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic 


#OCR App class
class OCRApp(QMainWindow):
   def __init__(self):
      QMainWindow.__init__(self)
      self.ui = uic.loadUi("ui.ui", self)
      self.ui.load_image.clicked.connect(self.open)
      self.image = None
      self.ui.label.setStyleSheet("border: 1px solid black")

      self.rubberband = QRubberBand(QRubberBand.Rectangle, self)
      #self.ui.image.setMouseTracking(True)
      #self.ui.image.installEventFilter(self)
      self.ui.label.setMouseTracking(True)
      self.ui.label.installEventFilter(self)
      #self.ui.label.setScaledContents(True)
      self.ui.label.setAlignment(Qt.AlignTop)
    
   def open(self):
      filename = QFileDialog.getOpenFileName(self, 'Select file')
      print filename
      self.image = cv2.imread(str(filename))
      #print self.image[100,100]
      frame = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
      image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
      self.ui.label.setPixmap(QPixmap.fromImage(image))

   def imageTotext(self,crop_opencv):
      gray = cv2.cvtColor(crop_opencv,cv2.COLOR_BGR2GRAY)
      #remove noise
      gary = cv2.medianBlur(gray,3)
      crop = Image.fromarray(gray)
      text = pytesseract.image_to_string(crop)
      return text
      

   #Event Filter 
   def eventFilter(self, source, event):
      if (event.type() == QEvent.MouseButtonPress and source is self.ui.label):
                 print "mouse press"
                 self.origin = self.mapFromGlobal(event.globalPos())
                 self.left_top_point = event.pos()
                 print self.origin
                 self.rubberband.setGeometry(QRect(self.origin, QSize()))
                 self.rubberband.show()
      elif (event.type() == QEvent.MouseMove and source is self.ui.label):
                 if self.rubberband.isVisible():
                         self.rubberband.setGeometry(QRect(self.origin, self.mapFromGlobal(event.globalPos())).normalized())
      elif (event.type() == QEvent.MouseButtonRelease and source is self.ui.label):
                 if self.rubberband.isVisible():
                         self.rubberband.hide()
                         rect = self.rubberband.geometry()
                         self.x1 = self.left_top_point.x()
                         self.y1 = self.left_top_point.y()
                         width = rect.width()
                         height  = rect.height()
                         self.x2 = self.x1 + width
                         self.y2 = self.y1 + height
		         print self.x1,self.y1,self.x2,self.y2
                         if width >= 10 and height >= 10 and self.image is not None:
                                self.text = ""
                         	self.crop = self.image[self.y1:self.y2, self.x1:self.x2]
                         	cv2.imwrite("crop.png",self.crop)
                                self.text = self.imageTotext(self.crop)
				self.ui.text_label.appendPlainText(str(self.text))
                 else:
                         self.rubberband.hide()
      else:
                 return 0
      return QWidget.eventFilter(self, source, event)

app = QApplication(sys.argv)
mainWindow = OCRApp()
mainWindow.show()
sys.exit(app.exec_())
