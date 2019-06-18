"""
Embellishes the lasagna status bar in a pointless way
"""
from lasagna.plugins.lasagna_plugin import LasagnaPlugin


# Must be a class called "plugin" and must inherit LasagnaPlugin first
class plugin(LasagnaPlugin):
    def __init__(self, lasagna_serving):
        # The following calls the LasagnaPlugin constructor which in turn calls subsequent constructors
        super(plugin, self).__init__(
            lasagna_serving
        )  # Run the constructor from LasagnaPlugin with lasagna as an input argument
        # re-define some default properties that were originally defined in LasagnaPlugin
        self.pluginShortName = "Embelisher"  # Appears on the menu
        self.pluginLongName = (
            "status bar emblishment"
        )  # Can be used for other purposes (e.g. tool-tip)
        self.pluginAuthor = "Rob Campbell"

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # House-keeping method
    def closePlugin(self):
        """
        Detaches hook method (below) when the plugin closes.
        """
        self.detachHooks()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Hooks
    # The following methods are called from methods in lasagna_object
    def hook_updateStatusBar_End(self):
        """
        Define a special "hook_XXX" method. This method is run at the end of lasagna.updateStatusBar()
        right before the message is actually displayed. In general, hooks should be in the form
        hook_[lasagna method name_[Start|End] Search lasagna_object.py for methods that have hooks.
        """
        self.lasagna.statusBarText = "CuReNt CoOrDiNaTeS: " + self.lasagna.statusBarText
