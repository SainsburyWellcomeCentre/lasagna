""" 
This class overrides the behavior of the parent ViewBox to handle operations for
for scaling and translating of one or more linked axes
"""


import pyqtgraph as pg
from PyQt5.QtWidgets import *
import numpy as np
import pyqtgraph.functions as fn
from PyQt5 import QtCore, QtWidgets
import platform


class lasagna_viewBox(pg.ViewBox):
    mouseWheeled = QtCore.pyqtSignal(object, object)  # Make a mouseWheeled signal
    # This fires when the user mouse-wheels without keyboard modifiers
    progressLayer = (QtCore.pyqtSignal())
    mouseClicked = QtCore.pyqtSignal(object)  # Make a mouseClicked signal

    def __init__(self, linkedAxis={}):
        super(lasagna_viewBox, self).__init__(enableMenu=False)

        """
        linkedAxis is a dictionary with the following structure:
        keys are ViewBoxes and their value is a dictionary with the following keys:
            linkX - link self's X axis to the key's 'x'  or 'y' axis or None (do not link)
            linkY - link self's Y axis to the key's 'x'  or 'y' axis or None (do not link)
            linkZoom  - link self's zoom with the key's zoom (True or False)
        """
        self.linkedAxis = linkedAxis  # A list of ViewBox axes to link to
        self.controlDrag = False

        # Flip stack in X/Y or the image flipped incorrectly
        self.invertY()

        # Define a custom signal to indicate when the user has created an event that will increment the displayed layer
        self.progressBy = 0

    def wheelEvent(self, ev, axis=None):
        """
        Intercept pg.ViewBox.wheelEvent
        """
        self.onMouseWheeled(ev, axis)
        # The sigRangeChangedManually signal is defined in pg.ViewBox:  sigRangeChangedManually = QtCore.Signal(object)
        self.sigRangeChangedManually.emit(self.state["mouseEnabled"])
        self.mouseWheeled.emit(ev, axis)  # Then it emits a mouseWheeled signal

    def mouseDragEvent(self, ev, axis=None, linkX=False, linkY=False):
        """
        Intercept pg.ViewBox.mouseDragEvent to provide linked panning
        across different axes
        """

        if len(self.linkedAxis) is None:
            return

        # Not zoom if the user right-drags, because this messes up stuff. Let's just do all zooming with the wheel
        if ev.button() & QtCore.Qt.RightButton:
            return

        # Do not drag and link displays if we are pressing the control key.
        # Instead, set the self.controlDrag boolean to True and bail out
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            self.controlDrag = True
            return
        else:
            self.controlDrag = False

        # Call the built-in mouseDragEvent
        pg.ViewBox.mouseDragEvent(self, ev, axis)

        # The following is use dby lasagna_axis.updateDisplayedSlices_2D to link the views
        for thisView in list(self.linkedAxis.keys()):
            # Get the current view center in x and y
            vr = self.targetRect()

            x = None
            y = None

            if self.linkedAxis[thisView]["linkX"] == "x":
                x = vr.center().x()

            if self.linkedAxis[thisView]["linkY"] == "y":
                y = vr.center().y()

            if self.linkedAxis[thisView]["linkX"] == "y":
                y = vr.center().x()

            if self.linkedAxis[thisView]["linkY"] == "x":
                x = vr.center().y()

            self.centreOn(thisView, x, y)
            thisView.scaleBy([1, 1])

    def centreOn(self, thisViewBox, x=None, y=None):
        """
        Centre thisViewBox on coordinates defined by x and y.
        """
        vr = thisViewBox.targetRect()

        if x is not None:
            x = x - vr.center().x()
            x = vr.left() + x, vr.right() + x
        if y is not None:
            y = y - vr.center().y()
            y = vr.top() + y, vr.bottom() + y

        if x is not None or y is not None:
            thisViewBox.setRange(xRange=x, yRange=y, padding=0)

    def mouseClickEvent(self, ev):
        """
        Can be used to capture mouse clicks
        """
        self.mouseClicked.emit(ev)  # just re-emit an event to hook plugins
        pg.ViewBox.mouseClickEvent(self, ev)

    def onMouseWheeled(self, ev, axis):
        """
        Allows mouse wheel zoom on ctrl-click [currently]
        """
        self.controlDrag = False  # TODO: hack that should not be needed
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier or (
            modifiers == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier)
        ):
            # Emit a signal when the wheel is rotated alone and return a positive or negative value in self.progressBy
            # that we can use to incremement the image layer in the current axes
            if ev.delta() > 0:
                self.progressBy = 1
            elif ev.delta() < 0:
                self.progressBy = -1
            else:
                self.progressBy = 0

            # this may be mouse-specific!
            self.progressBy = (self.progressBy * abs(ev.delta()) / 120)

            if modifiers == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
                # Allow faster scrolling if it was a shift+wheel
                self.progressBy = self.progressBy * 5

            self.progressLayer.emit()
        else:
            # Handle zoom (mousewheel with no keyboard modifier)
            mask = np.array(self.state["mouseEnabled"], dtype=np.float)

            if axis is not None and 0 <= axis < len(mask):
                mv = mask[axis]
                mask[:] = 0
                mask[axis] = mv

            # actual scaling factor
            s = ((mask * 0.02) + 1) ** (ev.delta() * self.state["wheelScaleFactor"])

            center = pg.Point(
                fn.invertQTransform(self.childGroup.transform()).map(ev.pos())
            )
            # center = ev.pos()

            self._resetTarget()
            self.scaleBy(s, center)
            self.sigRangeChangedManually.emit(self.state["mouseEnabled"])
            ev.accept()

            if len(self.linkedAxis) > 0:
                for thisViewBox in self.linkedAxis:

                    if self.linkedAxis[thisViewBox]["linkZoom"]:
                        # Centre with the appropriate axes to avoid the views translating in horrible ways during zooming
                        # I don't know why I also need to call my centerOn() method, but at least this works
                        if (
                            self.linkedAxis[thisViewBox]["linkX"] == "x"
                            and self.linkedAxis[thisViewBox]["linkY"] is None
                        ):
                            thisViewBox.scaleBy(s, x=center.x())
                            self.centreOn(thisViewBox, x=center.x())

                        if (
                            self.linkedAxis[thisViewBox]["linkY"] == "y"
                            and self.linkedAxis[thisViewBox]["linkX"] is None
                        ):
                            thisViewBox.scaleBy(s, y=center.y())
                            self.centreOn(thisViewBox, y=center.y())

                        if (
                            self.linkedAxis[thisViewBox]["linkX"] == "y"
                            and self.linkedAxis[thisViewBox]["linkY"] is None
                        ):
                            thisViewBox.scaleBy(s, y=center.x())
                            self.centreOn(thisViewBox, y=center.x())

                        if (
                            self.linkedAxis[thisViewBox]["linkY"] == "x"
                            and self.linkedAxis[thisViewBox]["linkX"] is None
                        ):
                            thisViewBox.scaleBy(s, x=center.y())
                            self.centreOn(thisViewBox, x=center.y())

                        # The following two cases aren't used currently by Lasagna, but may be required in the future.
                        # They haven't been tested yet. [28/07/15]
                        if (
                            self.linkedAxis[thisViewBox]["linkY"] == "x"
                            and self.linkedAxis[thisViewBox]["linkX"] == "y"
                        ):
                            thisViewBox.scaleBy(s, x=center.y(), y=center.x())
                            self.centreOn(thisViewBox, x=center.y(), y=center.x())

                        if (
                            self.linkedAxis[thisViewBox]["linkY"] == "y"
                            and self.linkedAxis[thisViewBox]["linkX"] == "x"
                        ):
                            thisViewBox.scaleBy(s, x=center.x(), y=center.y())
                            self.centreOn(thisViewBox, x=center.x(), y=center.y())
