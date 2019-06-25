"""
The following plugin functions by default expect the name and path of the preferences file to be the
main lasagna preferences file. However, this can be over-ridden so that individual plugins can have
their own preferences files and still use these functions.
"""

import os

import yaml

from lasagna.utils.path_utils import getHomeDir, lasagna_plugins_abs_path
from lasagna.utils.pref_utils import get_lasagna_pref_file


def defaultPreferences():
    """
    ** These are the default preferences **
    Return a dictionary containing the default lasagna preferences. This is necessary
    in case a particular preference is missing or the preferences file is missing.
    """

    return {
            'lastLoadDir': getHomeDir(),           # The directory from which we last loaded data
            'numRecentFiles': 5,                   # The number of recently loaded file names to store
            'recentlyLoadedFiles': [],             # A list containing the last "numRecentFiles" file names
            'IO_modulePaths': [ ],  # must be asbolute paths
            'pluginPaths': [lasagna_plugins_abs_path() + os.sep + 'tutorial_plugins',
                            lasagna_plugins_abs_path() + os.sep + 'registration_plugins',
                            lasagna_plugins_abs_path() + os.sep + 'ara'],  # must be asbolute paths
            'defaultAxisRatios': [1, 2, 0.5],         # The default axis ratios
            'defaultPointZSpread': [5, 5, 3],         # The range of layers over which points or lines are visible
            'showCrossHairs': True,                 # Whether or not to show the cross hairs
            'colorOrder': ['red', 'green', 'blue', 'magenta', 'cyan', 'yellow', 'gray'],  # The order in which colors appear by default (see imagestack class)
            'symbolOrder': ['o', 's', 't', 'd', '+'],
            'defaultLineWidth': 2,
            'defaultSymbolOpacity': 200,
            'defaultSymbolSize': 8,
            'hideZoomResetButtonOnImageAxes': True,
            'hideAxes': True,
            }


def loadAllPreferences(prefFName=get_lasagna_pref_file(), defaultPref=defaultPreferences()):
    """
    Load the preferences YAML file. If the file is missing, we create it using the default
    preferences defined above. Preferences are returned as a dictionary.
    """
    # print "loading from pref file %s" % prefFName
    # Generate a default preferences file if no preferences file exists
    if not os.path.exists(prefFName):
        print("PREF FILE: %s" % prefFName)
        writeAllPreferences(defaultPref, prefFName=prefFName)
        print("Created default preferences file in " + prefFName)

    # Load preferences YAML file as a dictionary
    with open(prefFName, 'r') as stream:
        return yaml.load(stream)


def readPreference(preferenceName, prefFName=get_lasagna_pref_file(), preferences=get_lasagna_pref_file()):
    """
    Read preferences with key "preferenceName" from YAML file prefFName on disk.
    If the key is abstent, call defaultPreferences and search for the key. If it
    is present, add to preferences file and return the value. If absent, raise a
    warning and return None. The caller function needs to decide what to do with
    the None.
    """

    # TODO: need some sort of check as to whether the preference value is valid

    # Check on disk
    preferences = loadAllPreferences(prefFName)
    if preferenceName in preferences:
        return preferences[preferenceName]
    else:
        print("Did not find preference %s on disk. Looking in defaultPreferencesa" % preferenceName)

    # Check in default preferences and to file and return if so
    preferences = defaultPreferences()
    if preferenceName in preferences:
        value = preferences[preferenceName]
        preferenceWriter(preferenceName, value, prefFName)
        return value
    else:
        print("Did not find preference %s in default preferences" % preferenceName)


def writeAllPreferences(preferences, prefFName=get_lasagna_pref_file()):
    """
    Save the dictionary "preferences" as a YAML file in the .lasagna directory located in the
    user's home directory.
    """
    assert isinstance(preferences, dict)

    # TODO: check ability to write to the file before proceeding
    with open(prefFName, 'w') as stream:
        yaml.dump(preferences, stream)


def preferenceWriter(preferenceName, newValue, prefFName=get_lasagna_pref_file()):
    """
    Overwrite a single key "preferenceName" in self.preferences with the value "newValue"
    Saves updates dictionary to the preferences file
    """
    print("Writing preference data for: %s\n" % preferenceName)
    preferences = loadAllPreferences(prefFName)
    if preferenceName in preferences:
        preferences[preferenceName] = newValue
    else:
        print("Adding missing preference %s to preferences file" % preferenceName)
        preferences[preferenceName] = newValue

    writeAllPreferences(preferences, prefFName)
