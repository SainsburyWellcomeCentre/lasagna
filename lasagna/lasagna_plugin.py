"""
template for our plugin base class

decide if plugins should be started from the menu
or if the menu should load a new window from which 
plugins are started. I prefer the latter. 
"""


"""
This class must implement the following:

1. Provide access to required information from the viewer
2. Perform common duties at startup. Maybe send to the viewer some signal that the plugin is running
3. Perform common duties at shutdown. 
"""


import re

class lasagna_plugin(object):

    #Constructor
    def __init__(self,lasagna):
        super(lasagna_plugin,self).__init__() #In case of multiple inheritence. Useful for GUI making
        #This is crude, but the plugin will have access to everything
        #in the main window
        self.lasagna=lasagna

        #code to indicate visually that the plugin is running


        #define some default properties that all plugins must have
        self.pluginShortName='Plugin' #Appears on the menu
        self.pluginLongName='Lasagna plugin' #Can be used for other purposes (e.g. tool-tip)
        self.pluginAuthor='author name'

        self.confirmOnClose = False

        self.verbose = True #If true we print out debugging messages to the command line 
        self.attachHooks()

        if self.verbose:
            print("Ran %s constructor" % self.__module__)


    """
    #could not get this to work for some reason [ROB 20/07/15]
    #Destructor
    def __exit__(self):
        #Any defined hooks should always be detached on close. 
        print "Detaching hooks and closing plugin"
        self.detachHooks()
    """


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def attachHooks(self):
        """
        Find all methods in the plugin starting with hook_ and register these
        with their hooks in the lasagna main object. e.g. the method called
        hook_myFunction_End in the plugin will be linked to the hook myFunction_End
        in the lasagna.hooks dictionary

        """
        regexp = re.compile('hook_(.*)')
       
        for thisProperty in dir(self):

            if regexp.match(thisProperty):              
                hookName =regexp.findall(thisProperty)[0]
                print(hookName)
                if hookName in self.lasagna.hooks:
                    #attach the hook by adding to dictionary
                    self.lasagna.hooks[hookName].append(getattr(self, thisProperty))
                    if self.verbose:
                        print("Linking " + thisProperty + " to " + hookName)
                else:
                    if self.verbose:
                        print("No hook " + hookName + " found in lasagna.hooks for method " + thisProperty)

    
    def detachHooks(self):
        """
        Search list of hooks in lasagna for any hooks that might have come from this plugin.
        Remove any that are found. 
        """
        pluginName = self.__class__.__name__
        regexp = re.compile('.*' + pluginName + '.*')
        if self.verbose:
            print("Unlinking hooks for plugin '%s'" % pluginName)
        for thisHookList in list(self.lasagna.hooks.keys()):
            if len(thisHookList)==0:
                continue

            #for the unusual [:] see:
            #http://stackoverflow.com/questions/1207406/remove-items-from-a-list-while-iterating-in-python
            #it iterates over a copy of the list
            for thisHook in self.lasagna.hooks[thisHookList][:]:
                #print "%d hooks in list %s" % (len(self.lasagna.hooks[thisHookList]), str(thisHookList))
                if regexp.match(str(thisHook)):
                    self.lasagna.hooks[thisHookList].remove(thisHook)
                    if self.verbose:
                        print("Removed hook '%s'"  % str(thisHook))



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def initPlugin(self):
        """
        This method must be present. It will be defined by the plugin. It may do nothing. 
        """
        pass


    def closePlugin(self):
        """
        This method must be present. It will be defined by the plugin. It may do nothing. 
        """
        pass

