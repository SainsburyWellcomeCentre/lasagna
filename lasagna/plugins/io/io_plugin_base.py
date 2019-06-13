from PyQt5 import QtGui

from lasagna.plugins.lasagna_plugin import LasagnaPlugin


class IoBasePlugin(LasagnaPlugin):
    def __init__(self, lasagna_serving):
        super(IoBasePlugin, self).__init__(lasagna_serving)
        self.lasagna = lasagna_serving
        # Construct the QActions and other stuff required to integrate the load dialog into the menu
        self.loadAction = QtGui.QAction(self.lasagna)  # Instantiate the menu action

        self.add_icon()
        self.insert_in_menu()

    def get_icon(self):
        """
        Get the icon from self.icon_name

        :return: QtGui.QPixmap
        """
        plugin_folder = ':/actions/icons/'  # FIXME: use module to give icon folder
        return QtGui.QPixmap('{}{}.png'.format(plugin_folder, self.icon_name))

    def add_icon(self):
        """
        Add an icon to the action
        """
        icon_load_overlay = QtGui.QIcon()
        icon_load_overlay.addPixmap(self.get_icon(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.loadAction.setIcon(icon_load_overlay)

    def insert_in_menu(self):
        """
        Insert the action into the menu
        """
        self.loadAction.setObjectName("fijiPointRead")
        self.lasagna.menuLoad_ingredient.addAction(self.loadAction)
        self.loadAction.setText(self.objectName.title().replace('_', ' ')[:-2])

        self.loadAction.triggered.connect(self.showLoadDialog)  # Link the action to the slot

    # def showLoadDialog(self, fname=None):