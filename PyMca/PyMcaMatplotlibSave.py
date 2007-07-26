import os
import numpy
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

DEBUG = 0

colordict = {}
colordict['blue']   = '#0000ff'
colordict['red']    = '#ff0000'
colordict['green']  = '#00ff00'
colordict['black']  = '#000000'
colordict['white']  = '#ffffff'
colordict['pink']   = '#ff66ff'
colordict['brown']  = '#a52a2a'
colordict['orange'] = '#ff9900'
colordict['violet'] = '#6600ff'
colordict['grey']   = '#808080'
colordict['yellow'] = '#ffff00'
colordict['darkgreen'] = 'g'
colordict['darkbrown'] = '#660000' 
colordict['magenta']   = 'm' 
colordict['cyan']      = 'c'
colordict['bluegreen'] = '#33ffff'
colorlist  = [colordict['black'],
              colordict['red'],
              colordict['blue'],
              colordict['green'],
              colordict['pink'],
              colordict['brown'],
              colordict['cyan'],
              colordict['orange'],
              colordict['violet'],
              colordict['bluegreen'],
              colordict['grey'],
              colordict['magenta'],
              colordict['darkgreen'],
              colordict['darkbrown'],
              colordict['yellow']]

class PyMcaMatplotlibSave:
    def __init__(self, size = (6,3),
                 logx = False,
                 logy = False,
                 legends = True,
                 bw = False):

        self.fig = Figure(figsize=size) #in inches
        self.canvas = FigureCanvas(self.fig)

        self._logX = logx
        self._logY = logy
        self._bw   = bw
        self._legend   = legends
        self._legendList = []
        self._dataCounter = 0

        if not legends:
            if self._logY:
                ax = self.fig.add_axes([.1, .15, .75, .8])
            else:
                ax = self.fig.add_axes([.15, .15, .75, .75])
        else:
            if self._logY:
                ax = self.fig.add_axes([.1, .15, .7, .8])
            else:
                ax = self.fig.add_axes([.15, .15, .7, .8])

        ax.set_axisbelow(True)

        self.ax = ax


        if self._logY:
            self._axFunction = ax.semilogy
        else:
            self._axFunction = ax.plot

        if self._bw:
            self.colorList = ['k']   #only black
            self.styleList = ['-', ':', '-.', '--']
            self.nColors   = 1
        else:
            self.colorList = colorlist
            self.styleList = ['-', '-.', ':']
            self.nColors   = len(colorlist)
        self.nStyles   = len(self.styleList)

        self.colorIndex = 0
        self.styleIndex = 0

        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
        self.limitsSet = False

    def setLimits(self, xmin, xmax, ymin, ymax):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.limitsSet = True


    def _filterData(self, x, y):
        index = numpy.flatnonzero((self.xmin <= x) & (x <= self.xmax))
        x = numpy.take(x, index)
        y = numpy.take(y, index)
        index = len(index)
        if index:
            index = numpy.flatnonzero((self.ymin <= y) & (y <= self.ymax))
            index = len(index)
        return index

    def _getColorAndStyle(self):
        color = self.colorList[self.colorIndex]
        style = self.styleList[self.styleIndex]
        self.colorIndex += 1
        if self.colorIndex >= self.nColors:
            self.colorIndex = 0
            self.styleIndex += 1
            if self.styleIndex >= self.nStyles:
                self.styleIndex = 0        
        return color, style

    def addDataToPlot(self, x, y, legend = None,
                      color = None,
                      linewidth = None,
                      linestyle = None, **kw):
        n = max(x.shape)
        if self.limitsSet is not None:
            n = self._filterData(x, y)
        if n == 0:
            #nothing to plot
            if DEBUG:
                print "nothing to plot"
            return
        style = None
        if color is None:
            color, style = self._getColorAndStyle()
        if linestyle is None:
            if style is None:
                style = '-'
        else:
            style = linestyle

        if linewidth is None:linewidth = 1.0
        self._axFunction( x, y, linestyle = style, color=color, linewidth = linewidth, **kw)
        self._dataCounter += 1
        if legend is None:
            #legend = "%02d" % self._dataCounter    #01, 02, 03, ...
            legend = "%c" % (96+self._dataCounter)  #a, b, c, ..
        self._legendList.append(legend)

    def setXLabel(self, label):
        self.ax.set_xlabel(label)

    def setYLabel(self, label):
        self.ax.set_ylabel(label)
        
    def plotLegends(self):
        if not self._legend:return
        if not len(self._legendList):return
        loc = (1.01, 0.0)
        labelsep = 0.015
        drawframe = True
        if len(self._legendList) > 14:
            drawframe = False
            loc = (1.05, -0.2)
            fontproperties = FontProperties(size=8)
        else:
            fontproperties = FontProperties(size=10)

        legend = self.ax.legend(self._legendList,
                                loc = loc,
                                prop = fontproperties,
                                labelsep = labelsep,
                                pad = 0.15)

        legend.draw_frame(drawframe)


    def saveFile(self, filename, format=None):
        if format is None:
            format = filename[-3:]

        if format.upper() not in ['EPS', 'PNG', 'SVG']:
            raise "Unknown format %s" % format

        if os.path.exists(filename):
            os.remove(filename)

        if self.limitsSet:
            self.ax.set_ylim(self.ymin, self.ymax)
            self.ax.set_xlim(self.xmin, self.xmax)

        self.canvas.print_figure(filename)
        return
        
if __name__ == "__main__":
    DEBUG = 1
    x = numpy.arange(1000.)
    y0 = x * 100 + 10.
    y1 = x * 110 + 20.
    y2 = x * 120 + 20.
    plot = PyMcaMatplotlibSave(logy=True)
    plot.setLimits(100, 900, 100*100, 700*100)
    plot.addDataToPlot(x, y0)
    plot.addDataToPlot(x, y1)
    plot.addDataToPlot(x, y2)
    plot.setXLabel('X Label')
    plot.setYLabel('Y Label')
    plot.plotLegends()
    plot.saveFile("myfile.png")

    