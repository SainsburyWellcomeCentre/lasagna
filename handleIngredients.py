"""
Functions for handling ingredients

TODO: ingredients can only be handled if they are in the ingredients module
ingredients defined in plugin directories, etc, can not be handled by this 
module. This potentially makes plugin creation awkward as it couples it too
strongly to the core code (new ingredients must be added to the ingredients
module). This may turn out to not be a problem in practice, so we leave 
things for now and play it by ear. 
"""

import ingredients


def addIngredient(ingredientList=[], kind='', objectName='', data=None, fname=''):
    """
    Adds an ingredient to the list of ingredients.
    Scans the list of ingredients to see if an ingredient is already present. 
    If so, it removes it before adding a new one with the same name. 
    ingredients are classes that are defined in the ingredients package
    """

    if len(kind)==0:
        print "ERROR: no ingredient kind specified"
        return

    #Do not attempt to add an ingredient if its class is not defined
    if not hasattr(ingredients,kind):
        print "ERROR: ingredients module has no class '%s'" % kind
        return

    removeIngredient(objectName)

    #Get ingredient of this class from the ingredients package
    ingredientClassObj = getattr(getattr(ingredients,kind),kind)
    ingredientList.append(ingredientClassObj(
                            fnameAbsPath=fname,
                            data=data,
                            objectName=objectName
                    )
                )

    return ingredientList


def removeIngredient(ingredientList=[], objectName=''):
    """
    Finds ingredient by name and removes it
    """
    if len(objectName)==0:
        return

    for thisIngredient in ingredientList[:]:
        if thisIngredient.__module__.endswith(objectName):
            print 'Removing ingredient ' + objectName
            #TODO: also remove item from ViewBox and maybe also call a destructor
            print "TODO: also need to remove item from ViewBox"
            ingredientList.remove(thisIngredient)

    return ingredientList


def listIngredients(ingredientList=[]):
    """
    Return a list of ingredient objectNames
    """
    ingredientNames = [] 
    for thisIngredient in ingredientList:
        ingredientNames.append(thisIngredient.objectName)

    return ingredientNames


def returnIngredientByName(objectName,ingredientList=[]):
    """
    Return a specific ingredient based upon its object name.
    Returns False if the ingredient was not found
    """
    verbose = 0
    if len(ingredientList)==0:
        if verbose:
            print "returnIngredientByName finds no ingredients in list!"
        return False

    for thisIngredient in ingredientList:
        if thisIngredient.objectName == objectName:
            return thisIngredient

    if verbose:
        print "returnIngredientByName finds no ingredient called " + objectName
    return False
