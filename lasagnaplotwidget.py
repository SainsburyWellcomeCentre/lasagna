"""A simple subclass of PlotWidget to add a lasagna viewbox

"""

from pyqtgraph import PlotWidget
from lasagna_viewBox import lasagna_viewBox

class LasagnaPlotWidget(PlotWidget):

    def __init__(self, *args, **kwargs):
        if not 'viewBox' in kwargs.keys():
            kwargs['viewBox']=lasagna_viewBox()
        super(LasagnaPlotWidget,self).__init__(*args, **kwargs)
