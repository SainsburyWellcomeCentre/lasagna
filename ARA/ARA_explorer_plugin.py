
"""
Tools for handling the ARA
eventually this will be a plugin
"""

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
        self.lasagna.imageStack = self.lasagna.loadImageStack(self.pathToARA)
        

        #Something along these lines should be able to change the color map 
        pos = np.array([0.0, 0.001, 0.25, 0.35, 0.45, 0.65, 0.9])
        color = np.array([[0,0,0,255],[255,0,0,255], [0,2,230,255], [7,255,112,255], [255,240,7,255], [7,153,255,255], [255,7,235,255]], dtype=np.ubyte)
        map = pg.ColorMap(pos, color)
        lut = map.getLookupTable(0.0, 1.0, 256)
        
        self.lasagna.coronal.img.setLookupTable(lut)
        self.lasagna.sagittal.img.setLookupTable(lut)
        self.lasagna.transverse.img.setLookupTable(lut)


        self.lasagna.initialiseAxes()
        self.lasagna.plottedIntensityRegionObj.setRegion((0,2E3))


    def closePlugin(self):

        #return color scale to normal
        self.lasagna.coronal.img.setLookupTable(None)
        self.lasagna.sagittal.img.setLookupTable(None)
        self.lasagna.transverse.img.setLookupTable(None)

        self.detachHooks()
        self.lasagna.clearAxes()


    #all methods starting with hook_ are automatically registered as hooks with lasagna 
    #when the plugin is started this happens in the lasagna_plugin constructor 
    def hook_updateStatusBar_End(self):
        """
        hooks into the stats bar updat to show the brain area name in the status bar 
        as the user mouses over the images
        """
        #code that was used to show the brain area name
        #is being moved to a plugin
        #ind=thisImage[self.mouseX,self.mouseY,0]


        if self.lasagna.pixelValue in self.annotations:
            thisArea=self.annotations[self.lasagna.pixelValue]
        else:
            thisArea='UKNOWN'

        self.lasagna.statusBarText = self.lasagna.statusBarText + ", area: " + thisArea


    def hook_loadBaseImageStack_Start(self):
        """
        Hooks into the file loading method to shut down the ARA Explorer if the
        user attempts to load a base stack
        """
        self.lasagna.stopPlugin(self.__module__) #This will call self.closePlugin
        self.lasagna.pluginActions[self.__module__].setChecked(False) #Uncheck the menu item associated with this plugin's name

        self.closePlugin()
