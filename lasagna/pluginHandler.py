
"""
Methods to handle finding of plugins, etc
"""
import os


def findPlugins(pluginPaths):
    """
    Looks for files named "*_plugin.py" in the directory list "pluginPaths"
    """

    plugins = []  # This list will contain the names of plugins found in the pluginPaths directory list
    plugin_directories = []  # This list will contain the directories that contain valid plugins

    for plugin_folder in pluginPaths:
        if not os.path.isdir(plugin_folder):
            print("Plugin path {} is not a valid path. SKIPPING".format(plugin_folder))
            continue

        # Get all files in the directory that match the plugin file name pattern
        plugin_files = [f for f in os.listdir(plugin_folder) if is_plugin_file(plugin_folder, f)]
        if not plugin_files:
            continue

        plugin_directories.append(plugin_folder)
        plugins.extend(plugin_files)
    return plugins, plugin_directories


def is_plugin_file(file_path, f):
    return os.path.isfile(os.path.join(file_path, f)) and f.endswith('_plugin.py')


def getPluginInstanceFromFileName(fileName, attributeToImport='plugin'):
    """
    returns a plugin instance based on a file name (e.g. myPlugin.py) that is in the python path
    this allows for dynamic loading of plugins. By default it return the plugin attribute, but this
    needn't be the case. attributeToImport is None then the module is returned instead. 
    code from: stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
    """

    module_name = os.path.splitext(fileName)[0]
    imported_module = __import__(module_name)
    if attributeToImport is not None:
        returned_attribute = getattr(imported_module, attributeToImport)
    else:
        returned_attribute = imported_module

    return returned_attribute, module_name  # return the plugin object and optionally the module name
