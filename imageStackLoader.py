
"""
Read MHD stacks (using the vtk library) or TIFF stacks
@author: Rob Campbell
"""


from __future__ import division
import vtk
from vtk.util.numpy_support import vtk_to_numpy


def loadTiffStack(fname):
  """
  Read a TIFF stack.
  Bugs: known to fail with tiffs produced by Icy [23/07/15]

  """
  #I think TIFF3D uses libtiff whereas TIFFfile is pure python. Provide both options
  purePython = True
  if purePython:
    from libtiff import TIFF3D
    tiff3d = TIFF3D.open(fname)
    print "Loading:\n" + tiff3d.info() + "\n"
    im = tiff3d.read_image()
    tiff3d.close()
  else:
    from libtiff import TIFFfile
    import numpy as np
    tiff = TIFFfile(fname)
    samples, sample_names = tiff.get_samples() #we should have just one
    print "Loading:\n" + tiff.get_info() + "\n"
    im = np.asarray(samples[0])

  print "read image of size: rows: %d, cols: %d, layers: %d" % (im.shape[1],im.shape[2],im.shape[0])
  return im


def mhdRead(fname):
  """
  Read an MHD file
  """
  imr = vtk.vtkMetaImageReader()
  imr.SetFileName(fname)
  imr.Update()

  im = imr.GetOutput()
  rows, cols, z = im.GetDimensions()
  sc = im.GetPointData().GetScalars()
  a = vtk_to_numpy(sc)

  print "Reading MHD image of size: rows: %d, cols: %d, layers: %d" % (rows,cols,z)

  return a.reshape(z, cols, rows) #TODO: Inverted from example I found. Why? Did I fuck up?


def getVoxelSpacing(fname):
  """
  Attempts to get the voxel spacing in all three dimensions. This allows us to set the axis
  ratios automatically. TODO: Currently this will only work for MHD files, but we may be able 
  to swing something for TIFFs (e.g. by creating Icy-like metadata files)
  """
  from lasagna_helperFunctions import readPreference

  if fname.lower().endswith('.mhd'):
    imr = vtk.vtkMetaImageReader()
    imr.SetFileName(fname)
    imr.Update()
  
    im = imr.GetOutput()
    spacing = im.GetSpacing()

    if len(spacing)==0: 
      return readPreference('defaultAxisRatios') #defaults
    
    #Determine the ratios from the spacing 
    ratios = [1,1,1]
    
    ratios[0] = spacing[0]/spacing[1]
    ratios[1] = spacing[2]/spacing[0]
    ratios[2] = spacing[1]/spacing[2]
    return ratios

  else:
    return readPreference('defaultAxisRatios') #defaults


def loadStack(fname):
  """
  loadStack determines the data type from the file extension determines what data are to be 
  loaded and chooses the approproate function to return the data.
  """
  if fname.lower().endswith('.tif') or fname.lower().endswith('.tiff'):
    return loadTiffStack(fname)
  elif fname.lower().endswith('.mhd'):
    return mhdRead(fname)
  else:
    print fname + " not loaded. data type unknown"

