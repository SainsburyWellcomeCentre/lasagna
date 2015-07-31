
""" 
This class overrides the behavior of the parent ViewBox to all for scaling and translating 
of one or more linked axes
"""


import pyqtgraph as pg
import numpy as np
import pyqtgraph.functions as fn
from PyQt4 import QtCore, QtGui

class lasagna_viewBox(pg.ViewBox):
    mouseWheeled = QtCore.pyqtSignal(object, object) #Make a mouseWheeled signal

    def __init__(self, linkedAxis={}):
        super(lasagna_viewBox,self).__init__()

        """
        linkedAxis is a dictionary with the following structure:
        keys are ViewBoxes and their value is a dictionary with the following keys:
            linkX - link self's X axis to the key's 'x'  or 'y' axis or None (do not link)
            linkY - link self's Y axis to the key's 'x'  or 'y' axis or None (do not link)
            linkZoom  - link self's zoom with the key's zoom (True or False)
        """
        self.linkedAxis = linkedAxis #A list of ViewBox axes to link to 


    def wheelEvent(self, ev, axis=None):
        """
        Intercept pg.ViewBox.wheelEvent
        """
        self.onMouseWheeled(ev,axis)
        #The sigRangeChangedManually signal is defined in pg.ViewBox:  sigRangeChangedManually = QtCore.Signal(object)
        self.sigRangeChangedManually.emit(self.state['mouseEnabled']) 
        self.mouseWheeled.emit(ev, axis) #Then it emits a mouseWheeled signal


    def mouseDragEvent(self, ev, axis=None, linkX=False, linkY=False):
        """
        Intercept pg.ViewBox.mouseDragEvent
        """
        #Call the built-in mouseDragEvent
        pg.ViewBox.mouseDragEvent(self,ev,axis)

        if len(self.linkedAxis)==None:
            return

        for thisView in self.linkedAxis.keys():
            #Get the current view center in x and y
            vr = self.targetRect()

            x=None
            y=None

            if self.linkedAxis[thisView]['linkX']=='x':
                x = vr.center().x()

            if self.linkedAxis[thisView]['linkY']=='y':
                y = vr.center().y()

            if self.linkedAxis[thisView]['linkX']=='y':
                y = vr.center().x()

            if self.linkedAxis[thisView]['linkY']=='x':
                x = vr.center().y()

            self.centreOn(thisView,x,y)


    def centreOn(self,thisViewBox,x=None,y=None):
        """
        Centre thisViewBox on coordinates defined by x and y. 
        """
        vr = thisViewBox.targetRect()

        if x is not None:
            x = x-vr.center().x()
            x = vr.left()+x, vr.right()+x
        if y is not None:
            y = y-vr.center().y()
            y = vr.top()+y, vr.bottom()+y

        if x is not None or y is not None:
            thisViewBox.setRange(xRange=x, yRange=y, padding=0)


    def mouseClickEvent(self,ev):
        """
        Can be used to capture mouse clicks
        """
        pg.ViewBox.mouseClickEvent(self,ev)


    def onMouseWheeled(self, ev, axis):
        """
        Allows mouse wheel zoom on ctrl-click [currently]
        """
        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
            #Handle zoom (scaling with ctrl+mousewheel) 
            mask = np.array(self.state['mouseEnabled'], dtype=np.float)
 
            if axis is not None and axis >= 0 and axis < len(mask):
                mv = mask[axis]
                mask[:] = 0
                mask[axis] = mv

            s = ((mask * 0.02) + 1) ** (ev.delta() * self.state['wheelScaleFactor']) # actual scaling factor
            center = pg.Point(fn.invertQTransform(self.childGroup.transform()).map(ev.pos()))
            #center = ev.pos()
        
            self._resetTarget()
            self.scaleBy(s, center)
            self.sigRangeChangedManually.emit(self.state['mouseEnabled'])
            ev.accept()

            if len(self.linkedAxis)>0:
                for thisViewBox in self.linkedAxis:

                    if self.linkedAxis[thisViewBox]['linkZoom']==True: 
                        #Centre with the appropriate axes to avoid the views translating in horrible ways during zooming
                        #I don't know why I also need to call my centerOn() method, but at least this works
                        if self.linkedAxis[thisViewBox]['linkX']=='x' and self.linkedAxis[thisViewBox]['linkY']==None :
                            thisViewBox.scaleBy(s,x=center.x())
                            self.centreOn(thisViewBox,x=center.x())

                        if self.linkedAxis[thisViewBox]['linkY']=='y' and self.linkedAxis[thisViewBox]['linkX']==None :
                            thisViewBox.scaleBy(s,y=center.y())
                            self.centreOn(thisViewBox,y=center.y())

                        if self.linkedAxis[thisViewBox]['linkX']=='y' and self.linkedAxis[thisViewBox]['linkY']==None : 
                            thisViewBox.scaleBy(s,y=center.x())
                            self.centreOn(thisViewBox,y=center.x())

                        if self.linkedAxis[thisViewBox]['linkY']=='x' and self.linkedAxis[thisViewBox]['linkX']==None : 
                            thisViewBox.scaleBy(s,x=center.y())
                            self.centreOn(thisViewBox,x=center.y())

                        #The following two cases aren't used currently by Lasagna, but may be required in the future. 
                        #They haven't been tested yet. [28/07/15]
                        if self.linkedAxis[thisViewBox]['linkY']=='x' and self.linkedAxis[thisViewBox]['linkX']=='y' : 
                            thisViewBox.scaleBy(s,x=center.y(),y=center.x())
                            self.centreOn(thisViewBox,x=center.y(),y=center.x())

                        if self.linkedAxis[thisViewBox]['linkY']=='y' and self.linkedAxis[thisViewBox]['linkX']=='x' : 
                            thisViewBox.scaleBy(s,x=center.x(),y=center.y())
                            self.centreOn(thisViewBox,x=center.x(),y=center.y())
            
            return
    
        # Here is where we can put code to switch layer because this only
        # runs if wheel is rotated alone 
