#/*##########################################################################
# Copyright (C) 2004-2014 V.A. Sole, European Synchrotron Radiation Facility
#
# This file is part of the PyMca X-ray Fluorescence Toolkit developed at
# the ESRF by the Software group.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
__author__ = "V.A. Sole - ESRF Data Analysis"
__contact__ = "sole@esrf.fr"
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
import sys
import numpy
from PyMca5.PyMcaGui import PyMcaQt as qt
if hasattr(qt, "QString"):
    QString = qt.QString
else:
    QString = str
from PyMca5.PyMcaGui.plotting.PyMca_Icons import IconDict
from PyMca5.PyMcaGui.plotting import MaskImageWidget
from . import ScanWindow

class StackPluginResultsWindow(MaskImageWidget.MaskImageWidget):
    def __init__(self, *var, **kw):
        ddict = {}
        ddict['usetab'] = kw.get("usetab",True)
        ddict['aspect'] = kw.get("aspect",True)
        ddict.update(kw)
        ddict['standalonesave'] = False
        MaskImageWidget.MaskImageWidget.__init__(self, *var, **ddict) 
        self.slider = qt.QSlider(self)
        self.slider.setOrientation(qt.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)

        if ddict['usetab']:
            # The 1D graph
            self.spectrumGraph = ScanWindow.ScanWindow(self)
            self.mainTab.addTab(self.spectrumGraph, "VECTORS")
        
        self.mainLayout.addWidget(self.slider)
        self.slider.valueChanged[int].connect(self._showImage)

        self.imageList = None
        self.spectrumList = None
        self.spectrumNames = None
        self.spectrumGraphTitles = None
        standalonesave = kw.get("standalonesave", True)
        if standalonesave:
            self.graphWidget.saveToolButton.clicked.connect(\
                                         self._saveToolButtonSignal)
            self._saveMenu = qt.QMenu()
            self._saveMenu.addAction(QString("Image Data"),
                                     self.saveImageList)
            self._saveMenu.addAction(QString("Standard Graphics"),
                                     self.graphWidget._saveIconSignal)
            self._saveMenu.addAction(QString("Matplotlib") ,
                             self._saveMatplotlibImage)
        self.multiplyIcon = qt.QIcon(qt.QPixmap(IconDict["swapsign"]))
        infotext = "Multiply image by -1"
        self.multiplyButton = self.graphWidget._addToolButton(\
                                        self.multiplyIcon,
                                        self._multiplyIconChecked,
                                        infotext,
                                        toggle = False,
                                        position = 12)

    def sizeHint(self):
        return qt.QSize(400, 400)

    def _multiplyIconChecked(self):
        if self.imageList is None:
            return
        index = self.slider.value()
        self.imageList[index] *= -1
        if self.spectrumList is not None:
            self.spectrumList[index] *= -1

        self._showImage(index)

    def _showImage(self, index):
        if len(self.imageList):
            self.showImage(index, moveslider=False)
        if self.spectrumList is not None:
            legend = self.spectrumNames[index]
            x = self.xValues[index]
            y = self.spectrumList[index]
            self.spectrumGraph.addCurve(x, y, legend, replace=True)
            if self.spectrumGraphTitles is not None:
                self.spectrumGraph.setGraphTitle(self.spectrumGraphTitles[index])
                
            
    def showImage(self, index=0, moveslider=True):
        if self.imageList is None:
            return
        if len(self.imageList) == 0:
            return
        # first the title to update any related selection curve legend
        self.graphWidget.graph.setGraphTitle(self.imageNames[index])
        self.setImageData(self.imageList[index])
        if moveslider:
            self.slider.setValue(index)

    def setStackPluginResults(self, images, spectra=None,
                   image_names = None, spectra_names = None,
                   xvalues=None, spectra_titles=None):
        self.spectrumList = spectra
        if type(images) == type([]):
            self.imageList = images
            if image_names is None:
                self.imageNames = []
                for i in range(nimages):
                    self.imageNames.append("Image %02d" % i)
            else:
                self.imageNames = image_names
        elif len(images.shape) == 3:
            nimages = images.shape[0]
            self.imageList = [0] * nimages
            for i in range(nimages):
                self.imageList[i] = images[i,:]
                if 0:
                    #leave the data as they originally come
                    if self.imageList[i].max() < 0:
                        self.imageList[i] *= -1
                        if self.spectrumList is not None:
                            self.spectrumList [i] *= -1
            if image_names is None:
                self.imageNames = []
                for i in range(nimages):
                    self.imageNames.append("Image %02d" % i)
            else:
                self.imageNames = image_names
                
        if self.imageList is not None:
            self.slider.setMaximum(len(self.imageList)-1)
            self.showImage(0)
        else:
            self.slider.setMaximum(0)

        if self.spectrumList is not None:
            if spectra_names is None:
                self.spectrumNames = []
                for i in range(nimages):
                    self.spectrumNames.append("Spectrum %02d" % i)
            else:
                self.spectrumNames = spectra_names
            if xvalues is None:
                self.xValues = []
                for i in range(nimages):
                    self.xValues.append(numpy.arange(len(self.spectrumList[0])))
            else:
                self.xValues = xValues
            self.spectrumGraphTitles = spectra_titles
            legend = self.spectrumNames[0]
            x = self.xValues[0]
            y = self.spectrumList[0]
            self.spectrumGraph.addCurve(x, y, legend, replace=True)
            if self.spectrumGraphTitles is not None:
                self.spectrumGraph.setGraphTitle(self.spectrumGraphTitles[0])
            
        self.slider.setValue(0)


    def saveImageList(self, filename=None, imagelist=None, labels=None):
        if self.imageList is None:
            return
        labels = []
        for i in range(len(self.imageList)):
            labels.append(self.imageNames[i].replace(" ","_"))
        return MaskImageWidget.MaskImageWidget.saveImageList(self,
                                                             imagelist=self.imageList,
                                                             labels=labels)
    def setImageList(self, imagelist):
        self.imageList = imagelist
        self.spectrumList = None
        if imagelist is not None:
            self.slider.setMaximum(len(self.imageList)-1)
            self.showImage(0)
            

def test():
    app = qt.QApplication([])
    app.lastWindowClosed.connect(app.quit)

    container = StackPluginResultsWindow()
    data = numpy.arange(20000)
    data.shape = 2, 100, 100
    data[1, 0:100,0:50] = 100
    container.setStackPluginResults(data, spectra=[numpy.arange(100.), numpy.arange(100.)+10],
                                image_names=["I1", "I2"], spectra_names=["V1", "V2"])
    container.show()
    def theSlot(ddict):
        print(ddict['event'])

    container.sigMaskImageWidgetSignal.connect(theSlot)
    app.exec_()

if __name__ == "__main__":
    import numpy
    test()
        
