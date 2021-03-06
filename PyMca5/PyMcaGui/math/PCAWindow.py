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

import numpy
from PyMca5.PyMcaGui import PyMcaQt as qt
from PyMca5.PyMcaGui import PyMca_Icons
IconDict = PyMca_Icons.IconDict
from PyMca5.PyMcaGui import MaskImageWidget
from PyMca5.PyMcaGui import ScanWindow
from PyMca5.PyMcaMath.mva import PCAModule

if hasattr(qt, "QString"):
    QString = qt.QString
else:
    QString = str

MDP = PCAModule.MDP
MATPLOTLIB = MaskImageWidget.MATPLOTLIB
QTVERSION = MaskImageWidget.QTVERSION


class PCAParametersDialog(qt.QDialog):
    def __init__(self, parent=None, options=[1, 2, 3, 4, 5, 10],
                 regions=False):
        qt.QDialog.__init__(self, parent)
        if QTVERSION < '4.0.0':
            self.setCaption("PCA Configuration Dialog")
        else:
            self.setWindowTitle("PCA Configuration Dialog")
        self.mainLayout = qt.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(11, 11, 11, 11)
        self.mainLayout.setSpacing(0)

        self.methodOptions = qt.QGroupBox(self)
        self.methodOptions.setTitle('PCA Method to use')
        self.methods = ['Covariance', 'Expectation Max.',
                        'Cov. Multiple Arrays']
        self.functions = [PCAModule.numpyPCA,
                          PCAModule.expectationMaximizationPCA,
                          PCAModule.multipleArrayPCA]
        self.methodOptions.mainLayout = qt.QGridLayout(self.methodOptions)
        self.methodOptions.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.methodOptions.mainLayout.setSpacing(2)
        #this does not seem to bring any advantage
        if 0:
            self.methods.append("Covariance Numpy")
            self.functions.append(PCAModule.numpyPCA)
        if MDP:
            #self.methods.append("MDP (PCA + ICA)")
            self.methods.append("MDP (SVD float32)")
            self.methods.append("MDP (SVD float64)")
            self.methods.append("MDP ICA (float32)")
            self.methods.append("MDP ICA (float64)")
            self.functions.append(PCAModule.mdpPCASVDFloat32)
            self.functions.append(PCAModule.mdpPCASVDFloat64)
            self.functions.append(PCAModule.mdpICAFloat32)
            self.functions.append(PCAModule.mdpICAFloat64)
        self.buttonGroup = qt.QButtonGroup(self.methodOptions)
        i = 0
        for item in self.methods:
            rButton = qt.QRadioButton(self.methodOptions)
            self.methodOptions.mainLayout.addWidget(rButton, 0, i)
            #self.l.setAlignment(rButton, qt.Qt.AlignHCenter)
            if i == 1:
                rButton.setChecked(True)
            rButton.setText(item)
            self.buttonGroup.addButton(rButton)
            self.buttonGroup.setId(rButton, i)
            i += 1
        self.buttonGroup.buttonPressed[int].connect(self._slot)

        self.mainLayout.addWidget(self.methodOptions)

        #built in speed options
        self.speedOptions = qt.QGroupBox(self)
        self.speedOptions.setTitle("Speed Options")
        self.speedOptions.mainLayout = qt.QGridLayout(self.speedOptions)
        self.speedOptions.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.speedOptions.mainLayout.setSpacing(2)
        labelPC = qt.QLabel(self)
        labelPC.setText("Number of PC:")
        self.nPC = qt.QSpinBox(self.speedOptions)
        self.nPC.setMinimum(0)
        self.nPC.setValue(10)
        self.nPC.setMaximum(40)

        self.binningLabel = qt.QLabel(self.speedOptions)
        self.binningLabel.setText("Spectral Binning:")
        self.binningCombo = qt.QComboBox(self.speedOptions)
        for option in options:
            self.binningCombo.addItem("%d" % option)
        self.speedOptions.mainLayout.addWidget(labelPC, 0, 0)
        self.speedOptions.mainLayout.addWidget(self.nPC, 0, 1)
        #self.speedOptions.mainLayout.addWidget(qt.HorizontalSpacer(self), 0, 2)
        self.speedOptions.mainLayout.addWidget(self.binningLabel, 1, 0)
        self.speedOptions.mainLayout.addWidget(self.binningCombo, 1, 1)
        self.binningCombo.setEnabled(False)
        self.binningCombo.activated[int].connect( \
                     self._updatePlotFromBinningCombo)
        if regions:
            self.__regions = True
            self.__addRegionsWidget()
        else:
            self.__regions = False
            #the optional plot
            self.scanWindow = None

        #the OK button
        hbox = qt.QWidget(self)
        hboxLayout = qt.QHBoxLayout(hbox)
        hboxLayout.setContentsMargins(0, 0, 0, 0)
        hboxLayout.setSpacing(0)
        self.okButton = qt.QPushButton(hbox)
        self.okButton.setText("Accept")
        self.okButton.setAutoDefault(False)
        hboxLayout.addWidget(qt.HorizontalSpacer(hbox))
        hboxLayout.addWidget(self.okButton)
        hboxLayout.addWidget(qt.HorizontalSpacer(hbox))
        self.mainLayout.addWidget(self.speedOptions)
        if regions:
            self.mainLayout.addWidget(self.regionsWidget)
        self.mainLayout.addWidget(hbox)
        if self.scanWindow is not None:
            self.mainLayout.addWidget(self.scanWindow)

        self.okButton.clicked[()].connect(self.accept)

    def __addRegionsWidget(self):
        #Region handling
        self.regionsWidget = RegionsWidget(self)
        self.regionsWidget.setEnabled(False)
        self.regionsWidget.sigRegionsWidgetSignal.connect( \
            self.regionsWidgetSlot)
        #the plot
        self.scanWindow = ScanWindow.ScanWindow(self)
        self.scanWindow.sigPlotSignal.connect(self._graphSlot)
        if not self.__regions:
            #I am adding after instantiation
            self.mainLayout.insertWidget(2,self.regionsWidget)
            self.mainLayout.addWidget(self.scanWindow)
        self.__regions = True

    def regionsWidgetSlot(self, ddict):
        fromValue = ddict['from']
        toValue   = ddict['to']
        self.graph = self.scanWindow
        self.graph.clearMarkers()
        self.graph.insertXMarker(fromValue,
                                  'From',
                                   label='From',
                                   color='blue',
                                   draggable=True)
        self.graph.insertXMarker(toValue,
                                 'To', label = 'To',
                                  color='blue',
                                  draggable=True)
        self.graph.replot() 

    def _graphSlot(self, ddict):
        if ddict['event'] == "markerMoved":
            marker = ddict['label']
            value = ddict['x']
            signal = False
            if marker == "From":
                self.regionsWidget.fromLine.setText("%f" % value)
            elif marker == "To":
                self.regionsWidget.toLine.setText("%f" % value)
            else:
                signal = True
            self.regionsWidget._editingSlot(signal=signal)

    def _slot(self, index):
        button = self.buttonGroup.button(index)
        button.setChecked(True)
        self.binningLabel.setText("Spectral Binning:")
        if index != 2:
            self.binningCombo.setEnabled(True)
        else:
            self.binningCombo.setEnabled(False)
        if self.__regions:
            if index < 3:
                self.regionsWidget.setEnabled(False)
            else:
                self.regionsWidget.setEnabled(True)
        return

    def setSpectrum(self, x, y, legend=None):
        if self.scanWindow is None:
            self.__addRegionsWidget()
        if legend is None:
            legend = "Current Active Spectrum"
        if not isinstance(x, numpy.ndarray):
            x = numpy.array(x)
            y = numpy.array(y)

        self._x = x
        self._y = y
        self.regionsWidget.setLimits(x.min(), x.max())
        self._legend = legend
        self.updatePlot()

    # value unused, but received with the Qt signal
    def _updatePlotFromBinningCombo(self, value):
        if self.scanWindow is None:
            return
        self.updatePlot()

    def updatePlot(self):
        binning = int(self.binningCombo.currentText())
        x = self._x * 1.0
        y = self._y * 1.0
        x.shape = 1, -1
        y.shape = 1, -1
        r, c = x.shape
        x.shape = r, c / binning, binning
        y.shape = r, c / binning, binning
        x = x.sum(axis=-1) / binning
        y = y.sum(axis=-1)
        x.shape = -1
        y.shape = -1
        self._binnedX = x
        self._binnedY = y
        self.scanWindow.newCurve(x, y, self._legend, replace=True)

    def setParameters(self, ddict):
        if 'options' in ddict:
            self.binningCombo.clear()
            for option in ddict['options']:
                self.binningCombo.addItem("%d" % option)
        if 'binning' in ddict:
            option = "%d" % ddict['binning']
            for i in range(self.binningCombo.count()):
                if str(self.binningCombo.itemText(i)) == option:
                    self.binningCombo.setCurrentIndex(i)
        if 'npc' in ddict:
            self.nPC.setValue(ddict['npc'])
        if 'method' in ddict:
            self.buttonGroup.buttons()[ddict['method']].setChecked(True)
            if ddict['method'] != 2:
                self.binningCombo.setEnabled(True)
            else:
                self.binningCombo.setEnabled(False)
        return

    def getParameters(self):
        ddict = {}
        ddict['binning'] = int(self.binningCombo.currentText())
        ddict['npc'] = self.nPC.value()
        i = self.buttonGroup.checkedId()
        ddict['method'] = i
        ddict['methodlabel'] = self.methods[i]
        ddict['function'] = self.functions[i]
        mask = None
        if self.__regions:
            regions = self.regionsWidget.getRegions()
            if not len(regions):
                mask = None
            else:
                mask = numpy.zeros(self._binnedX.shape, numpy.int32)
                for region in regions:
                    mask[(self._binnedX >= region[0]) *\
                         (self._binnedX <= region[1])] = 1
        ddict['mask'] = mask
        return ddict


class RegionsWidget(qt.QGroupBox):
    sigRegionsWidgetSignal = qt.pyqtSignal(object)
    def __init__(self, parent=None, nregions=10, limits=[0.0, 1000.]):
        qt.QGroupBox.__init__(self, parent)
        self.setTitle('Spectral Regions')
        self.mainLayout = qt.QGridLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(2)
        if nregions % 2:
            nregions += 1
        self.nRegions = nregions
        self.regionList = []
        self.__limits = [limits[0], limits[1]]
        # Nice hint -> What about:
        # self.regionList.extend([[limits[0], limits[1]] * self.nRegions)
        # instead of this loop with the useless i?
        for i in range(self.nRegions):
            self.regionList.append([limits[0], limits[1]])
        self.nRegionsLabel = qt.QLabel(self)
        self.nRegionsLabel.setText("Number of Regions:")
        self.nRegionsSpinBox = qt.QSpinBox(self)
        self.nRegionsSpinBox.setMinimum(0)
        self.nRegionsSpinBox.setValue(0)
        self.nRegionsSpinBox.setMaximum(self.nRegions)
        self.mainLayout.addWidget(self.nRegionsLabel, 0, 0)
        self.mainLayout.addWidget(self.nRegionsSpinBox, 0, 1)
        self.nRegionsSpinBox.valueChanged[int].connect(self._regionsChanged)

        self.currentRegionLabel = qt.QLabel(self)
        self.currentRegionLabel.setText("Current Region:")
        self.currentRegionSpinBox = qt.QSpinBox(self)
        self.currentRegionSpinBox.setMinimum(1)
        self.currentRegionSpinBox.setValue(1)
        self.currentRegionSpinBox.setMaximum(1)
        self.mainLayout.addWidget(self.currentRegionLabel, 0, 2)
        self.mainLayout.addWidget(self.currentRegionSpinBox, 0, 3)
        self.currentRegionSpinBox.valueChanged[int].connect(self._currentRegionChanged)

        label = qt.QLabel(self)
        label.setText("From:")
        self.fromLine = qt.QLineEdit(self)
        self.fromLine.setText("%f" % limits[0])
        self.fromLine._v = qt.QDoubleValidator(self.fromLine)
        self.fromLine.setValidator(self.fromLine._v)
        self.mainLayout.addWidget(label, 0, 4)
        self.mainLayout.addWidget(self.fromLine, 0, 5)
        self.fromLine.editingFinished[()].connect(self._editingSlot)

        label = qt.QLabel(self)
        label.setText("To:")
        self.toLine = qt.QLineEdit(self)
        self.toLine.setText("%f" % limits[1])
        self.toLine._v = qt.QDoubleValidator(self.toLine)
        self.toLine.setValidator(self.toLine._v)
        self.mainLayout.addWidget(label, 0, 6)
        self.mainLayout.addWidget(self.toLine, 0, 7)
        self.toLine.editingFinished[()].connect(self._editingSlot)
        self._regionsChanged(0)

    def setLimits(self, xmin, xmax):
        for i in range(len(self.regionList)):
            self.regionList[i][0] = max(self.regionList[i][0], xmin)
            self.regionList[i][1] = min(self.regionList[i][1], xmax)
        self.__limits = [xmin, xmax]
        current = self.currentRegionSpinBox.value()
        self._currentRegionChanged(current)

    def _regionsChanged(self, value):
        if value == 0:
            self.toLine.setDisabled(True)
            self.fromLine.setDisabled(True)
            self.currentRegionSpinBox.setDisabled(True)
        else:
            current = self.currentRegionSpinBox.value()
            self.currentRegionSpinBox.setMaximum(value)
            self.toLine.setDisabled(False)
            self.fromLine.setDisabled(False)
            self.currentRegionSpinBox.setDisabled(False)
            if current > value:
                self.currentRegionSpinBox.setValue(value)
                self._currentRegionChanged(value)

    def _currentRegionChanged(self, value):
        fromValue, toValue = self.regionList[value - 1]
        self.fromLine.setText("%f" % fromValue)
        self.toLine.setText("%f" % toValue)
        self.mySignal()

    def _editingSlot(self, signal=True):
        current = self.currentRegionSpinBox.value() - 1
        self.regionList[current][0] = float(str(self.fromLine.text()))
        self.regionList[current][1] = float(str(self.toLine.text()))
        if self.regionList[current][0] < self.__limits[0]:
            self.regionList[current][0] = self.__limits[0]
        if self.regionList[current][1] > self.__limits[1]:
            self.regionList[current][1] = self.__limits[1]
        if signal:
            self.mySignal()

    def mySignal(self):
        current = self.currentRegionSpinBox.value() - 1
        ddict={}
        ddict['event'] = 'regionChanged'
        ddict['from'] = self.regionList[current][0]
        ddict['to'] = self.regionList[current][1]
        self.sigRegionsWidgetSignal.emit(ddict)

    def getRegions(self):
        nRegions = self.nRegionsSpinBox.value()
        regions = []
        if nRegions > 0:
            for i in range(nRegions):
                regions.append(self.regionList[i])
        return regions


class PCAWindow(MaskImageWidget.MaskImageWidget):
    def __init__(self, *var, **kw):
        ddict = {}
        ddict['usetab'] = True
        ddict.update(kw)
        ddict['standalonesave'] = False
        MaskImageWidget.MaskImageWidget.__init__(self, *var, **ddict) 
        self.slider = qt.QSlider(self)
        self.slider.setOrientation(qt.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)

        # The 1D graph
        self.vectorGraph = ScanWindow.ScanWindow(self)
        self.mainTab.addTab(self.vectorGraph, "VECTORS")

        self.mainLayout.addWidget(self.slider)
        self.slider.valueChanged[int].connect(self._showImage)

        self.imageList = None
        self.imageNames=None
        self.eigenValues = None
        self.eigenVectors = None
        self.vectorNames = None
        self.vectorGraphTitles = None
        standalonesave = kw.get("standalonesave", True)
        if standalonesave:
            self.graphWidget.saveToolButton.clicked[()].connect( \
                         self._saveToolButtonSignal)
            self._saveMenu = qt.QMenu()
            self._saveMenu.addAction(QString("Image Data"),
                                     self.saveImageList)
            self._saveMenu.addAction(QString("Standard Graphics"),
                                     self.graphWidget._saveIconSignal)
            if MATPLOTLIB:
                self._saveMenu.addAction(QString("Matplotlib") ,
                                             self._saveMatplotlibImage)
        self.multiplyIcon = qt.QIcon(qt.QPixmap(IconDict["swapsign"]))
        infotext = "Multiply image by -1"
        self.multiplyButton = self.graphWidget._addToolButton(\
                                        self.multiplyIcon,
                                        self._multiplyIconChecked,
                                        infotext,
                                        toggle=False,
                                        position=12)

    def sizeHint(self):
        return qt.QSize(400, 400)

    def _multiplyIconChecked(self):
        if self.imageList is None:
            return
        index = self.slider.value()
        self.imageList[index] *= -1
        if self.eigenVectors is not None:
            self.eigenVectors[index] *= -1

        self._showImage(index)

    def _showImage(self, index):
        if len(self.imageList):
            self.showImage(index, moveslider=False)
        if self.eigenVectors is not None:
            legend = self.vectorNames[index]
            y = self.eigenVectors[index]
            self.vectorGraph.newCurve(range(len(y)), y, legend, replace=True)
            if self.vectorGraphTitles is not None:
                self.vectorGraph.graph.setTitle(self.vectorGraphTitles[index])

    def showImage(self, index=0, moveslider=True):
        if self.imageList is None:
            return
        if len(self.imageList) == 0:
            return
        self.setImageData(self.imageList[index])
        self.graphWidget.graph.setGraphTitle(self.imageNames[index])
        if moveslider:
            self.slider.setValue(index)

    def setPCAData(self, images, eigenvalues=None, eigenvectors=None,
                   imagenames=None, vectornames=None):
        self.eigenValues = eigenvalues
        self.eigenVectors = eigenvectors
        if type(images) == type([]):
            self.imageList = images
        elif len(images.shape) == 3:
            nimages = images.shape[0]
            self.imageList = [0] * nimages
            for i in range(nimages):
                self.imageList[i] = images[i, :]
                if self.imageList[i].max() < 0:
                    self.imageList[i] *= -1
                    if self.eigenVectors is not None:
                        self.eigenVectors[i] *= -1
            if imagenames is None:
                self.imageNames = []
                for i in range(nimages):
                    self.imageNames.append("Eigenimage %02d" % i)
            else:
                self.imageNames = imagenames

        if self.imageList is not None:
            self.slider.setMaximum(len(self.imageList) - 1)
            self.showImage(0)
        else:
            self.slider.setMaximum(0)

        if self.eigenVectors is not None:
            if vectornames is None:
                self.vectorNames = []
                for i in range(nimages):
                    self.vectorNames.append("Component %02d" % i)
            else:
                self.vectorNames = vectornames
            legend = self.vectorNames[0]
            y = self.eigenVectors[0]
            self.vectorGraph.newCurve(range(len(y)), y, legend, replace=True)

        self.slider.setValue(0)

    def saveImageList(self, filename=None, imagelist=None, labels=None):
        if self.imageList is None:
            return
        labels = []
        for i in range(len(self.imageList)):
            labels.append(self.imageNames[i].replace(" ", "_"))
        return MaskImageWidget.MaskImageWidget.saveImageList(self,
                                                             imagelist=self.imageList,
                                                             labels=labels)

    def setImageList(self, imagelist):
        self.imageList = imagelist
        self.eigenValues = None
        self.eigenVectors = None
        if imagelist is not None:
            self.slider.setMaximum(len(self.imageList) - 1)
            self.showImage(0)


def test2():
    app = qt.QApplication([])
    app.lastWindowClosed.connect(app.quit)
    dialog = PCAParametersDialog()
    dialog.setParameters({'options': [1,3,5,7,9], 'method': 1, 'npc': 8,
                          'binning': 3})
    dialog.setModal(True)
    ret = dialog.exec_()
    if ret:
        dialog.close()
        print(dialog.getParameters())


def test():
    app = qt.QApplication([])
    app.lastWindowClosed.connect(app.quit)
    container = PCAWindow()
    data = numpy.arange(20000)
    data.shape = 2, 100, 100
    data[1, 0:100, 0:50] = 100
    container.setPCAData(data, eigenvectors=[numpy.arange(100.),
                                             numpy.arange(100.) + 10],
                         imagenames=["I1", "I2"], vectornames=["V1", "V2"])
    container.show()

    def theSlot(ddict):
        print(ddict['event'])

    container.sigMaskImageWidgetSignal.connect(theSlot)
    app.exec_()

if __name__ == "__main__":
    test()

