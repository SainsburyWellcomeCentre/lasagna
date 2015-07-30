"""
load an overlay image stack that will be placed on top of the base stack to
create a red/green overlay
"""

import handleIngredients
from PyQt4 import QtGui
import os

class loadOverlayImageStack(object):
    def __init__(self,lasagna):

        self.lasagna = lasagna
        self.objectName = 'load_overlay' #Can be uased as an optional way of finding the object later


        #Construct the QActions and other stuff required to integrate the load dialog into the menu
        
        #Instantiate the action
        self.loadAction = QtGui.QAction(self.lasagna)
        self.loadAction.setEnabled(True)    #TODO: make this contingent on whether there is a base stack loaded
                                            #TODO: also see lasagna.loadBaseImageStack()

        #Add an icon to the action
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/actions/icons/overlay.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.loadAction.setIcon(icon4)

        #Insert the action into the menu
        self.loadAction.setObjectName("loadOverlayImageStack")
        self.lasagna.menuLoad_ingredient.addAction(self.loadAction)
        self.loadAction.setText("Load overlay stack")

        #Link the action to the slot
        self.loadAction.triggered.connect(self.showLoadDialog)


    def load(self,fnameToLoad):
        """
        The load method does all of the things necessary for loading the overlay
        and displaying it correctly
        """

        #Get the existing base image stack so we can ensure that our overlay is the same size
        baseStack = handleIngredients.returnIngredientByName('baseImage',self.lasagna.ingredients) 

        if  baseStack == False:
            self.lasgna.actionLoadOverlay.setEnabled(False) #TODO: will need to be changed as we detach this from core application
            return

        #Use method from lasagna to load imagestack
        loadedImageStack = self.lasagna.loadImageStack(fnameToLoad) 

        #Do not proceed with adding overlay if it's of a different size
        existingSize = baseStack.data().shape
        overlaySize = loadedImageStack.shape

        #Ensure that overlay is the same size as the base image stack
        if not existingSize == overlaySize:
            msg = '*** Overlay is not the same size as the loaded image ***'
            print msg
            self.lasagna.statusBar.showMessage(msg)

            print "Base image:"
            print existingSize
            print "Overlay image:"
            print overlaySize

            return


        #TODO: this is mostly duplicated code from loadBaseImageStack. Maybe this can be reduced somewhat?
        objName='overlayImage'
        self.lasagna.ingredients = handleIngredients.addIngredient(self.lasagna.ingredients, objectName=objName , 
                                                              kind='imagestack'       , 
                                                              data=loadedImageStack   , 
                                                              fname=fnameToLoad)

        #set colormaps for the two stacks
        handleIngredients.returnIngredientByName('baseImage',self.lasagna.ingredients).lut='red'
        handleIngredients.returnIngredientByName('overlayImage',self.lasagna.ingredients).lut='green'
        
        #Add plot items to axes so that they become available for plotting
        [axis.addItemToPlotWidget(handleIngredients.returnIngredientByName(objName,self.lasagna.ingredients)) for axis in self.lasagna.axes2D]

        #TODO: Both of the following lines need to be changed. They call hard-coded stuff in lasagna.py 
        #and doing this is no longer an option
        self.lasagna.overlayEnableActions()
        self.lasagna.overlayLoaded=True



    def showLoadDialog(self):
        """
        This slot brings up the load dialog and retrieves the file name.
        If the file name is valid, it loads the base stack using the load method.
        We split things up to make it easier to load the base stack pragmatically,
        such as from a plugin, without going via the load dialog. 
        """
        print "IN SLOT"
        fname = self.lasagna.showFileLoadDialog()
        if fname == None:
            return

        if os.path.isfile(fname): 
            self.load(str(fname)) #convert QString and load
            self.lasagna.initialiseAxes()
        else:
            self.lasagna.statusBar.showMessage("Unable to find " + str(fname))
