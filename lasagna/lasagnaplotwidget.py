"""
A simple subclass of PlotWidget to add a lasagna viewbox in Qt Designer
"""

from pyqtgraph import PlotWidget
from lasagna.lasagna_viewBox import lasagna_viewBox


class LasagnaPlotWidget(PlotWidget):
    def __init__(self, *args, **kwargs):
        if 'viewBox' not in kwargs.keys():
            kwargs['viewBox'] = lasagna_viewBox()
        super(LasagnaPlotWidget, self).__init__(*args, **kwargs)
