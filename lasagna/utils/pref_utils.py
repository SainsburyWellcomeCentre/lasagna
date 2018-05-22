import os

from lasagna.utils.path_utils import getHomeDir


def get_lasagna_pref_dir():
    """
    Returns the path to lasagna preferences directory.
    If it does not exist it creates it and then returns the path
    """
    pref_dir = getHomeDir() + '.lasagna'
    if not os.path.exists(pref_dir):
        os.makedirs(pref_dir)

    assert os.path.exists(pref_dir)

    if os.name != "posix":
        pref_dir = pref_dir + '\\'
    else:
        pref_dir = pref_dir + '/'

    return pref_dir


def get_lasagna_pref_file():
    """
    Returns the location of the main lasagna preferences file.
    It does not matter if the file does not exist, since it will be
    created on demand by other functions.
    """
    return get_lasagna_pref_dir() + 'lasagna_prefs.yml'
