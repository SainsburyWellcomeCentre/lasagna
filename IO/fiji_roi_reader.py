"""
Loads data from imagej/fiji ROIs or ROIs sets (zip files)

Require ijroi from: https://github.com/tdsmith/ijroi/blob/master/ijroi/ijroi.py
`pip install ijroi` to get it.


"""
import ijroi

class loaderClass(lasagna_plugin):
    def __init__(self, lasagna):
        super(loaderClass, self).__init__(lasagna)

        self.lasagna = lasagna
        self.objectName = 'fiji_roi_reader'
        self.kind = 'sparsepoints'
        # Construct the QActions and other stuff required to integrate the load dialog into the menu
        self.loadAction = QtGui.QAction(self.lasagna)  # Instantiate the menu action

        # Add an icon to the action
        iconLoadOverlay = QtGui.QIcon()
        iconLoadOverlay.addPixmap(QtGui.QPixmap(":/actions/icons/points.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.loadAction.setIcon(iconLoadOverlay)

        # Insert the action into the menu
        self.loadAction.setObjectName("fijiPointRead")
        self.lasagna.menuLoad_ingredient.addAction(self.loadAction)
        self.loadAction.setText("Fiji roi read")

        self.loadAction.triggered.connect(self.showLoadDialog)  # Link the action to the slot



        # Slots follow

    def showLoadDialog(self, fname=None):
        """
        This slot brings up the load dialog and retrieves the file name.
        If a filename is provided then this is loaded and no dialog is brought up.
        If the file name is valid, it loads the base stack using the load method.

        """

        if fname is None or fname == False:
            fname = self.lasagna.showFileLoadDialog(fileFilter="ImageJ ROIs (*.roi *.zip)")

        if fname is None or fname == False:
            return

        if os.path.isfile(fname):
            if fname.endswith('.zip'):
                rois = ijroi.read_roi_zip(fname)
            else:
                rois = []

            # a list of strings with each string being one line from the file
            asList = contents.split('\n')
            data = []
            for ii in range(len(asList)):
                if len(asList[ii]) == 0:
                    continue
                data.append([float(x) for x in asList[ii].split(',')])

            # A point series should be a list of lists where each list has a length of 3,
            # corresponding to the position of each point in 3D space. However, point
            # series could also have a length of 4. If this is the case, the fourth
            # value is the index of the series. This allows a single file to hold multiple
            # different point series. We handle these two cases differently. First we deal
            # with the the standard case:
            if len(data[1]) == 3:
                # Create an ingredient with the same name as the file name
                objName = fname.split(os.path.sep)[-1]
                self.lasagna.addIngredient(object_name=objName,
                                           kind=self.kind,
                                           data=np.asarray(data),
                                           fname=fname
                                           )

                # Add this ingredient to all three plots
                self.lasagna.returnIngredientByName(objName).addToPlots()

                # Update the plots
                self.lasagna.initialiseAxes()

            elif len(data[1]) == 4:
                # What are the unique data series values?
                dSeries = [x[3] for x in data]
                dSeries = list(set(dSeries))

                # Loop through these unique series and add as separate sparse point objects

                for thisIndex in dSeries:
                    tmp = []
                    for thisRow in data:
                        if thisRow[3] == thisIndex:
                            tmp.append(thisRow[:3])

                    print("Adding point series %d with %d points" % (thisIndex, len(tmp)))

                    # Create an ingredient with the same name as the file name
                    objName = "%s #%d" % (fname.split(os.path.sep)[-1], thisIndex)

                    self.lasagna.addIngredient(object_name=objName,
                                               kind=self.kind,
                                               data=np.asarray(tmp),
                                               fname=fname
                                               )

                    # Add this ingredient to all three plots
                    self.lasagna.returnIngredientByName(objName).addToPlots()

                    # Update the plots
                    self.lasagna.initialiseAxes()


            else:
                print(("Point series has %d columns. Only 3 or 4 columns are supported" % len(data[1])))


        else:
            self.lasagna.statusBar.showMessage("Unable to find " + str(fname))
