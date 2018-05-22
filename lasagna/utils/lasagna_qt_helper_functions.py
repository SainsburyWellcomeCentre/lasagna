"""
Helper functions for lasagna. Functions in this file are involved in the following task:
Finding plot widgets by name within an object.
"""


def find_pyqt_graph_object_name_in_plot_widget(PlotWidget, itemName, regex=False, verbose=False):
    """
    Searches a PyQtGraph PlotWidget for an plot object (i.e. something added with .addItem)
    with name "itemName"

    Inputs:
    PlotWidget - an instance of a PyQtGraph plot widget
    itemName - a string defining the .objectName to search for in PlotWidget. 
    regex - if True the itemName is treated as a regular expression. [False by default]

    Outputs:
    Returns the instance of the object bearing the chosen name. Returns None if no
    object was found. 

    Notes:
    The user must assign a sensible name to every created plot item. Added objects will
    by default have a blank object name. This function does not do a recursive search,
    so you can't feed it the GUI root object and expect an answer. It returns *ONLY* the 
    first found item.
    """

    if verbose:
        print("find_pyqt_graph_object_name_in_plot_widget - "
              "looking for object {} in PlotWidget {}".format(itemName, PlotWidget))

    if regex:
        import re

    if not hasattr(PlotWidget, 'getPlotItem'):
        print("find_pyqt_graph_object_name_in_plot_widget finds no attribute getPlotItem")
        return False

    plot_item = PlotWidget.getPlotItem()

    if not hasattr(plot_item, 'items'):
        print("find_pyqt_graph_object_name_in_plot_widget finds no attribute 'items'")
        return False

    if not plot_item.items:
        print("find_pyqt_graph_object_name_in_plot_widget finds no items in list")
        return False

    if regex:
        for item in plot_item.items:
            if re.search(itemName, item.objectName):
                return item
    else:
        for item in plot_item.items:
            if item.objectName == itemName:
                return item

    if verbose:
        print("Failed to find {} in PlotWidget".format(itemName))
    return False
