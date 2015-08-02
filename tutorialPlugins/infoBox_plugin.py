

"""
Creates a plugin that is composed of a new window with a text field (QLabel)
The plugin hooks into updateMainWindowOnMouseMove and gets the X and Y 
position of the mouse in the current axes each time this method is run. 
This information is then displayed on the screen. 
"""


from lasagna_plugin import lasagna_plugin
import infoBox_UI
from PyQt4 import QtGui, QtCore
import sys

class plugin(lasagna_plugin, QtGui.QWidget, infoBox_UI.Ui_infoBox): #must inherit lasagna_plugin first

    def __init__(self,lasagna,parent=None):
        super(plugin,self).__init__(lasagna) #This calls the lasagna_plugin constructor which in turn calls subsequent constructors

        #re-define some default properties that were originally defined in lasagna_plugin
        self.pluginShortName='Info Box' #Appears on the menu
        self.pluginLongName='displays image info in a new window' #Can be used for other purposes (e.g. tool-tip)
        self.pluginAuthor='Rob Campbell'


        #Create widgets defined in the designer file
        self.setupUi(self)
        self.show()

        #Set up the close button by linking it to the same slot as the normal window close button
        self.closeButton.released.connect(self.closePlugin)



    #self.lasagna.updateMainWindowOnMouseMove is run each time the axes are updated. So we can hook into it 
    #to update this window also
    def hook_updateMainWindowOnMouseMove_End(self):
        X = self.lasagna.mouseX
        Y = self.lasagna.mouseY

        pos = QtGui.QCursor.pos()
        PlotWidget = QtGui.qApp.widgetAt(pos).parent()
        currentAxisName = PlotWidget.objectName()
        
        msg = "Mouse is in %s\nX: %d , Y: %d" % (currentAxisName,X,Y)
        self.label.setText(msg)


    #The following methods are involved in shutting down the plugin window
    """
    This method is called by lasagna when the user unchecks the plugin in the menu
    """
    def closePlugin(self):
        self.detachHooks()
        self.close()


    #We define this here because we can't assume all plugins will have QWidget::closeEvent
    def closeEvent(self, event):
        """
        This event is execute when the user presses the close window (cross) button in the title bar
        """
        self.lasagna.stopPlugin(self.__module__) #This will call self.closePlugin as well as making it possible to restart the plugin
        self.lasagna.pluginActions[self.__module__].setChecked(False) #Uncheck the menu item associated with this plugin's name
        self.deleteLater()
        event.accept()

