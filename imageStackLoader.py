
"""
Read MHD stacks (using the vtk library) or TIFF stacks
@author: Rob Campbell - Basel - git<a>raacampbell.com
https://github.com/raacampbell13/lasagna
"""

from __future__ import division
import re
import os
import struct 
import numpy as np
import imp #to look for the presence of a module. Python 3 will require importlib
import lasagna_helperFunctions as lasHelp 


#-------------------------------------------------------------------------------------------
#   *General methods*
# The methods in this section are the ones that are called by by Lasagna or are called by other
# functions in this module. They determine the correct loader methods, etc, for the file format 
# so that Lasagna doesn't have to know about this. 

def loadStack(fname):
  """
  loadStack determines the data type from the file extension determines what data are to be 
  loaded and chooses the approproate function to return the data.
  """
  if fname.lower().endswith('.tif') or fname.lower().endswith('.tiff'):
    return loadTiffStack(fname)
  elif fname.lower().endswith('.mhd'):
    return mhdRead(fname)
  elif fname.lower().endswith('.nrrd') or fname.lower().endswith('.nrd'):
    return nrrdRead(fname)
  else:
    print "\n\n*" + fname + " NOT LOADED. DATA TYPE NOT KNOWN\n\n"


def imageFilter():
  """
  Returns a string defining the filter for the Qt Loader dialog. 
  As image formats are added (or removed) from this module, this 
  string should be manually modified accordingly.
  """
  return "Images (*.mhd *.tiff *.tif *.nrrd *.nrd)"


def getVoxelSpacing(fname,fallBackMode=False):
  """
  Attempts to get the voxel spacing in all three dimensions. This allows us to set the axis
  ratios automatically. TODO: Currently this will only work for MHD files, but we may be able 
  to swing something for TIFFs (e.g. by creating Icy-like metadata files)
  """

  if fname.lower().endswith('.mhd'):
    return mhd_getRatios(fname)
  if fname.lower().endswith('.nrrd') or fname.lower().endswith('.nrd'):  
    return nrrd_getRatios(fname)
  else:
    return lasHelp.readPreference('defaultAxisRatios') #defaults


def spacingToRatio(spacing):
  """
  Takes a vector of axis spacings and converts it to ratios
  so Lasagna can plot the images correctly
  Expects spacing to have a length of 3
  """
  assert len(spacing) == 3

  ratios = [0,0,0]
  ratios[0] = spacing[0]/spacing[1]
  ratios[1] = spacing[2]/spacing[0]
  ratios[2] = spacing[1]/spacing[2]
  return ratios


#-------------------------------------------------------------------------------------------
#   *TIFF handling methods*
def loadTiffStack(fname,useLibTiff=False):
  """
  Read a TIFF stack.
  We're using tifflib by default as, right now, only this works when the application is compile on Windows. [17/08/15]
  Bugs: known to fail with tiffs produced by Icy [23/07/15]

  """
  purePython = True
  if useLibTiff:
    from libtiff import TIFFfile
    import numpy as np
    tiff = TIFFfile(fname)
    samples, sample_names = tiff.get_samples() #we should have just one
    print "Loading:\n" + tiff.get_info() + " with libtiff\n"
    im = np.asarray(samples[0])
  else:
    print "Loading:\n" + fname + " with tifffile\n"
    from tifffile import imread 
    im = imread(fname)

  print "read image of size: rows: %d, cols: %d, layers: %d" % (im.shape[1],im.shape[2],im.shape[0])
  return im



#-------------------------------------------------------------------------------------------
#   *MHD handling methods*
def mhdRead(fname,fallBackMode = False):
  """
  Read an MHD file using either VTK (if available) or the slower-built in reader
  if fallBackMode is true we force use of the built-in reader
  """
  if fallBackMode == False: 
    #Attempt to load vtk
    try:
      imp.find_module('vtk')
      import vtk
      from vtk.util.numpy_support import vtk_to_numpy
    except ImportError:
      print "Failed to find VTK. Falling back to built in (but slower) MHD reader"
      fallBackMode = True

  if fallBackMode:
    return mhd_read_fallback(fname)
  else:
    #use VTK
    imr = vtk.vtkMetaImageReader()
    imr.SetFileName(fname)
    imr.Update()

    im = imr.GetOutput()
    rows, cols, z = im.GetDimensions()
    sc = im.GetPointData().GetScalars()
    a = vtk_to_numpy(sc)
    print "Using VTK to read MHD image of size: rows: %d, cols: %d, layers: %d" % (rows,cols,z)
    return a.reshape(z, cols, rows) #TODO: Inverted from example I found. Why? Did I fuck up?


def mhd_read_fallback(fname):
  """
  Read the header file from the MHA file then use this to 
  build a 3D stack from the raw file

  fname should be the name of the mhd (header) file
  """

  if os.path.exists(fname) == False:
    print "mha_read can not find file %s" % fname
    return False
  else:
    info = mhd_read_header_file(fname)
    if len(info)==0:
      print "No data extracted from header file"
      return False


  if info.has_key('dimsize') == False:
    print "Can not find dimension size information in MHD file. Not importing data"
    return False


  #read the raw file
  if info.has_key('elementdatafile') == False:
    print "Can not find the data file as the key 'elementdatafile' does not exist in the MHD file"
    return False

  return mhd_read_raw_file(info)


def mhd_read_raw_file(header):
  """
  Raw .raw file associated with the MHD header file
  CAUTION: this may not adhere to MHD specs! Report bugs to author.
  """

  if header.has_key('headersize'):
    if header['headersize']>0:
      print "\n\n **MHD reader can not currently cope with header information in .raw file. Contact the author** \n\n"
      return False

  #Set the endian type correctly
  if header.has_key('byteorder'):
    if header['byteorder'].lower == 'true' :
      endian = '>' #big endian
    else:
      endian = '<' #little endian
  else:
    endian = '<' #little endian


  #Set the data type correctly 
  if header.has_key('datatype'):
    datatype = header['datatype'].lower()

    if datatype == 'float':
      formatType = 'f'
    elif datatype == 'double':
      formatType = 'd'
    elif datatype == 'long':
      formatType = 'l'
    elif datatype == 'ulong':
      formatType = 'L'
    elif datatype == 'char':
      formatType = 'c'
    elif datatype == 'uchar':
      formatType = 'B'
    elif datatype == 'short':
      formatType = 'h'      
    elif datatype == 'ushort':
      formatType = 'H'      
    elif datatype == 'int':
      formatType = 'i'      
    elif datatype == 'uint':
      formatType = 'I'
    else:
      formatType = False

  else:
      formatType = False

  if formatType == False:
    print "\nCan not find data format type in MHD file. **CONTACT AUTHOR**\n"
    return False



  rawFname = header['elementdatafile']
  with  open(rawFname,'rb') as fid:
    data = fid.read()
    
  dimSize = header['dimsize']
  #from: http://stackoverflow.com/questions/26542345/reading-data-from-a-16-bit-unsigned-big-endian-raw-image-file-in-python
  fmt = endian + str(int(np.prod(dimSize))) + formatType
  pix = np.asarray(struct.unpack(fmt, data))
  
  return pix.reshape((dimSize[2],dimSize[1],dimSize[0]))


def mhd_read_header_file(fname):
  """
  Read an MHD plain text header file and return contents as a dictionary
  """

  mhd_header = dict()
  mhd_header['FileName'] = fname

  with open(fname,'r') as fid:
    contents = fid.read()


  info = dict() #header data stored here

  for line in contents.split('\n'):
    if len(line)==0:
      continue

    m=re.match('\A(\w+)',line)
    if m == None:
      continue

    key = m.groups()[0].lower() #This is the data key

    #Now we get the data
    m=re.match('\A\w+ *= * (.*) *',line)
    if m == None:
      print "Can not get data for key %s" % key
      continue

    if len(m.groups())>1:
      print "multiple matches found during mhd_read_header_file. skipping " + key
      continue

    #If we're here, we found reasonable data
    data = m.groups()[0] 

    #If there are any characters not associated with a number we treat as a string and add to the dict
    if re.match('.*[^0-9 \.].*',data) != None:
      info[key] = data
      continue

    #Otherwise we have a single number of a list of numbers in space-separated form. 
    #So we return these as a list or a single number. We convert everything to float just in
    #case it's not an integer. 
    data = data.split(' ')
    numbers = []
    for number in data:
      if len(number)>0:
        numbers.append(float(number))

    #If the list has just one number we return an int
    if len(numbers)==1:
      numbers = float(numbers[0])

    info[key] = numbers

  return info


def writeMHD(fname,info):
  """
  This is a quick and very dirty, *SIMPLE*, mha writer. It can only cope with the fields hard-coded described below. 
  """

  fileStr = '' #Build a string that we will write to a file
  if info.has_key('ndims'):
    fileStr = fileStr + ('NDims = %d\n' % info['ndims'])

  if info.has_key('datatype'):
    fileStr = fileStr + ('DataType = %s\n' % info['datatype'])

  if info.has_key('dimsize'):
    numbers = ' '.join(map(str,(map(int,info['dimsize'])))) #convert a list of floats into a space separated series of ints
    fileStr = fileStr + ('DimSize = %s\n' % numbers)

  if info.has_key('elementsize'):
    numbers = ' '.join(map(str,(map(int,info['elementsize'])))) 
    fileStr = fileStr + ('ElementSize = %s\n' % numbers)

  if info.has_key('elementspacing'):
    numbers = ' '.join(map(str,(map(int,info['elementspacing'])))) 
    fileStr = fileStr + ('ElementSpacing = %s\n' % numbers)

  if info.has_key('elementType'):
    numbers = ' '.join(map(str,(map(int,info['elementtype'])))) 
    fileStr = fileStr + ('ElementType = %s\n' % numbers)

  if info.has_key('elementbyteordermsb'):
    fileStr = fileStr + ('ElementByteOrderMSB = %s\n' % str(info['elementbyteordermsb']))

  if info.has_key('elementdatafile'):
    fileStr = fileStr + ('ElementDataFile = %s\n' % info['elementdatafile'])


  #If we're here, then hopefully things went well. We write to the file
  with open (fname,'w') as fid:
    fid.write(fileStr)


def mhd_getRatios(fname):
  """
  Get relative axis ratios from MHD file defined by fname
  """
  try:
    #Attempt to use the vtk module to read the element spacing
    imp.find_module('vtk')
    import vtk
    imr = vtk.vtkMetaImageReader()
    imr.SetFileName(fname)
    imr.Update()
 
    im = imr.GetOutput()
    spacing = im.GetSpacing()    
  except ImportError:
    #If the vtk module fails, we try to read the spacing using the built-in reader
    info = mhd_read_header_file(fname)
    if info.has_key('elementspacing'):
      spacing = info['elementspacing']
    else:
      print "Failed to find spacing info in MHA file. Using default axis length values"      
      return lasHelp.readPreference('defaultAxisRatios') #defaults


  if len(spacing)==0: 
    print "Failed to find spacing valid spacing info in MHA file. Using default axis length values"      
    return lasHelp.readPreference('defaultAxisRatios') #defaults
  
  return spacingToRatio(spacing)  



#-------------------------------------------------------------------------------------------
#   *NRRD handling methods*
def nrrdRead(fname):
  """
  Read NRRD file
  """
  import nrrd 
  (data,header) = nrrd.read(fname)
  return data


def nrrdHeaderRead(fname):
  """
  Read NRRD header
  """

  import nrrd
  with open(fname,'rb') as fid:
    header = nrrd.read_header(fid)

  return header


def nrrd_getRatios(fname):
  """
  Get the aspect ratios from the NRRD file
  """
  header = nrrdHeaderRead(fname)
  axSizes = header['space directions']

  spacing =[]
  for ii in range(len(axSizes)):
    spacing.append(axSizes[ii][ii])

  return spacingToRatio(spacing)
