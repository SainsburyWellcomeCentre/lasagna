# Lasagna - Python Volume Visualiser for 3-D data. #


## Concept ##
Lasagna is a lightweight platform for visualising for 3D volume data. Lasagna features
a flexible plugin system, allowing it to be easily extended using Python and PyQt. 
Visualisation is peformed via three linked 2D views. Lasagna was written to explore 
registration accuracy of 3D data, guide registration, and overlay point data onto images. 
It was also written to help explore the Allen Reference Atlas. *Lasagna is still under 
development but is usable*. For details [see the website](http://sainsburywellcomecentre.github.io/lasagna/). 

## Installation ##
Lasagna runs on Python 3, PyQt5, and uses PyQtGraph for the plotting and requires the following modules:


* PyLibTiff
* pynrrd
* numpy
* pyqtgraph >0.10.0
* MatplotLib
* yaml [and pyyaml]
* Scipy [optional - ARA explorer]
* Scikit-Image [optional - ARA explorer]
* PyQt5
* SIP
* tifffile [optional for importing LSM files]
* vtk [optional, for faster import of MHD files but doesn't work in Python 3]



On Linux you can install most of the above via your package manager
with the remaining packages being installed via `pip3` (`cd` to Lasagna
directory to run the `pip3` install line) :

```
apt-get install python3 python3-pip python3-pyqt5 python3-numpy python3-matplotlib
python3-scipy python3-sip
pip3 install -r requirements.txt --user
```

This command installs the dependencies in your home folder.
If you add the `--upgrade` flag, `pip3` will also install newer
vesions of packages already in the system path.

There is currently no `vtk` support in Python 3. 
If you run into problems try installing the dependencies separately (see below).
For other platforms, please see [here](http://raacampbell.github.io/lasagna/installation.html)

On Mac you will first need to Install [HomeBrew](http://brew.sh/)

```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

The install Python 3 and a couple of other packages without which you won't be able to install the rest of the dependencies:

```
brew install freetype pkg-config python3
```

Now you can install the dependencies in requirements.txt using:
``
pip3 install -r requirements.txt --user
``

If for some reason this fails, try installing the dependencies seperately:
```
pip3 install numpy
pip3 install matplotlib
...
```



## Setup ##
After the first run, Lasagna creates a preferences file in the ```.lasagna``` hidden directory in your home directory. 
You may need to edit this file to make Lasagna aware of its built in-plugins. i.e. edit the pluginPaths preference. 
This step isn't user-friendly, sorry.

## Usage

## Current status ##
Even the master branch is currently unstable (although should always be usable). 
