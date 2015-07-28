# Lasagna - Python Volume Visualiser for 3-D data. #

## Concept ##
lasagna is a prototype of a lightweight Python [VV](http://www.creatis.insa-lyon.fr/rio/vv) clone. lasagna works on 3-D image stacks that can be loaded entirely into RAM. Very large data sets will need to be downsampled. lasagna allows the user to visualise data as three linked 2-D views. The views are linked such that they all zoom and pan together. Moving the mouse cursor in one view controls which slice (of the 3-D volume) is displayed in the other two views. The viewer is *only a prototype* but it works well.

## Current features
* Interactive exploration of one 3D volume. 
* Overlay of a second volume onto the first. Useful for assessing the degree of alignment between two 3D samples. 
* Loading of either TIFF stacks or MHD files, so can work well with [Elastix](http://elastix.isi.uu.nl/). 
* Interactive exploration of the ARA brain areas through a simple plugin.
* A simple plugin system: Python scripts with a particular format located in a particular directory are made accessible via a "Plugins" menu and can modify the behavior of lasagna by calling existing methods or modifying those methods via hooks. 
* The zoom can be reset via a button and the scale modified by sliders on top of an image intensity histogram.


## Critical upcoming features ##
For the program to be useful, we must implement the following features:

* Overlaying extracted data (e.g. cell locations, cell densities, or traced neurons) over the image stacks. 
* An overhauled axis class to allow for arbitrary data to be easily overlaid.
* Interactive exploration of Allen Reference Atlas brain areas in relation to registered brain. e.g. displaying current brain by mousing over and highlighting areas from a list.
