"""
This class defines the basic imagestack and instructs lasagna as to how to handle image stacks.
TODO: once this is working, pull out the general purpose stuff and set up an ingredient class that this inherits
"""

from __future__ import division
import numpy as np
import os

class imagestack(object):
	def __init__(self, data=None, fnameAbsPath='', enable=True, objectName='', minMax=[0,2E3]):

		#Assign input arguments to properties of the class instance. 
		#The following properties are common to all ingredients
		self.__data 	= data			 	#The raw data for this ingredient go here.
		self.fnameAbsPath = fnameAbsPath	#Absolute path to file name
		self.enable 	= enable			#Item is plotted if enable is True. Hidden if enable is False
		self.objectName = objectName		#The name of the object TODO: decide exactly what this will be


		#Set up class-specific properties, which classes other than image stack may not share
		#or may share but have different values assigned
		self.pgObject = 'ImageItem' #The PyQtGraph item type which will display the data

		self.minMax = minMax
		#TODO: need some way of setting up ImageItem properties such as border and levels




	def fname(self):
		"""
		Strip the absolute path and return only the file name as as a string
		"""
		return self.fnameAbsPath.split(os.path.sep)[-1]




	# TODO: farm out preceeding stuff to a general-purpose ingredient class 
	# Methods that follow are specific to the imagestack class. Methods that preceed this
	# are general-purpose and can be part of an "ingredient" class
	def data(self,axisToPlot=0):
		"""
		Returns data formated in the correct way for plotting in the axes that 
		requested it.
		axisToPlot defines the data dimension along which we are plotting the data.
		specifically, axisToPlot is the dimension that is treated as the z-axis
		"""
		return self.__data.swapaxes(0,axisToPlot)


	def plotIngredient(self,pyqtObject,axisToPlot=0,sliceToPlot=0):
		"""
		Plots the ingredient onto pyqtObject along axisAxisToPlot,
		onto the object with which it is associated
		"""
		data = self.data(axisToPlot)
		pyqtObject.setImage(data[sliceToPlot], levels=self.minMax)



	def defaultHistRange(self,logY=False):
		"""
		Returns a reasonable values for the maximum plotted value.
		logY if True we log the Y values
		"""

		(y,x) = np.histogram(self.data(),bins=100)

		if logY==True:
			y=np.log10(y+0.1)

		
		#I'm sure this isn't the most robust approach but it works for now
		thresh=0.925 #find values greater than this proportion

		y=np.append(y,0)

		m = x*y
		vals = np.cumsum(m)/np.sum(m)
		vals = vals>thresh

		return x[vals.tolist().index(True)]


