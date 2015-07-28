


"""
Tools for handling the ARA
eventually this will be a plugin
"""
from lasagna_plugin import lasagna_plugin
import ARA

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
        self.lasagna.initialiseAxes()
        self.lasagna.plottedIntensityRegionObj.setRegion((0,2E3))


    def closePlugin(self):
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
