from PyQt5 import QtGui, QtWidgets
from loader_dialog_UI import Ui_LoadPointDialog
from lasagna.utils import preferences


class LoaderDialog(QtWidgets.QDialog, Ui_LoadPointDialog):
    def __init__(self, parent=None, fileFilter=None):
        super(LoaderDialog, self).__init__(parent=parent)

        # Set up the user interface from Designer.
        self.setupUi(self)
        self.fileFilter = fileFilter
        # Connect up the buttons.
        self.loadToolButton.clicked.connect(self.get_fname)

    def get_fname(self):
        fnames = QtGui.QFileDialog.getOpenFileNames(self, 'Open file',
                                                    preferences.readPreference('lastLoadDir'),
                                                    self.fileFilter)[0]
        # getOpenFileNames returns a tuple of (file_list, filter). Ignore the filter
        self.FileListTextEdit.setText('\n'.join(fnames))

    def get_results(self):
        res = dict()
        fnames = self.FileListTextEdit.toPlainText().split('\n')
        res['fnames'] = fnames
        res['xy_scale'] = self.XYDoubleSpinBox.value()
        res['z_scale'] = self.ZDoubleSpinBox.value()
        res['first_slice'] = self.FirstSliceSpinBox.value()
        res['last_slice'] = self.LastSliceSpinBox.value()
        return res
