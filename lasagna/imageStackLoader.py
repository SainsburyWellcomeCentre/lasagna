
"""
Read MHD stacks (using the vtk library) or TIFF stacks
@author: Rob Campbell - Basel - git<a>raacampbell.com
https://github.com/raacampbell13/lasagna
"""


import re
import os
import struct 
import numpy as np
import imp #to look for the presence of a module. Python 3 will require importlib
from lasagna import lasagna_helperFunctions as lasHelp


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
    print("\n\n*" + fname + " NOT LOADED. DATA TYPE NOT KNOWN\n\n")

def saveStack(fname, data, format='tif'):
  """Save the image data
  Works only for tif for now
  """
  format = format.lower().strip().strip('.')
  if format in ['tif', 'tiff']:
    saveTiffStack(fname, data)
  else:
    raise NotImplementedError

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
  if not os.path.exists(fname):
    print("imageStackLoader.loadTiffStack can not find %s" % fname)
    return

  purePython = True
  if useLibTiff:
    from libtiff import TIFFfile
    import numpy as np
    tiff = TIFFfile(fname)
    samples, sample_names = tiff.get_samples() #we should have just one
    print("Loading:\n" + tiff.get_info() + " with libtiff\n")
    im = np.asarray(samples[0])
  else:
    print("Loading:\n" + fname + " with tifffile\n")
    from tifffile import imread 
    im = imread(fname)

  im=im.swapaxes(1,2) 
  print("read image of size: cols: %d, rows: %d, layers: %d" % (im.shape[1],im.shape[2],im.shape[0]))
  return im

def saveTiffStack(fname, data, useLibTiff = False):
    """Save data in file fname
    """
    if useLibTiff:
        raise NotImplementedError
    from tifffile import imsave
    imsave(str(fname), data.swapaxes(1,2))

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
      import vtk #Seems not exist currently for Python 3 (Jan 2017)
      from vtk.util.numpy_support import vtk_to_numpy
    except ImportError:
      print("Failed to find VTK. Falling back to built in (but slower) MHD reader")
      fallBackMode = True

  if fallBackMode:
    return mhdRead_fallback(fname)
  else:
    #use VTK
    imr = vtk.vtkMetaImageReader()
    imr.SetFileName(fname)
    imr.Update()

    im = imr.GetOutput()

    rows, cols, z = im.GetDimensions()
    sc = im.GetPointData().GetScalars()
    a = vtk_to_numpy(sc)
    a = a.reshape(z, cols, rows) 
    a = a.swapaxes(1,2)
    print("Using VTK to read MHD image of size: cols: %d, rows: %d, layers: %d" % (rows,cols,z))
    return a    


def mhdWrite(imStack,fname):
  """
  Write MHD file, updating both the MHD and raw file.
  imStack - is the image stack volume ndarray
  fname - is the absolute path to the mhd file.
  """
  imStack = np.swapaxes(imStack,1,2)
  out = mhd_write_raw_file(imStack,fname)
  if out==False:
    return False
  else:
    info=out

  #Write the mhd header file, as it may have been modified
  print("Saving image of size %s" % str(imStack.shape))
  mhd_write_header_file(fname,info)
  return True


def mhdRead_fallback(fname):
  """
  Read the header file from the MHA file then use this to 
  build a 3D stack from the raw file

  fname should be the name of the mhd (header) file
  """

  if os.path.exists(fname) == False:
    print("mha_read can not find file %s" % fname)
    return False
  else:
    info = mhd_read_header_file(fname)
    if len(info)==0:
      print("No data extracted from header file")
      return False


  if ('dimsize' in info) == False:
    print("Can not find dimension size information in MHD file. Not importing data")
    return False


  #read the raw file
  if ('elementdatafile' in info) == False:
    print("Can not find the data file as the key 'elementdatafile' does not exist in the MHD file")
    return False

  return mhd_read_raw_file(fname,info)



def mhd_read_raw_file(fname,header):
  """
  Raw .raw file associated with the MHD header file
  CAUTION: this may not adhere to MHD specs! Report bugs to author.
  """

  if 'headersize' in header:
    if header['headersize']>0:
      print("\n\n **MHD reader can not currently cope with header information in .raw file. Contact the author** \n\n")
      return False

  #Set the endian type correctly
  if 'byteorder' in header:
    if header['byteorder'].lower == 'true' :
      endian = '>' #big endian
    else:
      endian = '<' #little endian
  else:
    endian = '<' #little endian


  #Set the data type correctly 
  if 'datatype' in header:
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

  #If we couldn't find it, look in the ElenentType field
  if formatType == False:
    if 'elementtype' in header:
      datatype = header['elementtype'].lower()

      if datatype == 'met_short':
        formatType = 'h'
      else:
        formatType = False

    else:
      formatType = False



  if formatType == False:
    print("\nCan not find data format type in MHD file. **CONTACT AUTHOR**\n")
    return False


  pathToFile = lasHelp.stripTrailingFileFromPath(fname) 
  print(header['elementdatafile'])   #TODO: CLEAN THIS SHIT

  rawFname = os.path.join(pathToFile,header['elementdatafile'])
  with  open(rawFname,'rb') as fid:
    data = fid.read()
    
  dimSize = header['dimsize']
  #from: http://stackoverflow.com/questions/26542345/reading-data-from-a-16-bit-unsigned-big-endian-raw-image-file-in-python
  fmt = endian + str(int(np.prod(dimSize))) + formatType
  pix = np.asarray(struct.unpack(fmt, data))

  #Round it to keep python 3 happy 
  dimSize = [round(d) for d in dimSize]

  return pix.reshape((dimSize[2],dimSize[1],dimSize[0])).swapaxes(1,2)


def mhd_write_raw_file(imStack,fname,info=None):
  """
  Write raw MHD file.
  imStack - is the image stack volume ndarray
  fname - is the absolute path to the mhd file.
  info - is a dictionary containing imported data from the mhd file. This is optional. 
        If info is missing, we read the data from the mhd file
  """

  if info is None:
    info=mhd_read_header_file(fname)

  #Get the name of the raw file and check it exists
  path = os.path.dirname(fname)
  pathToRaw = path + os.path.sep + info['elementdatafile']

  if not os.path.exists(pathToRaw):
    print("Unable to find raw file at %s. Aborting mhd_write_raw_file" % pathToRaw)
    return False


  #replace the stack dimension sizes in the info stack in case the user changed this
  info['dimsize'] = imStack.shape[::-1] #We need to flip the list for some reason

  #TODO: the endianness is not set here or defined in the MHD file. Does this matter?
  try:
    with open(pathToRaw,'wb') as fid:
      fid.write( bytearray(imStack.ravel()) )
    return info
  except IOError:
    print("Failed to write raw file in mhd_write_raw_file")
    return False


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
    if m is None:
      continue

    key = m.groups()[0].lower() #This is the data key

    #Now we get the data
    m=re.match('\A\w+ *= * (.*) *',line)
    if m is None:
      print("Can not get data for key %s" % key)
      continue

    if len(m.groups())>1:
      print("multiple matches found during mhd_read_header_file. skipping " + key)
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


def mhd_write_header_file(fname,info):
  """
  This is a quick and very dirty, *SIMPLE*, mhd header writer. It can only cope with the fields hard-coded described below. 
  """

  fileStr = '' #Build a string that we will write to a file
  if 'ndims' in info:
    fileStr = fileStr + ('NDims = %d\n' % info['ndims'])

  if 'datatype' in info:
    fileStr = fileStr + ('DataType = %s\n' % info['datatype'])

  if 'dimsize' in info:
    numbers = ' '.join(map(str,(list(map(int,info['dimsize']))))) #convert a list of floats into a space separated series of ints
    fileStr = fileStr + ('DimSize = %s\n' % numbers)

  if 'elementsize' in info:
    numbers = ' '.join(map(str,(list(map(int,info['elementsize']))))) 
    fileStr = fileStr + ('ElementSize = %s\n' % numbers)

  if 'elementspacing' in info:
    numbers = ' '.join(map(str,(list(map(int,info['elementspacing']))))) 
    fileStr = fileStr + ('ElementSpacing = %s\n' % numbers)

  if 'elementtype' in info:
    fileStr = fileStr + ('ElementType = %s\n' % info['elementtype'])
  
  if 'elementbyteordermsb' in info:
    fileStr = fileStr + ('ElementByteOrderMSB = %s\n' % str(info['elementbyteordermsb']))

  if 'elementdatafile' in info:
    fileStr = fileStr + ('ElementDataFile = %s\n' % info['elementdatafile'])


  #If we're here, then hopefully things went well. We write to the file
  with open (fname,'w') as fid:
    fid.write(fileStr)


def mhd_getRatios(fname):
  """
  Get relative axis ratios from MHD file defined by fname
  """
  if not os.path.exists(fname):
    print("imageStackLoader.mhd_getRatios can not find %s" % fname)
    return
    
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
    if 'elementspacing' in info:
      spacing = info['elementspacing']
    else:
      print("Failed to find spacing info in MHA file. Using default axis length values")      
      return lasHelp.readPreference('defaultAxisRatios') #defaults


  if len(spacing)==0: 
    print("Failed to find spacing valid spacing info in MHA file. Using default axis length values")      
    return lasHelp.readPreference('defaultAxisRatios') #defaults
  
  return spacingToRatio(spacing)  



#-------------------------------------------------------------------------------------------
#   *NRRD handling methods*
def nrrdRead(fname):
  """
  Read NRRD file
  """
  if not os.path.exists(fname):
    print("imageStackLoader.nrrdRead can not find %s" % fname)
    return

  import nrrd 
  (data,header) = nrrd.read(fname)
  return data.swapaxes(1,2)


def nrrdHeaderRead(fname):
  """
  Read NRRD header
  """
  if not os.path.exists(fname):
    print("imageStackLoader.nrrdHeaderRead can not find %s" % fname)
    return

  import nrrd
  with open(fname,'rb') as fid:
    header = nrrd.read_header(fid)

  return header


def nrrd_getRatios(fname):
  """
  Get the aspect ratios from the NRRD file
  """
  if not os.path.exists(fname):
    print("imageStackLoader.nrrd_getRatios can not find %s" % fname)
    return

  header = nrrdHeaderRead(fname)
  axSizes = header['space directions']

  spacing =[]
  for ii in range(len(axSizes)):
    spacing.append(axSizes[ii][ii])

  return spacingToRatio(spacing)
