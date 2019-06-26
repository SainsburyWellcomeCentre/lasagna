"""
Functions that find and define paths for handling plugins and preferences
"""
import os


def getHomeDir():
    """
    Return the user's home directory as a string. Should work on both Windows and Linux
    See: http://stackoverflow.com/questions/10644183/how-to-store-variables-preferences-in-python-for-later-use
    """

    if os.name != "posix":
        homedir = os.path.expanduser("~")+"\\"
    else:
        homedir = "{}/".format(os.path.expanduser("~"))

    return homedir


def stripTrailingFileFromPath(path):
    """
    Given a path (e.g. '/home/user/myImage.tiff') strip the file name and return the rest of the path
    """
    path = os.path.split(path)

    path = str(path[0])
    path += os.path.sep

    if path[-1] != os.path.sep:
        path = path + os.path.sep

    return path


def stripTrailingDirFromPath(path):
    """ Remove last directory from path

        Given path /tmp/somthing/wibble/ strip "wibble" and return the rest
    """
    if path[-1] == os.path.sep:
        path = os.path.split(path)
        path = str(path[0])

    return os.path.split(path)[0]
  


def abs_path_to_lasagna():
    """
    Returns the absolute path to this module, which in turn is the absolute path to lasagna.
    This function is used for thing such as identifying the correct path for loading plugins
    packaged with lasagna.
    """

    tmp = stripTrailingFileFromPath(os.path.abspath(__file__))
    return stripTrailingDirFromPath(tmp)


def lasagna_plugins_abs_path():
    return os.path.join(abs_path_to_lasagna(), 'plugins')+os.sep
