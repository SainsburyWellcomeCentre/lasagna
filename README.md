# Lasagna - Python Volume Visualiser for 3-D data. #

## Concept ##
Lasagna is a lightweight platform for visualising for 3D volume data. Lasagna features
a flexible plugin system, allowing it to be easily extended using Python and PyQt. 
Visualisation is peformed via three linked 2D views. Lasagna was written to explore 
registration accuracy of 3D data, guide registration, and overlay point data onto images. 
It was also written to help explore the Allen Reference Atlas. Lasagna is under heavy 
development but is maturing rapidly. For more information see 
the [website](http://raacampbell13.github.io/lasagna).

### Critical upcoming features ###
The following features are receiving the most attention:

* Overlaying extracted data (e.g. cell locations, cell densities, or traced neurons) over the image stacks. 
* An overhauled axis class to allow for arbitrary data to be easily overlaid.
* Interactive exploration of Allen Reference Atlas brain areas in relation to registered brain. e.g. displaying current brain by mousing over and highlighting areas from a list.

## Installation ##
Lasagna runs on Python 2.7, PyQt4, and uses PyQtGraph for the plotting. You'll need the following modules:
* tifffile [for importing TIFF files]
* vtk [for importing MHD files]
* numpy
* pyqtgraph 9.10
* yaml
* PyQt4
* tempfile 
* urllib
