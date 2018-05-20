"""
Standalone core image processing functions that do not
need to be part of the volVis object. This facilitates
modifying and extending volVis without having to touch 
the main main.py file and without bloating it much.
"""


import numpy as np


def defaultHistRange(y,x):
	"""
	Returns a reasonable values for the maximum plotted value.
	y - range of values from the intensity histogram
	x - range of x values for the histogram
	"""

	#I'm sure this isn't the most robust approach but it works for now
	thresh=0.925 #find values greater than this proportion

	m = x*y
	vals = np.cumsum(m)/np.sum(m)
	vals = vals>thresh

	return x[vals.tolist().index(True)]