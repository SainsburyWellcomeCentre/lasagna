

"""
This tutorial plugin demonstrates how to overlay dynamically generated
point data onto the plot axes. The plugin does the following:

* Upon starting, the plugin generates 100 independent random points in
  each view and overlays them onto the axes.
* Upon each re-painting of the axes a new set of 100 points are created
  and overlaid.
* The points are all removed and their plot items are cleaned up when
  the plugin is closed.

"""

import numpy as np

from lasagna.plugins.lasagna_plugin import LasagnaPlugin


class plugin(LasagnaPlugin):

    def __init__(self, lasagna_serving, parent=None):
        super(plugin, self).__init__(lasagna_serving)

        # re-define some default properties that were originally defined in LasagnaPlugin
        self.pluginShortName = 'Overlay random points'
        self.pluginLongName = 'displays dynamically generated random points onto the axes'
        self.pluginAuthor = 'Rob Campbell'

        self.lasagna = lasagna_serving

        # add a sparsepoints ingredient
        self.objName = 'tutePoints'
        self.lasagna.addIngredient(objectName=self.objName,
                                   kind='sparsepoints',
                                   data=self.generateRandomData())

        self.lasagna.returnIngredientByName(self.objName).addToPlots()  # Add item to all three 2D plots
        self.lasagna.axes2D[0].listNamedItemsInPlotWidget()
        self.lasagna.update_2D_plot_ingredients_in_axes(resetAxes=True)  # update the plots.

    def generateRandomData(self):
        """
        Generate random data spanning the extent of the first image stack
        """
        stack_name = self.lasagna.imageStackLayers_Model.index(0, 0).data()
        first_layer = self.lasagna.returnIngredientByName(stack_name)
        if not first_layer:
            print("No image layers loaded")
            return

        im_shape = first_layer.data().shape

        n = 10000  # number of random points to make
        print("Overlaying %d random points" % n)
        num_axes = 3

        r = np.random.rand(n*num_axes).reshape((n, num_axes))  # the random array

        # multiply values in each dimension of the array by the array size of the first layer image
        for i in range(num_axes):
            r[:, i] = np.floor(r[:, i]*im_shape[i])

        return r

    # The following methods are involved in shutting down the plugin window
    """
    This method is called by lasagna when the user unchecks the plugin in the menu
    """

    def closePlugin(self):
        # Remove points from axes then remove the ingredient from the list.
        self.lasagna.removeIngredientByName(self.objName)
