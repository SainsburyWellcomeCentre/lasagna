#!/usr/bin/python
"""
This function accepts a csv file produced by exportGogglePoints.m
Each row of the csv file produced by that function is in this format:
nodeId,parentID,z position,x position,y position

This file imports this file and turns it into a format suitable
for plotting in lasagna. i.e. into a line series format:
line series #, z, x, y
This is not done very efficiently right now, but it works.
The algorithm just finds the path from each leaf to the root node. 

Processed text is dumped to standard output by default unless
the user specifies otherwise with -q
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


dataTree = importData(fname,headerLine=['id','parent','x','y','z'])

#Get the paths from each leaf back to the root. 
#This is the brute-force method of plotting the tree
paths=[]
for thisLeaf in dataTree.findLeaves():
    paths.append(dataTree.pathToRoot(thisLeaf))


def dataFromPath(tree,path):
    """
    Get the data from the tree given a path.
    TODO: make more efficient as we're over-plotting a lot here. 
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


    return (x,y,z)


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


