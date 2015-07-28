"""
Tools for handling the ARA
this may be imported into a plugin
"""

import csv
import os.path



def readAnnotation(fname):
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
    


#The following should eventually be read from a preferences file
def fileNames():
    return {
        'ARAdir' : '/mnt/sonastv/Data/Mrsic-Flogel/ReferenceAtlas/Osten/',
        'stackFname' : 'ORL_ARA_v2.5.3_bulbFirst.tif',
        'annotationFname' : 'ARA2_annotation_structure_info.csv'
        }
