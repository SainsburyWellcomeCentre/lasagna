"""
Tools for handling the ARA
this may be imported into a plugin
"""

import csv
import os.path
import lasagna_helperFunctions as lasHelp # Module the provides a variety of import functions (e.g. preference file handling)
import yaml 

def readAnnotation(fname):
    """
    Read a brain annotation file and return it as an index
    """
    try:  
        assert os.path.isfile(fname)
    except:
        print "Failed to find " + fname
        return

    areas={}
    with open(fname) as csvfile:
        ARA = csv.reader(csvfile, delimiter='|')
        csv_headings = next(ARA)
        for row in ARA:
            areaIndex = int(row[0])
            areas[areaIndex] = row[1]

    return areas
    

def getARAPrefFile():
    """
    Returns the location of the main lasagna preferences file.
    It does not matter if the file does not exist, since it will be 
    created on demand by other functions.
    """
    return lasHelp.getLasagna_prefDir() + 'ARA_prefs.yml'


def defaultPrefs():
    """
    Return default preferences in the YAML file in this directory
    """
    stream = file('ARA_prefs.yml', 'r')
    Y = yaml.load(stream)
    stream.close()
    return Y


#The following should eventually be read from a preferences file
def fileNames():
    return {
        'ARAdir' : '/mnt/sonastv/Data/Mrsic-Flogel/ReferenceAtlas/Osten/',
        'stackFname' : 'ORL_ARA_v2.5.3_bulbFirst.tif',
        'annotationFname' : 'ARA2_annotation_structure_info.csv'
        }
