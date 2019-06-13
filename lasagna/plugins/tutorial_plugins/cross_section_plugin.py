"""
Creates a plugin that is composed of a new window with a pyqtgraph PlotWidget
On this graph we plot an x-axis cross-section of the image at the level which the 
mouse cursor is at. 
"""

from PyQt5 import QtGui
from PyQt5.QtWidgets import qApp

from lasagna.plugins.lasagna_plugin import LasagnaPlugin
from lasagna.plugins.tutorial_plugins import cross_section_plot_UI
from lasagna.utils import lasagna_qt_helper_functions


class plugin(LasagnaPlugin, QtGui.QWidget, cross_section_plot_UI.Ui_xSection): #must inherit LasagnaPlugin first

    def __init__(self, lasagna_serving, parent=None):
        super(plugin, self).__init__(lasagna_serving)  # This calls the LasagnaPlugin constructor which in turn calls subsequent constructors

        # re-define some default properties that were originally defined in LasagnaPlugin
        self.pluginShortName = 'Cross Section'  # Appears on the menu
        self.pluginLongName = 'displays cross section in a new window'  # Can be used for other purposes (e.g. tool-tip)
        self.pluginAuthor = 'Rob Campbell'

        # Create widgets defined in the designer file
        self.setupUi(self)
        self.show()

        # Set up the close button by linking it to the same slot as the normal window close button
        self.closeButton.released.connect(self.closePlugin)

    # self.lasagna.updateMainWindowOnMouseMove is run each time the axes are updated. So we can hook into it
    # to update this window also
    def hook_updateMainWindowOnMouseMove_End(self):
        """
        This will run whenever the mouse moves in x or y across one of the axes in the main plot
        TODO: it would be nice to also run this on mouse wheel
        """
        x = self.lasagna.mouseX
        y = self.lasagna.mouseY

        # Get the widget that the mouse is currently in
        pos = QtGui.QCursor.pos()
        plot_widget = qApp.widgetAt(pos).parent()  # The mouse is in this widget

        # Get the base image from this widget
        selected_stack_name = self.lasagna.selectedStackName()
        image_item = lasagna_qt_helper_functions.find_pyqt_graph_object_name_in_plot_widget(plot_widget,
                                                                                            itemName=selected_stack_name,
                                                                                            regex=True)
        if not image_item:
            return

        # Extract data from base image
        if image_item is not None:
            if image_item.image.shape[1] <= y or y < 0:
                return
            x_data = image_item.image[:, y]

            self.graphicsView.clear()
            self.graphicsView.plot(x_data)

        # Link the x axis of the cross-section view with the x axis of the image view
        # Do not use self.graphicsView.setXLink() as it is bidirectional
        x_range = plot_widget.viewRange()[0]
        self.graphicsView.setXRange(min=x_range[0], max=x_range[1])

    # The following methods are involved in shutting down the plugin window
    def closePlugin(self):
        """
        This method is called by lasagna when the user unchecks the plugin in the menu.
        """
        self.detachHooks() 
        self.close()

    # We define this here because we can't assume all plugins will have QWidget::closeEvent
    def closeEvent(self, event):
        """
        This event is executed when the user presses the close window (cross) button in the title bar
        """
        self.lasagna.stopPlugin(self.__module__)  # This will call self.closePlugin
        self.lasagna.pluginActions[self.__module__].setChecked(False)  # Uncheck the menu item associated with this plugin's name
        self.deleteLater()
        event.accept()
