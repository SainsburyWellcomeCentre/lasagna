#! /usr/bin/env python3


"""
Show coronal, transverse and saggital plots in different panels


Depends on:
vtk
pyqtgraph (0.9.10 and above 0.9.8 is known not to work)
numpy
tifffile
argparse
tempfile
urllib
"""

__author__ = "Rob Campbell"
__license__ = "GPL v3"
__maintainer__ = "Rob Campbell"


import os
import sys
import argparse

import pyqtgraph as pg
from PyQt5 import QtGui

# Parse command-line input arguments
parser = argparse.ArgumentParser()
parser.add_argument("-D", help="Load demo images", action="store_true")  # Store true makes it zero by default
parser.add_argument("-im", nargs='+', help="file name(s) of image stacks to load")
parser.add_argument("-S", nargs='+', help="file names of sparse points file(s) to load")
parser.add_argument("-L", nargs='+', help="file names of lines file(s) to load")
parser.add_argument("-T", nargs='+', help="file names of tree file(s) to load")
parser.add_argument("-C", help="start a ipython console", action='store_true')
parser.add_argument("-P", help="start plugin of this name. use string from plugins menu as the argument")
args = parser.parse_args()

PLUGIN_TO_START = args.P
SPARSE_POINTS_TO_LOAD = args.S
LINES_TO_LOAD = args.L
TREES_TO_LOAD = args.T

# Either load the demo stacks or a user-specified stacks
if args.D:
    import tempfile
    import urllib.request, urllib.parse, urllib.error
from lasagna.lasagna_object import Lasagna

    IM_STACK_FNAMES_TO_LOAD = [tempfile.gettempdir() + os.path.sep + 'reference.tiff',
                               tempfile.gettempdir() + os.path.sep + 'sample.tiff']

    loadUrl = 'http://mouse.vision/lasagna/'
    for fname in IM_STACK_FNAMES_TO_LOAD:
        if not os.path.exists(fname):
            url = loadUrl + fname.split(os.path.sep)[-1]
            print(('Downloading %s to %s' % (url, fname)))
            urllib.request.urlretrieve(url, fname)
else:
    IM_STACK_FNAMES_TO_LOAD = args.im


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Set up the figure window
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def main(imStackFnamesToLoad=None, sparsePointsToLoad=None, linesToLoad=None, pluginToStart=None, embedConsole=False):
    app = QtGui.QApplication([])

    tasty = Lasagna()
    tasty.app = app

    # Data from command line input if the user specified this
    if imStackFnamesToLoad is not None:
        for fname in imStackFnamesToLoad:
            print(("Loading stack " + fname))
            tasty.loadImageStack(fname)

    if sparsePointsToLoad is not None:
        for fname in sparsePointsToLoad:
            print(("Loading points " + fname))
            tasty.loadActions['sparse_point_reader'].showLoadDialog(fname)

    if linesToLoad is not None:
        for fname in linesToLoad:
            print(("Loading lines " + fname))
            tasty.loadActions['lines_reader'].showLoadDialog(fname)

    if TREES_TO_LOAD is not None:
        for fname in TREES_TO_LOAD:
            print(("Loading tree " + fname))
            tasty.loadActions['tree_reader'].showLoadDialog(fname)

    tasty.initialiseAxes()

    if pluginToStart is not None:
        if pluginToStart in tasty.plugins:
            tasty.startPlugin(pluginToStart)
            tasty.pluginActions[pluginToStart].setChecked(True)
        else:
            print(("No plugin '%s': not starting" % pluginToStart))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Link slots to signals
    # connect views to the mouseMoved slot. After connection this runs in the background.
    proxies = []
    for i in range(3):
        proxy = pg.SignalProxy(tasty.axes2D[i].view.scene().sigMouseMoved, rateLimit=30, slot=tasty.mouseMoved)
        proxy.axisID = i  # this is picked up the mouseMoved slot
        proxies.append(proxy)

        proxy = pg.SignalProxy(tasty.axes2D[i].view.getViewBox().mouseClicked, rateLimit=30, slot=tasty.axisClicked)
        proxy.axisID = i  # this is picked up the mouseMoved slot
        proxies.append(proxy)

    if embedConsole:
        from IPython import embed
        embed()

    sys.exit(app.exec_())


# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    main(imStackFnamesToLoad=IM_STACK_FNAMES_TO_LOAD, sparsePointsToLoad=SPARSE_POINTS_TO_LOAD, linesToLoad=LINES_TO_LOAD,
         pluginToStart=PLUGIN_TO_START, embedConsole=args.C)
