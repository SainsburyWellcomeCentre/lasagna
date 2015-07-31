
"""
Tools for handling the ARA
eventually this will be a plugin
"""

import handleIngredients
from lasagna_plugin import lasagna_plugin
import ARA
import numpy as np
import pyqtgraph as pg

class plugin(lasagna_plugin):
    

    def __init__(self,lasagna):
        super(plugin,self).__init__(lasagna)
        self.lasagna=lasagna

        self.pluginShortName="ARA explorer"
        self.pluginLongName="Allen Reference Atlas explorer"
        self.pluginAuthor="Rob Campbell"

        fnames = ARA.fileNames() 
        self.pathToARA = fnames['ARAdir'] + fnames['stackFname']    
        self.pathToAnnotations = fnames['ARAdir'] + fnames['annotationFname']   

        self.annotations = ARA.readAnnotation(self.pathToAnnotations)

        self.initPlugin()


    def initPlugin(self):
        self.lasagna.loadBaseImageStack(self.pathToARA)
        

        #Make up a disjointed colormap
        pos = np.array([0.0, 0.001, 0.25, 0.35, 0.45, 0.65, 0.9])
        color = np.array([[0,0,0,255],[255,0,0,255], [0,2,230,255], [7,255,112,255], [255,240,7,255], [7,153,255,255], [255,7,235,255]], dtype=np.ubyte)
        map = pg.ColorMap(pos, color)
        lut = map.getLookupTable(0.0, 1.0, 256)

        #Assign the colormap to the imagestack object
        handleIngredients.returnIngredientByName('baseImage',self.lasagna.ingredients).lut=lut

        self.lasagna.initialiseAxes()
        self.lasagna.plottedIntensityRegionObj.setRegion((0,2E3))


    def closePlugin(self):

        #Ensure image color scale returns to normal
        handleIngredients.returnIngredientByName('baseImage',self.lasagna.ingredients).lut='gray'
        self.detachHooks()


    #all methods starting with hook_ are automatically registered as hooks with lasagna 
    #when the plugin is started this happens in the lasagna_plugin constructor 
    def hook_updateStatusBar_End(self):
        """
        hooks into the status bar update function to show the brain area name in the status bar 
        as the user mouses over the images
        """
        #code to handle the brain area names is in ARA.py
        if self.lasagna.pixelValue in self.annotations:
            thisArea=self.annotations[self.lasagna.pixelValue]
        else:
            thisArea='UKNOWN'

        self.lasagna.statusBarText = self.lasagna.statusBarText + ", area: " + thisArea



    #The following hooks are for graceful shut down
    def hook_showBaseStackLoadDialog_Start(self):
        """
        Hooks into base image file dialog method to shut down the ARA Explorer if the
        user attempts to load a base stack
        """

        self.lasagna.stopPlugin(self.__module__) #This will call self.closePlugin
        self.lasagna.pluginActions[self.__module__].setChecked(False) #Uncheck the menu item associated with this plugin's name

        self.closePlugin()


    def hook_loadRecentFileSlot_Start(self):
        """
        Hooks into the recent file loading method to shut down the ARA Explorer if the
        user attempts to load a base stack
        """

        self.lasagna.stopPlugin(self.__module__) #This will call self.closePlugin
        self.lasagna.pluginActions[self.__module__].setChecked(False) #Uncheck the menu item associated with this plugin's name

        self.closePlugin()

