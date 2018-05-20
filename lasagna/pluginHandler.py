
"""
Methods to handle finding of plugins, etc
"""

from os import path, listdir 


def findPlugins(pluginPaths):
    """
    Looks for files named "*_plugin.py" in the directory list "pluginPaths"
    """

    plugins = []  # This list will contain the names of plugins found in the pluginPaths directory list
    pluginDirectories = []  # This list will contain the directories that contain valid plugins

    for thisPath in pluginPaths:
        if not path.isdir(thisPath):
            print("Plugin path " + thisPath + " is not a valid path. SKIPPING")
            continue

        # Get all files in the directory that match the plugin file name pattern
        thesePluginFiles = [f for f in listdir(thisPath) if path.isfile(path.join(thisPath, f)) and f.endswith('_plugin.py')]
        if not thesePluginFiles:
            continue

        pluginDirectories.append(thisPath)
        for thisPlugin in thesePluginFiles:
            plugins.append(thisPlugin)
    return plugins, pluginDirectories


def getPluginInstanceFromFileName(fileName, attributeToImport='plugin'):
    """
    returns a plugin instance based on a file name (e.g. myPlugin.py) that is in the python path
    this allows for dynamic loading of plugins. By default it return the plugin attribute, but this
    needn't be the case. attributeToImport is None then the module is returned instead. 
    code from: stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
    """

    parts = fileName.split('.')
    moduleName = ".".join(parts[:-1])  # trim file extension whilst retaining other dots
    importedModule = __import__(moduleName)
    if attributeToImport is not None:
        returnedAttribute = getattr(importedModule, attributeToImport)
    else:
        returnedAttribute = importedModule

    return returnedAttribute, moduleName  # return the plugin object and optionally the module name
