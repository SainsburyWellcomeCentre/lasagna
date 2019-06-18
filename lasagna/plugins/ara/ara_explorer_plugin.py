"""
lasagna plugin for exploring the Allen Brain Atlas:
1. Display of average template brain.
2. Reporting of brain area name
more stuff... 

Rob Campbell
"""

import os

from PyQt5 import QtGui, QtCore


# For the UI
from lasagna.plugins.ara import ara_explorer_UI

# For contour drawing
from lasagna.plugins.ara.ara_plugin_base import AraPluginBase


class plugin(AraPluginBase, ara_explorer_UI.Ui_ara_explorer):
    def __init__(self, lasagna_serving):
        self.pluginAuthor = "Rob Campbell"
        self.pluginShortName = "ARA explorer"
        self.pluginLongName = "Allen Reference Atlas explorer"

        # Default names of the files that we need:
        self.atlasFileName = "atlas"
        self.templateFileName = "template"
        self.labelsFileName = "labels"
        self.contourName = "aracontour"
        self.clear_stacks = True
        super(plugin, self).__init__(lasagna_serving)

    def setup_tree(self):
        self.brainArea_itemModel = QtGui.QStandardItemModel(self.brainArea_treeView)
        self.brainArea_treeView.setModel(self.brainArea_itemModel)
        # Link the selections in the tree view to a slot in order to allow highlighting of the selected area
        self.brainArea_treeView.selectionModel().selectionChanged[
            QtCore.QItemSelection, QtCore.QItemSelection
        ].connect(self.highlightSelectedAreaFromList)

    def autoload_first_ara_entry(self):
        # If the user has asked for this, load the first ARA entry automatically
        currently_selected_ara = str(
            self.araName_comboBox.itemText(self.araName_comboBox.currentIndex())
        )
        if self.prefs["loadFirstAtlasOnStartup"]:
            print("Auto-Loading {}".format(currently_selected_ara))
            self.loadARA(currently_selected_ara)
            self.load_pushButton.setEnabled(
                False
            )  # disable because the current selection has now been loaded

    def _get_data_structure(self):
        return dict(currentlyLoadedAtlasName="", currentlyLoadedOverlay="")

    def link_slots(self):
        """Link signals to slots"""
        self.araName_comboBox.activated.connect(self.araName_comboBox_slot)
        self.load_pushButton.released.connect(self.load_pushButton_slot)
        self.overlayTemplate_checkBox.stateChanged.connect(
            self.overlayTemplate_checkBox_slot
        )
        self.statusBarName_checkBox.stateChanged.connect(
            self.statusBarName_checkBox_slot
        )
        self.highlightArea_checkBox.stateChanged.connect(
            self.highlightArea_checkBox_slot
        )

        self.setup_tree()

    # --------------------------------------
    # UI slots
    # all methods starting with hook_ are automatically registered as hooks with lasagna
    # when the plugin is started this happens in the LasagnaPlugin constructor
    def araName_comboBox_slot(self):
        """
        Enables the load button only if the currently selected item is not loaded
        """
        # If nothing has been loaded then for sure we need the load button enabled
        if not self.data["currentlyLoadedAtlasName"]:
            self.load_pushButton.setEnabled(True)
            return

        if self.data["currentlyLoadedAtlasName"] != str(
            self.araName_comboBox.itemText(self.araName_comboBox.currentIndex())
        ):  # FIXME: else ?
            self.load_pushButton.setEnabled(True)
        elif self.data["currentlyLoadedAtlasName"] == str(
            self.araName_comboBox.itemText(self.araName_comboBox.currentIndex())
        ):
            self.load_pushButton.setEnabled(False)

    def load_pushButton_slot(self):
        """
        Load the currently selected ARA version
        """
        selected_name = str(
            self.araName_comboBox.itemText(self.araName_comboBox.currentIndex())
        )
        self.loadARA(selected_name)

    def overlayTemplate_checkBox_slot(self):
        """
        Load or unload the template overlay
        """
        fname = self.data["template"]
        if not fname:
            return

        if self.overlayTemplate_checkBox.isChecked():
            if os.path.exists(fname):
                self.addOverlay(fname)
                return

        if not self.overlayTemplate_checkBox.isChecked():
            overlay_name = fname.split(os.path.sep)[-1]
            self.lasagna.removeIngredientByName(overlay_name)

        self.lasagna.returnIngredientByName(
            self.data["currentlyLoadedAtlasName"]
        ).lut = "gray"
        self.lasagna.initialiseAxes()

    # --------------------------------------
    # core methods: these do the meat of the work
    def loadARA(self, araName):
        """
        Coordinate loading of the ARA items defined in the dictionary paths. 
        araName is a value from the self.paths dictionary. The values will be 
        combobox item texts and will load a dictionary from self.paths. The keys
        of this dictionary have these keys: 
        'atlas' (full path to atlas volume file)
        'labels' (full path to atlas labels file - csv or json)
        'template' (full path to average template file - optional)
        """

        paths = self.paths[araName]

        # remove the currently loaded ARA (if present)
        if self.data["currentlyLoadedAtlasName"]:
            self.lasagna.removeIngredientByName(self.data["currentlyLoadedAtlasName"])

        self.data["labels"] = self.loadLabels(paths["labels"])  # see ARA_plotter.py

        self.addAreaDataToTreeView(
            self.data["labels"],
            self.rootNode,
            self.brainArea_itemModel.invisibleRootItem(),
        )

        self.lasagna.loadImageStack(paths["atlas"])

        self.data["currentlyLoadedAtlasName"] = paths["atlas"].split(os.path.sep)[-1]

        self.data["template"] = paths["template"]
        if os.path.exists(paths["template"]):
            self.overlayTemplate_checkBox.setEnabled(True)
            if self.overlayTemplate_checkBox.isChecked():
                self.addOverlay(self.data["template"])
        else:
            self.overlayTemplate_checkBox.setEnabled(False)

        # self.setARAcolors()
        # self.lasagna.initialiseAxes(resetAxes=True)
        self.lasagna.returnIngredientByName(
            self.data["currentlyLoadedAtlasName"]
        ).minMax = [0, 1.2e3]
        self.lasagna.initialiseAxes(resetAxes=True)

    def addOverlay(self, fname):
        """
        Add an overlay
        """
        self.lasagna.loadImageStack(fname)
        self.data["currentlyLoadedOverlay"] = str(fname.split(os.path.sep)[-1])
        self.lasagna.returnIngredientByName(
            self.data["currentlyLoadedAtlasName"]
        ).lut = "gray"
        self.lasagna.returnIngredientByName(
            self.data["currentlyLoadedOverlay"]
        ).lut = "cyan"
        self.lasagna.returnIngredientByName(
            self.data["currentlyLoadedOverlay"]
        ).minMax = [0, 1.5e3]
        self.lasagna.initialiseAxes(resetAxes=True)

    # ---------------
    # Methods to handle the tree
    def addAreaDataToTreeView(self, thisTree, nodeID, parent):
        """
        Add a tree structure of area names to the QListView
        """
        children = thisTree[nodeID].children
        for child in sorted(children):
            child_item = QtGui.QStandardItem(thisTree[child].data["name"])
            child_item.setData(
                child
            )  # Store index. Can be retrieved by: child_item.data().toInt()[0] NOT USING THIS RIGHT NOW
            parent.appendRow(child_item)
            self.addAreaDataToTreeView(thisTree, child, child_item)

    def AreaName2NodeID(self, thisTree, name, nodeID=None):
        """
        Searches the tree for a brain area called name and returns the node ID (atlas index value)
        Breaks out of the search loop if the area is found and propagates the value back through
        the recursive function calls
        """
        if nodeID is None:
            nodeID = self.rootNode

        children = thisTree[nodeID].children
        for child in sorted(children):
            if thisTree[child].data["name"] == name:
                return child
            else:
                return_val = self.AreaName2NodeID(
                    thisTree=thisTree, name=name, nodeID=child
                )
                if return_val:
                    return return_val
        return False

    def highlightSelectedAreaFromList(self):
        """
        This slot is run when the user clicks on a brain area in the list
        """
        get_from_model = (
            False
        )  # It would be great to get the area ID from the model, but I can't figure out how to get the sub-model that houses the data

        index = self.brainArea_treeView.selectedIndexes()[0]

        # Get the image stack, as we need to feed it to drawAreaHighlight
        _, image_stack = self.get_atlas_image_stack()

        if get_from_model:
            # The following row and column indexes are also correct, but index.model() is the root model and this is wrong.
            tree_index = (
                index.model().item(index.row(), index.column()).data().toInt()[0]
            )
            print("tree_index (%d,%d): %d" % (index.row(), index.column(), tree_index))
        else:  # so we do it the stupid way from the reee
            area_name = index.data()
            tree_index = self.AreaName2NodeID(self.data["labels"], area_name)

        if tree_index is not None:
            # print("highlighting %d" % tree_index)
            self.drawAreaHighlight(
                image_stack, tree_index, highlightOnlyCurrentAxis=False
            )

    def get_atlas_image_stack(self, plugin_name=None):
        ara_name = str(
            self.araName_comboBox.itemText(self.araName_comboBox.currentIndex())
        )
        atlas_layer_name = self.paths[ara_name]["atlas"].split(os.path.sep)[-1]
        ingredient = self.lasagna.returnIngredientByName(atlas_layer_name)
        if not ingredient:
            if plugin_name is not None:
                print(
                    "ARA_explorer_plugin.{} Failed to find image_stack named {}".format(
                        plugin_name, atlas_layer_name
                    )
                )
            return None, None
        else:
            image_stack = ingredient.raw_data()
            return atlas_layer_name, image_stack
