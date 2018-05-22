"""
Creates a plugin that can add lines and points on the image manually
"""

import numpy as np
from PyQt5 import QtGui

from lasagna.plugins.lasagna_plugin import lasagna_plugin
from lasagna.plugins.tutorial_plugins import add_line_UI


class plugin(lasagna_plugin, QtGui.QWidget, add_line_UI.Ui_addLine):  # must inherit lasagna_plugin first

    def __init__(self, lasagna, parent=None):
        super(plugin, self).__init__(lasagna)  # This calls the lasagna_plugin constructor which in turn calls subsequent constructors

        # re-define some default properties that were originally defined in lasagna_plugin
        self.pluginShortName = 'Add lines'  # Appears on the menu
        self.pluginLongName = 'manually add lines and points'  # Can be used for other purposes (e.g. tool-tip)
        self.pluginAuthor = 'Antonin Blot'

        # Create widgets defined in the designer file
        self.setupUi(self)
        self.show()
        self.items = {}
        self.name_lineEdit.setText('ManualLine')
        # Set up the close button by linking it to the same slot as the normal window close button
        self.closeButton.released.connect(self.closePlugin)
        self.id_count = 0
        # add a sparsepoints ingredient
        self.ptsName = 'addLine_currentLine'
        self.lasagna.addIngredient(objectName=self.ptsName,
                                   kind='sparsepoints',
                                   data=[])
        self.lasagna.returnIngredientByName(self.ptsName).addToPlots()  # Add item to all three 2D plots
        # add a line ingredient
        self.lineName = 'addLine_fit_currentLine'
        self.lasagna.addIngredient(objectName=self.lineName,
                                   kind='lines',
                                   data=[])
        self.lasagna.returnIngredientByName(self.lineName).addToPlots()  # Add item to all three 2D plots
        self.fit = {}
        self.lasagna.axes2D[0].listNamedItemsInPlotWidget()

        # Connections:
        self.fit_pushButton.clicked.connect(self.fit_line)
        self.deg_spinBox.valueChanged.connect(self.fit_line)
        self.clear_pushButton.clicked.connect(self.clear_line)
        self.add_pushButton.clicked.connect(self.add_line)
        self.interactive_checkBox.clicked.connect(self.fit_line)

    # self.lasagna.updateMainWindowOnMouseMove is run each time the axes are updated. So we can hook into it
    # to update this window also
    def hook_axisClicked(self, axis):
        pos = self.lasagna.mousePositionInStack
        if not pos:
            print('Load an image first')
            return
        elif len(pos) != 3:
            raise ValueError('I expect 3D coordinates. Got: {}'.format(pos))
        n_pts = self.spinBox.value() + 1
        self.spinBox.setValue(n_pts)
        self.tableWidget.setRowCount(n_pts)
        item_id = self.id_count
        self.id_count += 1
        new_item = QtGui.QTableWidgetItem(str(item_id))
        self.items[(item_id, 0)] = new_item
        self.tableWidget.setItem(n_pts-1, 0, new_item)
        for i, p in enumerate(pos):
            new_item = QtGui.QTableWidgetItem(str(p))
            self.items[(item_id, i)] = new_item
            self.tableWidget.setItem(n_pts-1, i+1, new_item)
        self.update_current_line()
        print(pos)

    def add_line(self):
        """Add the current line and points to lasagna and start a new line"""

        pts_name = '{}_pts'.format(self.name_lineEdit.text())
        self.lasagna.addIngredient(objectName=pts_name,
                                   kind='sparsepoints',
                                   data=self.get_points_coord())
        self.lasagna.returnIngredientByName(pts_name).addToPlots()  # Add i

        if self.fit:
            data = self.fit['fit_coords']
            line_name = '{}_fit'.format(self.name_lineEdit.text())
            self.lasagna.addIngredient(objectName=line_name,
                                       kind='lines',
                                       data=data)
            self.lasagna.returnIngredientByName(line_name).addToPlots()  # Add item to all three 2D plots
        self.clear_line()

    def clear_line(self):
        """Clear current line

        :return:
        """
        self.items = {}
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.spinBox.setValue(0)
        self.fit_line()
        self.update_current_line()

    def update_current_line(self):
        """Change current line ingredient and display points

        :return:
        """
        coords = self.get_points_coord()
        pts = self.lasagna.returnIngredientByName(self.ptsName)

        changed = False
        if len(coords) != len(pts.raw_data()):
            changed = True
        elif len(coords) and any(coords != pts.raw_data()):
            changed = True
        if not changed:
            return

        pts._data = coords
        self.lasagna.initialiseAxes()  # update the plots.
        if self.interactive_checkBox.isChecked():
            self.fit_line(coords)
        return

    def fit_line(self, *args, **kwargs):
        """Polynomial fit of the points.

        Try to fit y = f(x) and x = f(y) and keep the version with lowest residuals to take
        care of vertical lines

        :return:
        """
        # The *args catches whatever connected slot might send (deg for deg_spinBox.valueChanged
        #         for instance)

        if 'coords' in kwargs:
            coords = kwargs['coords']
        else:
            coords = self.get_points_coord()

        deg = self.deg_spinBox.value()
        if len(coords) <= deg:
            print("Need at least %i points to fit"%(deg+1))
            self.fit = {}
            return
        coefs_x = np.polyfit(coords[:, 1], coords[:, 2], deg)
        fit_x = np.poly1d(coefs_x)
        res_x = np.sum((coords[:, 2]-fit_x(coords[:, 1]))**2)

        coefs_y = np.polyfit(coords[:, 2], coords[:, 1], deg)
        fit_y = np.poly1d(coefs_y)
        res_y = np.sum((coords[:, 1] - fit_y(coords[:, 2]))**2)

        if res_x <= res_y:
            self.fit = dict(is_x_y=True,
                            fit=fit_x,
                            coefs=coefs_x)
        else:
            self.fit = dict(is_x_y=False,
                            fit=fit_y,
                            coefs=coefs_y)

        if self.fit['is_x_y']:
            fit_data = np.arange(coords[:, 1].min(), coords[:, 1].max())
            replaced_ax = 2
        else:
            fit_data = np.arange(coords[:, 2].min(), coords[:, 2].max())
            replaced_ax = 1
        line_coords = np.repeat(fit_data, 3).reshape((-1, 3))
        line_coords[:, 0] = self.lasagna.axes2D[0].currentSlice
        line_coords[:, replaced_ax] = self.fit['fit'](fit_data)
        line = self.lasagna.returnIngredientByName(self.lineName)
        line._data = line_coords
        self.fit['fit_coords'] = line_coords

        self.lasagna.initialiseAxes()

    def get_points_coord(self):
        """Return the coordinates of points in the table

        :return:
        """
        if self.tableWidget.rowCount() == 0:
            return []
        o = []
        for i in range(self.tableWidget.rowCount()):
            coords = [int(self.tableWidget.item(i, c).text()) for c in range(1, 4)]
            o.append(np.array(coords, dtype=float))
        return np.vstack(o)

    def hook_updateMainWindowOnMouseMove_End(self):
        """
        This will run whenever the mouse moves in x or y across one of the axes in the main plot
        TODO: it would be nice to also run this on mouse wheel
        """
        x = self.lasagna.mouseX
        y = self.lasagna.mouseY

        # Get the widget that the mouse is currently in
        pos = QtGui.QCursor.pos()

        # Get the base image from this widget
        selected_stack_name = self.lasagna.selectedStackName()

    # The following methods are involved in shutting down the plugin window
    def closePlugin(self):
        """
        This method is called by lasagna when the user unchecks the plugin in the menu.
        """
        self.lasagna.removeIngredientByName(self.ptsName)
        self.lasagna.removeIngredientByName(self.lineName)
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
