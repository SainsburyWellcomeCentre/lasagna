"""
A simple plugin just to change the order of the slices
"""
from PyQt5 import QtGui

from lasagna.lasagna_plugin import lasagna_plugin
from lasagna.registrationPlugins import reorder_stack_UI
from lasagna.registrationPlugins import selectstack_UI


class plugin(lasagna_plugin, QtGui.QWidget, reorder_stack_UI.Ui_reorderStack):  # must inherit lasagna_plugin first

    def __init__(self, lasagna, parent=None):
        super(plugin, self).__init__(lasagna)  # This calls the lasagna_plugin constructor which in turn calls subsequent constructors

        # re-define some default properties that were originally defined in lasagna_plugin
        self.pluginShortName = 'Reorder stack'  # Appears on the menu
        self.pluginLongName = 'manually reorder a stack'  # Can be used for other purposes (e.g. tool-tip)
        self.pluginAuthor = 'Antonin Blot'

        # Create widgets defined in the designer file
        self.setupUi(self)
        self.show()
        self.initialise()

        # Connections:
        self.closeButton.clicked.connect(self.close)
        self.down_toolButton.clicked.connect(self.move_down)
        self.up_toolButton.clicked.connect(self.move_up)
        self.listWidget.currentItemChanged.connect(self.update_plot)
        self.doit_pushButton.clicked.connect(self.doit)

    def initialise(self):
        self.listWidget.clear()
        self.stack_name = self.lasagna.selectedStackName()
        self.label.setText(self.stack_name)

        stk = self.lasagna.returnIngredientByName(self.stack_name)
        nslices = stk._data.shape[0]
        for i in range(nslices):
            self.listWidget.addItem('slice %i'%i)

    def move_up(self):
        """moves selected slices up
        """

        indice = [i.row() for i in self.listWidget.selectedIndexes()]
        if not len(indice):
            print('Select a slice to move it')
            return
        elif len(indice) != 1:
            raise IOError('Should not accept multiple selection. Change UI')
        indice = indice[0]
        if indice == 0:
            print('already first')
            return
        item = self.listWidget.takeItem(indice)
        self.listWidget.insertItem(indice-1, item)
        self.listWidget.setCurrentRow(indice-1)

    def move_down(self):
        indice = [i.row() for i in self.listWidget.selectedIndexes()]
        if not len(indice):
            print('Select a slice to move it')
            return
        elif len(indice) != 1:
            raise IOError('Should not accept multiple selection. Change UI')
        indice = indice[0]
        if indice == self.listWidget.count()-1:
            print('already last')
            return
        item = self.listWidget.takeItem(indice)
        self.listWidget.insertItem(indice+1, item)
        self.listWidget.setCurrentRow(indice+1)

    def update_plot(self, current=None, previous=None):
        """Update the drawn slice

        Current and Previous are arguments sent by currentItemChanged. If they are none
        just take the first (and only) selected item
        """
        # update only if the box is checked
        if not self.update_checkBox.isChecked():
            return

        if current is None:
            # we have no items provided, just take what is selected
            item = self.listWidget.selectedItems()
            if not len(item):
                # nothing is selected, return
                return
            item = item[0]
        else:
            # we have an item, ignore the previous, use the current
            item = current

        for axis in self.lasagna.axes2D:
            axis.updatePlotItems_2D(self.lasagna.ingredientList,
                                    sliceToPlot=int(item.text().split(' ')[1]))

    def doit(self):
        stk_list = [st.objectName for st in self.lasagna.returnIngredientByType('imagestack')]
        dlg = SelectStack(self, stk_list)
        results = dlg.exec_()
        if not results:
            print('Cancel')
            return
        values = dlg.getValues()

        if not len(values):
            print('Nothing selected, do nothing')
            return

        order = [self.listWidget.item(i) for i in range(self.listWidget.count())]
        order = [int(l.text().split(' ')[1]) for l in order]
        for stck_name in values:
            stk = self.lasagna.returnIngredientByName(str(stck_name))
            stk._data = stk._data[order, :, :]
        self.initialise()

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


class SelectStack(QtGui.QDialog, selectstack_UI.Ui_selectStack):  # must inherit lasagna_plugin first)
    def __init__(self, parent=None, stack_list=[]):
        super(SelectStack, self).__init__(parent)  # This calls the lasagna_plugin constructor which in turn calls subsequent constructors
        self.setupUi(self)

        for st in stack_list:
            self.listWidget.addItem(st)

    def getValues(self):
        return [i.text() for i in self.listWidget.selectedItems()]
