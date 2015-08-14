"""
Helper functions for lasagna. Functions in this file are involved in the following tasks:
1. Finding plot widgets by name within an object.
2. Finding paths to preferences files, etc.
3. Defining default preferences and loading and saving preferences.
"""

import os
import string
import yaml   #Preferences are stored in a YAML file


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def findPyQtGraphObjectNameInPlotWidget(PlotWidget,itemName,regex=False):
    """
    Searches a PyQtGraph PlotWidget for an plot object (i.e. something added with .addItem)
    with name "itemName"

    Inputs:
    PlotWidget - an instance of a PyQtGraph plot widget
    itemName - a string defining the .objectName to search for in PlotWidget. 
    regex - if True the itemName is treated as a regular expression. [False by default]

    Outputs:
    Returns the instance of the object bearing the chosen name. Returns None if no
    object was found. 

    Notes:
    The user must assign a sensible name to every created plot item. Added objects will
    by default have a blank object name. This function does not do a recursive search,
    so you can't feed it the GUI root object and expect an answer. It returns *ONLY* the 
    first found item.
    """

    if regex==True:
        import re

    pltItem = PlotWidget.getPlotItem()

    if not hasattr(pltItem,'items'):
        print "findPyQtGraphObjectNameInPlotWidget finds no attribute 'items'"
        return False

    if len(pltItem.items)==0:
        print "findPyQtGraphObjectNameInPlotWidget finds no items in list"
        return False


    if regex == True:
        for thisItem in pltItem.items:
            if re.search(itemName,thisItem.objectName):
               return thisItem
    else:
        for thisItem in pltItem.items:
            if thisItem.objectName == itemName:
                return thisItem


    print "Failed to find " + itemName + " in PlotWidget"
    return False


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Functions that find and define paths for handling plugins and preferences
def getHomeDir():
    """
    Return the user's home directory as a string. Should work on both Windows and Linux
    See: http://stackoverflow.com/questions/10644183/how-to-store-variables-preferences-in-python-for-later-use
    """

    if os.name != "posix":
        from win32com.shell import shellcon, shell
        homedir = "{}\\".format(shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0))
    else:
        homedir = "{}/".format(os.path.expanduser("~"))

    return homedir


def stripTrailingFileFromPath(thisPath):
    """
    Given a path (e.g. '/home/user/myImage.tiff') strip the file name and return the rest of the path
    """
    thisPath = thisPath.split(os.path.sep)
    thisPath = string.join(thisPath[:-1],os.path.sep)
    if thisPath[-1] != os.path.sep:
        thisPath = thisPath + os.path.sep

    return thisPath


def absPathToLasagna():
    """
    Returns the absolute path to this module, which in turn is the absolute path to lasagna.
    This function is used for thing such as identifying the correct path for loading plugins
    packaged with lasagna.
    """
    return stripTrailingFileFromPath(os.path.abspath(__file__))



def getLasagna_prefDir():
    """
    Returns the path to lasagna preferences directory. 
    If it does not exist it creates it and then returns the path
    """
    prefDir = getHomeDir() +'.lasagna'
    if not os.path.exists(prefDir):
        os.makedirs(prefDir)

    assert os.path.exists(prefDir)

    if os.name != "posix":
        prefDir = prefDir + '\\'
    else:
        prefDir = prefDir + '/'

    return prefDir


def getLasagnaPrefFile():
    """
    Returns the location of the main lasagna preferences file.
    It does not matter if the file does not exist, since it will be 
    created on demand by other functions. 
    """
    return getLasagna_prefDir() + 'lasagna_prefs.yml'







 #     - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -    
 #   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  
 # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
 # Functions that handle preferences
def defaultPreferences():
    """
    ** These are the default preferences **
    Return a dictionary containing the default lasagna preferences. This is necessary
    in case a particular preference is missing or the preferences file is missing.
    """
    
    return {
            'lastLoadDir' : getHomeDir() ,          #The directory from which we last loaded data
            'numRecentFiles' : 5 ,                  #The number of recently loaded file names to store
            'recentlyLoadedFiles' : [] ,            #A list containing the last "numRecentFiles" file names
            'IO_modulePaths' : [absPathToLasagna()+'IO'], #must be asbolute paths
            'pluginPaths' : [absPathToLasagna()+'tutorialPlugins', absPathToLasagna()+'ARA'], #must be asbolute paths
            'defaultAxisRatios' : [1,2,0.5],        #The default axis ratios
            'showCrossHairs' : True,                 #Whether or not to show the cross hairs 
            'colorOrder' : ['red','green','blue','magenta','cyan','yellow','gray'], #The order in which colors appear by default (see imagestack class)
            'symbolOrder' : ['o','s','t','d','+'],
            'defaultSymbolOpacity' : 180,
            'defaultSymbolSize' : 10,
            'hideZoomResetButtonOnImageAxes' : True ,
            'hideAxes' : True
            }

 # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
 #   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  
 #     - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -    




# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Functions that handle preferences
"""
The following plugin functions by default expect the name and path of the preferences file to be the 
main lasagna preferences file. However, this can be over-ridden so that indiviual plugins can have 
their own preferences files and still use these functions. 
"""

def loadAllPreferences(prefFName=getLasagnaPrefFile(),defaultPref=defaultPreferences()):
    """
    Load the preferences YAML file. If the file is missing, we create it using the default
    preferences defined above. Preferences are returned as a dictionary.
    """
    #print "loading from pref file %s" % prefFName
    #Generate a default preferences file if no preferences file exists
    if os.path.exists(prefFName) == False:
        print "PREF FILE"
        print prefFName
        writeAllPreferences(defaultPref,prefFName=prefFName)
        print "Created default preferences file in " + prefFName

    #Load preferences YAML file as a dictionary
    stream = file(prefFName, 'r')    
    return yaml.load(stream)
    stream.close()


def readPreference(preferenceName,prefFName=getLasagnaPrefFile(), preferences=getLasagnaPrefFile()):
    """
    Read preferences with key "preferenceName" from YAML file prefFName on disk.
    If the key is abstent, call defaultPreferences and search for the key. If it
    is present, add to preferences file and return the value. If absent, raise a
    warning and return None. The caller function needs to decide what to do with 
    the None. 
    """
    
    #TODO: need some sort of check as to whether the preference value is valid
    
    #Check on disk
    preferences = loadAllPreferences(prefFName)
    if preferences.has_key(preferenceName):
        return preferences[preferenceName]
    else:
        print "Did not find preference %s on disk. Looking in defaultPreferencesa" % preferenceName

    #Check in default preferences and to file and return if so
    preferences = defaultPreferences()
    if preferences.has_key(preferenceName):
        value = preferences[preferenceName]
        preferenceWriter(preferenceName,value,prefFName)
        return value
    else:
        print "Did not find preference %s in default preferences" % preferenceName







def writeAllPreferences(preferences,prefFName=getLasagnaPrefFile()):
    """
    Save the dictionary "preferences" as a YAML file in the .lasagna directory located in the 
    user's home directory. 
    """
    assert isinstance(preferences,dict)

    #TODO: check ability to write to the file before proceeding

    stream = file(prefFName, 'w')
    yaml.dump(preferences, stream)
    stream.close()


def preferenceWriter(preferenceName,newValue,prefFName=getLasagnaPrefFile()):
    """
    Overwrite a single key "preferenceName" in self.preferences with the value "newValue"
    Saves updates dictionary to the preferences file
    """
    print preferenceName
    preferences = loadAllPreferences(prefFName)
    if preferences.has_key(preferenceName):
        preferences[preferenceName] = newValue
    else:
        print "Adding missing preference %s to preferences file" % preferenceName
        preferences[preferenceName] = newValue

    writeAllPreferences(preferences,prefFName)
