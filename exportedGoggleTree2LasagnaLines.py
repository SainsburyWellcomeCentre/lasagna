#!/usr/bin/python
"""
This function accepts a csv file produced by exportGogglePoints.m
Each row of the csv file produced by that function is in this format:
nodeId,parentID,z position,x position,y position

This file imports this file and turns it into a format suitable
for plotting in lasagna. i.e. into a line series format:
line series #, z, x, y
Where each line series is one segment from the tree. This is 
produced using tree.findSegments, which returns all unique segments 
such that only nodes at the end of each segment are duplicated. 

Processed text is dumped to standard output by default unless
the user specifies otherwise with -q

Example:
1. Plot and don't dump data to screen
exportedGoggleTree2LasagnaLines.py -pqf ./ingredients/exampleTreeDump.csv 

2. Dump data to text file and don't plot
exportedGoggleTree2LasagnaLines.py -f ./ingredients/exampleTreeDump.csv  > /tmp/dumpedTree.csv

"""




import sys
import os
from tree import Tree, importData

#Parse command-line input arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-f", help="File name to load")
parser.add_argument("-p", help="Optionally plot tree", action="store_true")
parser.add_argument("-q", help="Quiet - do not dump processed tree to standard output", action="store_true")

args = parser.parse_args()

fname = args.f
doPlot = args.p
quiet = args.q


if fname == None:
    print "Please supply a file name to convert. e.g.:\nexportedGoggleTree2LasagnaLines.py -f myFile.csv\n"
    sys.exit(0)



#Get the data out of the tree
if os.path.exists(fname) == False:
    print 'Can not find ' + fname
    sys.exit(0)


dataTree = importData(fname,headerLine=['id','parent','z','x','y']) 

#Get the unique segments of each tree
paths=[]
for thisSegment in dataTree.findSegments():
    paths.append(thisSegment)


def dataFromPath(tree,path):
    """
    Get the data from the tree given a path.
    """
    x=[]
    y=[]
    z=[]
    for thisNode in path:
        if thisNode==0:
            continue
        z.append(tree.nodes[thisNode].data['z'])
        x.append(tree.nodes[thisNode].data['x'])
        y.append(tree.nodes[thisNode].data['y'])


    return (z,x,y)


#Show paths in standard output
if not quiet:
    ii=0
    for thisPath in paths:
        data = dataFromPath(dataTree,thisPath)
        for jj in range(len(data[0])):
            print "%d,%d,%d,%d" % (ii,data[0][jj],data[1][jj],data[2][jj])
        ii += 1



#-------------------------------------------------
#Optionally plot
if not doPlot:
    sys.exit(0)

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np


#Set up the window
app = QtGui.QApplication([])
mw = QtGui.QMainWindow()
mw.resize(800,800)

view = pg.GraphicsLayoutWidget()  # GraphicsView with GraphicsLayout inserted by default
mw.setCentralWidget(view)
mw.show()
mw.setWindowTitle('Neurite Tree')


#view 1
w1 = view.addPlot()
pathItem = []
for thisPath in paths:
    pathItem.append( pg.PlotDataItem(size=10, pen='w', symbol='o', symbolSize=2, brush=pg.mkBrush(255, 255, 255, 120)) )
    data = dataFromPath(dataTree,thisPath);
    pathItem[-1].setData(x=data[0], y=data[1])
    w1.addItem(pathItem[-1])


#view 2
w2 = view.addPlot()
pathItem = []
for thisPath in paths:
    pathItem.append( pg.PlotDataItem(size=10, pen='w', symbol='o', symbolSize=2, brush=pg.mkBrush(255, 255, 255, 120)) )
    data = dataFromPath(dataTree,thisPath)
    pathItem[-1].setData(x=data[0], y=data[2])
    w2.addItem(pathItem[-1])


#view 3
view.nextRow()
w3 = view.addPlot()
pathItem = []
for thisPath in paths:
    pathItem.append( pg.PlotDataItem(size=10, pen='w', symbol='o', symbolSize=2, brush=pg.mkBrush(255, 255, 255, 120)) )
    data = dataFromPath(dataTree,thisPath)
    pathItem[-1].setData(x=data[1], y=data[2])
    w3.addItem(pathItem[-1])



## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


