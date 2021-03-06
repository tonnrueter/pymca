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
import os

from . import PlotWidget
from PyMca5.PyMcaGraph.backends.MatplotlibBackend \
                    import MatplotlibBackend as backend
from .. import PyMcaQt as qt
from .PyMca_Icons import IconDict
from . import PyMcaPrintPreview
from PyMca5.PyMcaCore import PyMcaDirs

QTVERSION = qt.qVersion()
DEBUG = 0

class RGBCorrelatorGraph(qt.QWidget):
    sigProfileSignal = qt.pyqtSignal(object)

    def __init__(self, parent = None, selection=False, aspect=True,
                 colormap=False,
                 imageicons=False, standalonesave=True, standalonezoom=True,
                 profileselection=False, polygon=False):
        qt.QWidget.__init__(self, parent)
        self.mainLayout = qt.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self._keepDataAspectRatioFlag = False
        self._buildToolBar(selection, colormap, imageicons,
                           standalonesave,
                           standalonezoom=standalonezoom,
                           profileselection=profileselection,
                           aspect=aspect,
                           polygon=polygon)
        self.graph = PlotWidget.PlotWidget(self, backend=backend, aspect=aspect)
        self.graph.setGraphXLabel("Column")
        self.graph.setGraphYLabel("Row")
        self.graph.setYAxisAutoScale(True)
        self.graph.setXAxisAutoScale(True)
        if profileselection:
            if len(self._pickerSelectionButtons):
                self.graph.sigPlotSignal.connect(\
                    self._graphPolygonSignalReceived)
                self._pickerSelectionWidthValue.valueChanged[int].connect( \
                             self.setPickerSelectionWith)
        
        self.saveDirectory = os.getcwd()
        self.mainLayout.addWidget(self.graph)
        self.printPreview = PyMcaPrintPreview.PyMcaPrintPreview(modal = 0)
        if DEBUG:
            print("printPreview id = %d" % id(self.printPreview))

    def sizeHint(self):
        return qt.QSize(1.5 * qt.QWidget.sizeHint(self).width(),
                        qt.QWidget.sizeHint(self).height())

    def _buildToolBar(self, selection=False, colormap=False,
                      imageicons=False, standalonesave=True,
                      standalonezoom=True, profileselection=False,
                      aspect=False, polygon=False):
        self.solidCircleIcon = qt.QIcon(qt.QPixmap(IconDict["solidcircle"]))
        self.solidEllipseIcon = qt.QIcon(qt.QPixmap(IconDict["solidellipse"]))
        self.colormapIcon   = qt.QIcon(qt.QPixmap(IconDict["colormap"]))
        self.selectionIcon = qt.QIcon(qt.QPixmap(IconDict["normal"]))
        self.zoomResetIcon = qt.QIcon(qt.QPixmap(IconDict["zoomreset"]))
        self.polygonIcon = qt.QIcon(qt.QPixmap(IconDict["polygon"]))
        self.printIcon	= qt.QIcon(qt.QPixmap(IconDict["fileprint"]))
        self.saveIcon	= qt.QIcon(qt.QPixmap(IconDict["filesave"]))            
        self.xAutoIcon	= qt.QIcon(qt.QPixmap(IconDict["xauto"]))
        self.yAutoIcon	= qt.QIcon(qt.QPixmap(IconDict["yauto"]))
        self.hFlipIcon	= qt.QIcon(qt.QPixmap(IconDict["gioconda16mirror"]))
        self.imageIcon     = qt.QIcon(qt.QPixmap(IconDict["image"]))
        self.eraseSelectionIcon = qt.QIcon(qt.QPixmap(IconDict["eraseselect"]))
        self.rectSelectionIcon  = qt.QIcon(qt.QPixmap(IconDict["boxselect"]))
        self.brushSelectionIcon = qt.QIcon(qt.QPixmap(IconDict["brushselect"]))
        self.brushIcon          = qt.QIcon(qt.QPixmap(IconDict["brush"]))
        self.additionalIcon     = qt.QIcon(qt.QPixmap(IconDict["additionalselect"]))
        self.hLineIcon     = qt.QIcon(qt.QPixmap(IconDict["horizontal"]))
        self.vLineIcon     = qt.QIcon(qt.QPixmap(IconDict["vertical"]))
        self.lineIcon     = qt.QIcon(qt.QPixmap(IconDict["diagonal"]))

        self.toolBar = qt.QWidget(self)
        self.toolBarLayout = qt.QHBoxLayout(self.toolBar)
        self.toolBarLayout.setContentsMargins(0, 0, 0, 0)
        self.toolBarLayout.setSpacing(0)
        self.mainLayout.addWidget(self.toolBar)
        #Autoscale
        if standalonezoom:
            tb = self._addToolButton(self.zoomResetIcon,
                            self._zoomReset,
                            'Auto-Scale the Graph')
        else:
            tb = self._addToolButton(self.zoomResetIcon,
                            None,
                            'Auto-Scale the Graph')
        self.zoomResetToolButton = tb
        #y Autoscale
        tb = self._addToolButton(self.yAutoIcon,
                            self._yAutoScaleToggle,
                            'Toggle Autoscale Y Axis (On/Off)',
                            toggle = True, state=True)
        tb.setDown(True)

        self.yAutoScaleToolButton = tb
        tb.setDown(True)

        #x Autoscale
        tb = self._addToolButton(self.xAutoIcon,
                            self._xAutoScaleToggle,
                            'Toggle Autoscale X Axis (On/Off)',
                            toggle = True, state=True)
        self.xAutoScaleToolButton = tb
        tb.setDown(True)

        #Aspect ratio
        if aspect:
            self.aspectButton = self._addToolButton(self.solidCircleIcon,
                                self._aspectButtonSignal,
                                'Keep data aspect ratio',
                                toggle = False)
            self.aspectButton.setChecked(False)

        #colormap
        if colormap:
            tb = self._addToolButton(self.colormapIcon,
                                     None,
                                    'Change Colormap')
            self.colormapToolButton = tb

        #flip
        tb = self._addToolButton(self.hFlipIcon,
                                 None,
                                 'Flip Horizontal')
        self.hFlipToolButton = tb


        #save
        if standalonesave:
            tb = self._addToolButton(self.saveIcon,
                                 self._saveIconSignal,
                                 'Save Graph')
        else:
            tb = self._addToolButton(self.saveIcon,
                                 None,
                                 'Save')
        self.saveToolButton = tb

        #Selection
        if selection:
            tb = self._addToolButton(self.selectionIcon,
                                None,
                                'Toggle Selection Mode',
                                toggle = True,
                                state = False)
            tb.setDown(False)
            self.selectionToolButton = tb
        #image selection icons
        if imageicons:
            tb = self._addToolButton(self.imageIcon,
                                     None,
                                     'Reset')
            self.imageToolButton = tb

            tb = self._addToolButton(self.eraseSelectionIcon,
                                     None,
                                     'Erase Selection')
            self.eraseSelectionToolButton = tb

            tb = self._addToolButton(self.rectSelectionIcon,
                                     None,
                                     'Rectangular Selection')
            self.rectSelectionToolButton = tb

            tb = self._addToolButton(self.brushSelectionIcon,
                                     None,
                                     'Brush Selection')
            self.brushSelectionToolButton = tb


            tb = self._addToolButton(self.brushIcon,
                                     None,
                                     'Select Brush')
            self.brushToolButton = tb

            if polygon:
                tb = self._addToolButton(self.polygonIcon,
                                     None,
                        'Polygon selection\nRight click to finish')
                self.polygonSelectionToolButton = tb

            tb = self._addToolButton(self.additionalIcon,
                                     None,
                                     'Additional Selections Menu')
            self.additionalSelectionToolButton = tb            
        else:
            self.imageToolButton = None
        #picker selection
        self._pickerSelectionButtons = []
        if profileselection:
            self._profileSelection = True
            self._polygonSelection = False
            self._pickerSelectionButtons = []
            if self._profileSelection:
                tb = self._addToolButton(self.hLineIcon,
                                     self._hLineProfileClicked,
                                     'Horizontal Profile Selection',
                                     toggle=True,
                                     state=False)
                self.hLineProfileButton = tb
                self._pickerSelectionButtons.append(tb)
    
                tb = self._addToolButton(self.vLineIcon,
                                     self._vLineProfileClicked,
                                     'Vertical Profile Selection',
                                     toggle=True,
                                     state=False)
                self.vLineProfileButton = tb
                self._pickerSelectionButtons.append(tb)

                tb = self._addToolButton(self.lineIcon,
                                     self._lineProfileClicked,
                                     'Line Profile Selection',
                                     toggle=True,
                                     state=False)
                self.lineProfileButton = tb
                self._pickerSelectionButtons.append(tb)

                self._pickerSelectionWidthLabel = qt.QLabel(self.toolBar)
                self._pickerSelectionWidthLabel.setText("W:")
                self.toolBar.layout().addWidget(self._pickerSelectionWidthLabel)
                self._pickerSelectionWidthValue = qt.QSpinBox(self.toolBar)
                self._pickerSelectionWidthValue.setMinimum(1)
                self._pickerSelectionWidthValue.setMaximum(1000)
                self.toolBar.layout().addWidget(self._pickerSelectionWidthValue)
                #tb = self._addToolButton(None,
                #                     self._lineProfileClicked,
                #                     'Line Profile Selection',
                #                     toggle=True,
                #                     state=False)
                #tb.setText = "W:"
                #self.lineWidthProfileButton = tb
                #self._pickerSelectionButtons.append(tb)
            if self._polygonSelection:
                print("Polygon selection not implemented yet")
        #hide profile selection buttons
        if imageicons:
            for button in self._pickerSelectionButtons:
                button.hide()

        self.infoWidget = qt.QWidget(self.toolBar)
        self.infoWidget.mainLayout = qt.QHBoxLayout(self.infoWidget)
        self.infoWidget.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.infoWidget.mainLayout.setSpacing(0)
        self.infoWidget.label = qt.QLabel(self.infoWidget)
        self.infoWidget.label.setText("X = ???? Y = ???? Z = ????")
        self.infoWidget.mainLayout.addWidget(self.infoWidget.label)
        self.toolBarLayout.addWidget(self.infoWidget)
        self.infoWidget.hide()

        self.toolBarLayout.addWidget(qt.HorizontalSpacer(self.toolBar))

        # ---print
        tb = self._addToolButton(self.printIcon,
                                 self.printGraph,
                                 'Prints the Graph')

    def _aspectButtonSignal(self):
        if DEBUG:
            print("_aspectButtonSignal")
        if self._keepDataAspectRatioFlag:
            self.keepDataAspectRatio(False)
        else:
            self.keepDataAspectRatio(True)

    def keepDataAspectRatio(self, flag=True):
        if flag:
            self._keepDataAspectRatioFlag = True
            self.aspectButton.setIcon(self.solidEllipseIcon)
            self.aspectButton.setToolTip("Set free data aspect ratio")
        else:
            self._keepDataAspectRatioFlag = False
            self.aspectButton.setIcon(self.solidCircleIcon)
            self.aspectButton.setToolTip("Keep data aspect ratio")
        self.graph.keepDataAspectRatio(self._keepDataAspectRatioFlag)

    def showInfo(self):
        self.infoWidget.show()

    def hideInfo(self):
        self.infoWidget.hide()

    def setInfoText(self, text):
        self.infoWidget.label.setText(text)

    def infoText(self):
        return self.infoWidget.label.text()

    def setXLabel(self, label="Column"):
        return self.graph.setGraphXLabel(label)

    def setYLabel(self, label="Row"):
        return self.graph.setGraphYLabel(label)

    def getXLabel(self):
        return self.graph.getGraphXLabel()

    def getYLabel(self):
        return self.graph.getGraphYLabel()

    def hideImageIcons(self):
        if self.imageToolButton is None:return
        self.imageToolButton.hide()
        self.eraseSelectionToolButton.hide()
        self.rectSelectionToolButton.hide()
        self.brushSelectionToolButton.hide()
        self.brushToolButton.hide()
        if hasattr(self, "polygonSelectionToolButton"):
            self.polygonSelectionToolButton.hide()
        self.additionalSelectionToolButton.hide()

    def showImageIcons(self):
        if self.imageToolButton is None:return
        self.imageToolButton.show()
        self.eraseSelectionToolButton.show()
        self.rectSelectionToolButton.show()
        self.brushSelectionToolButton.show()
        self.brushToolButton.show()
        if hasattr(self, "polygonSelectionToolButton"):
            self.polygonSelectionToolButton.show()
        self.additionalSelectionToolButton.show()

    def _hLineProfileClicked(self):
        for button in self._pickerSelectionButtons:
            if button != self.hLineProfileButton:
                button.setChecked(False)

        if self.hLineProfileButton.isChecked():
            self._setPickerSelectionMode("HORIZONTAL")
        else:
            self._setPickerSelectionMode(None)

    def _vLineProfileClicked(self):
        for button in self._pickerSelectionButtons:
            if button != self.vLineProfileButton:
                button.setChecked(False)
        if self.vLineProfileButton.isChecked():
            self._setPickerSelectionMode("VERTICAL")
        else:
            self._setPickerSelectionMode(None)

    def _lineProfileClicked(self):
        for button in self._pickerSelectionButtons:
            if button != self.lineProfileButton:
                button.setChecked(False)
        if self.lineProfileButton.isChecked():
            self._setPickerSelectionMode("LINE")
        else:
            self._setPickerSelectionMode(None)

    def setPickerSelectionWith(self, intValue):
        self._pickerSelectionWidthValue.setValue(intValue)
        #get the current mode
        mode = "NONE"
        for button in self._pickerSelectionButtons:
            if button.isChecked():
                if button == self.hLineProfileButton:
                    mode = "HORIZONTAL"
                elif button == self.vLineProfileButton:
                    mode = "VERTICAL"
                elif button == self.lineProfileButton:
                    mode = "LINE"        
        ddict = {}
        ddict['event'] = "profileWidthChanged"
        ddict['pixelwidth'] = self._pickerSelectionWidthValue.value()
        ddict['mode'] = mode
        self.sigProfileSignal.emit(ddict)

    def hideProfileSelectionIcons(self):
        if not len(self._pickerSelectionButtons):
            return
        for button in self._pickerSelectionButtons:
            button.setChecked(False)
            button.hide()
        self._pickerSelectionWidthLabel.hide()
        self._pickerSelectionWidthValue.hide()
        #self.graph.setPickerSelectionModeOff()
        self.graph.setDrawModeEnabled(False)

    def showProfileSelectionIcons(self):
        if not len(self._pickerSelectionButtons):
            return
        for button in self._pickerSelectionButtons:
            button.show()
        self._pickerSelectionWidthLabel.show()
        self._pickerSelectionWidthValue.show()

    def getPickerSelectionMode(self):
        if not len(self._pickerSelectionButtons):
            return None
        if self.hLineProfileButton.isChecked():
            return "HORIZONTAL"
        if self.vLineProfileButton.isChecked():
            return "VERTICAL"
        if self.lineProfileButton.isChecked():
            return "LINE"
        return None

    def _setPickerSelectionMode(self, mode=None):
        if mode is None:
            self.graph.setDrawModeEnabled(False)
            self.graph.setZoomModeEnabled(True)
        else:
            if mode == "HORIZONTAL":
                shape = "hline"
            elif mode == "VERTICAL":
                shape = "vline"
            else:
                shape = "line"
            self.graph.setZoomModeEnabled(False)
            self.graph.setDrawModeEnabled(True,
                                          shape=shape,
                                          label=mode)
        ddict = {}
        if mode is None:
            mode = "NONE"
        ddict['event'] = "profileModeChanged"
        ddict['mode'] = mode
        self.sigProfileSignal.emit(ddict)

    def _graphPolygonSignalReceived(self, ddict):
        if DEBUG:
            print("PolygonSignal Received")
            for key in ddict.keys():
                print(key, ddict[key])

        if ddict['event'] not in ['drawingProgress', 'drawingFinished']:
            return
        label = ddict['parameters']['label']
        if  label not in ['HORIZONTAL', 'VERTICAL', 'LINE']:
            return
        ddict['mode'] = label
        ddict['pixelwidth'] = self._pickerSelectionWidthValue.value()
        self.sigProfileSignal.emit(ddict)

    def _addToolButton(self, icon, action, tip, toggle=None, state=None, position=None):
        tb      = qt.QToolButton(self.toolBar)            
        if icon is not None:
            tb.setIcon(icon)
        tb.setToolTip(tip)
        if toggle is not None:
            if toggle:
                tb.setCheckable(1)
                if state is not None:
                    if state:
                        tb.setChecked(state)
                else:
                    tb.setChecked(False)
        if position is not None:
            self.toolBarLayout.insertWidget(position, tb)
        else:
            self.toolBarLayout.addWidget(tb)
        if action is not None:
            tb.clicked[()].connect(action)
        return tb

    def _zoomReset(self, replot=None):
        if DEBUG:
            print("_zoomReset")
        if replot is None:
            replot = True
        if self.graph is not None:
            self.graph.resetZoom()
            if replot:
                self.graph.replot()

    def _yAutoScaleToggle(self):
        if self.graph is not None:
            if self.graph.isYAxisAutoScale():
                self.graph.setYAxisAutoScale(False)
                self.yAutoScaleToolButton.setDown(False)
            else:
                self.graph.setYAxisAutoScale(True)
                self.yAutoScaleToolButton.setDown(True)
            
    def _xAutoScaleToggle(self):
        if self.graph is not None:
            if self.graph.isXAxisAutoScale():
                self.graph.setXAxisAutoScale(False)
                self.xAutoScaleToolButton.setDown(False)
            else:
                self.graph.setXAxisAutoScale(True)
                self.xAutoScaleToolButton.setDown(True)

    def _saveIconSignal(self):
        self.saveDirectory = PyMcaDirs.outputDir

        fileTypeList = ["Image *.png",
                        "Image *.jpg",
                        "ZoomedImage *.png",
                        "ZoomedImage *.jpg",
                        "Widget *.png",
                        "Widget *.jpg"]

        outfile = qt.QFileDialog(self)
        outfile.setModal(1)
        outfile.setWindowTitle("Output File Selection")
        if hasattr(qt, "QStringList"):
            strlist = qt.QStringList()
        else:
            strlist = []
        for f in fileTypeList:
            strlist.append(f)
        outfile.setFilters(strlist)
        outfile.setFileMode(outfile.AnyFile)
        outfile.setAcceptMode(qt.QFileDialog.AcceptSave)
        outfile.setDirectory(self.saveDirectory)
        ret = outfile.exec_()

        if not ret:
            return
        filterused = qt.safe_str(outfile.selectedFilter()).split()
        filetype = filterused[0]
        extension = filterused[1]

        outstr = qt.safe_str(outfile.selectedFiles()[0])

        try:            
            outputFile = os.path.basename(outstr)
        except:
            outputFile = outstr
        outputDir  = os.path.dirname(outstr)
        self.saveDirectory = outputDir
        PyMcaDirs.outputDir = outputDir

        #always overwrite for the time being
        if len(outputFile) < len(extension[1:]):
            outputFile += extension[1:]
        elif outputFile[-4:] != extension[1:]:
            outputFile += extension[1:]
        outputFile = os.path.join(outputDir, outputFile)
        if os.path.exists(outputFile):
            try:
                os.remove(outputFile)
            except:
                qt.QMessageBox.critical(self, "Save Error",
                                        "Cannot overwrite existing file")
                return

        if filetype.upper() == "IMAGE":
            self.saveGraphImage(outputFile, original = True)
        elif filetype.upper() == "ZOOMEDIMAGE":
            self.saveGraphImage(outputFile, original = False)
        else:
            self.saveGraphWidget(outputFile)

    def saveGraphImage(self, filename, original = False):
        format_ = filename[-3:].upper()
        if original:
            #This is the whole image, not the zoomed one ...
            pixmap = qt.QPixmap.fromImage(self.graph.plotImage.image)
        else:
            pixmap = qt.QPixmap.grabWidget(self.graph.canvas())
        if pixmap.save(filename, format_):
            return
        else:
            qt.QMessageBox.critical(self, "Save Error",
                                    "%s" % sys.exc_info()[1])
            return

    def saveGraphWidget(self, filename):
        format_ = filename[-3:].upper()
        pixmap = qt.QPixmap.grabWidget(self.graph)
        if pixmap.save(filename, format_):
            return
        else:
            qt.QMessageBox.critical(self, "Save Error", "%s" % sys.exc_info()[1])
            return

    def setSaveDirectory(self, wdir):
        if os.path.exists(wdir):
            self.saveDirectory = wdir
            return True
        else:
            return False

    def printGraph(self):
        pixmap = qt.QPixmap.grabWidget(self.graph.getWidgetHandle())
        self.printPreview.addPixmap(pixmap)
        if self.printPreview.isReady():
            if self.printPreview.isHidden():
                self.printPreview.show()
            self.printPreview.raise_()

    def selectColormap(self):
        qt.QMessageBox.information(self, "Open", "Not implemented (yet)")  


class MyQLabel(qt.QLabel):
    def __init__(self,parent=None,name=None,fl=0,bold=True, color= qt.Qt.red):
        qt.QLabel.__init__(self,parent)
        palette = self.palette()
        role = self.foregroundRole()
        palette.setColor(role,color)
        self.setPalette(palette)
        self.font().setBold(bold)

def test():
    app = qt.QApplication([])
    app.lastWindowClosed.connect(app.quit)

    container = RGBCorrelatorGraph()
    container.show()
    app.exec_()

if __name__ == "__main__":
    test()
        
