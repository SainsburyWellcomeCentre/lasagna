

"""
Embelishes the lasagna status bar in a pointless way
"""
from lasagna_plugin import lasagna_plugin

class plugin(lasagna_plugin):

    def __init__(self,lasagna):
        super(plugin,self).__init__(lasagna) #Run the constructor from lasagna_plugin with lasagna as an input argument


        #re-define some default properties that were originally defined in lasagna_plugin
        self.pluginShortName='Embelisher' #Appears on the menu
        self.pluginLongName='status bar emblishment' #Can be used for other purposes (e.g. tool-tip)
        self.pluginAuthor='Rob Campbell'


    """
    Define a special "hook_XXX" method. This method is run at the end of lasagna.updateStatusBar()
    right before the message is actually displayed. In general, hooks should be in the form
    hook_[lasagna method name_[Start|End] Search main.py for methods that have hooks.
    """

    def hook_updateStatusBar_End(self):
        self.lasagna.statusBarText = "CuReNt CoOrDiNaTeS: " + self.lasagna.statusBarText 

    def closePlugin(self):
        self.detachHooks()
        

   