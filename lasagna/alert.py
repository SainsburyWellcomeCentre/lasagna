
"""
Brings up an alert message to warn the user when something significant has happened.
We can't rely on the user watching the console for messages.
"""

# TODO: maybe neater to just replace with a QMessageBox
# e.g.  QMessageBox.information(None, "Hello!", "Something went wrong")

from lasagna import alert_UI
from PyQt5 import QtWidgets


class alert(alert_UI.Ui_alertBox, QtWidgets.QWidget):

    def __init__(self, lasagna_serving, alertText="Alert!"):
        super(alert, self).__init__()

        self.alertText = alertText
        self.lasagna = lasagna_serving

        # Create widgets defined in the designer file
        self.setupUi(self)
        self.center()
        self.show()

        self.label.setText(alertText)

        self.closeButton.released.connect(self.closeAlertBox)

    def closeAlertBox(self):
        self.close()

    def center(self):
        """
        Centre window on screen
        http://stackoverflow.com/questions/20243637/pyqt4-center-window-on-active-screen
        """
        frame_gm = self.frameGeometry()
        screen = self.lasagna.app.desktop().screenNumber(self.lasagna.app.desktop().cursor().pos())
        center_point = self.lasagna.app.desktop().screenGeometry(screen).center()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())
