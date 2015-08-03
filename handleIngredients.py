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

    print "Adding ingredient " + objectName

    if len(kind)==0:
        print "ERROR: no ingredient kind specified"
        return

    #Do not attempt to add an ingredient if its class is not defined
    if not hasattr(ingredients,kind):
        print "ERROR: ingredients module has no class '%s'" % kind
        return

    #If an ingredient with this object name is already present we delete it
    ingredientList = removeIngredientByName(objectName,ingredientList)

    #Get ingredient of this class from the ingredients package
    ingredientClassObj = getattr(getattr(ingredients,kind),kind)
    ingredientList.append(ingredientClassObj(
                            fnameAbsPath=fname,
                            data=data,
                            objectName=objectName
                    )
                )

    return ingredientList


def removeIngredientByName(objectName, ingredientList=[]):
    """
    Finds ingredient by name and removes it from the list
    """

    verbose = False
    if len(ingredientList)==0:
        if verbose:
            print "removeIngredientByType finds no ingredients in list!"
        return ingredientList

    removedIngredient=False
    for thisIngredient in ingredientList[:]:
        if thisIngredient.objectName == objectName:
            if verbose:
                print 'Removing ingredient ' + objectName
            ingredientList.remove(thisIngredient)
            removedIngredient=True

    if removedIngredient == False & verbose==True:
        print "** Failed to remove ingredient %s **" % objectName
    return ingredientList


def removeIngredientByType(ingredientType, ingredientList=[]):
    """
    Finds ingredient by type and removes it
    """
    verbose = False
    if len(ingredientList)==0:
        if verbose:
            print "removeIngredientByType finds no ingredients in list!"
        return ingredientList

    for thisIngredient in ingredientList[:]:
        if thisIngredient.__module__.endswith(ingredientType):
            if verbose:
                print 'Removing ingredient ' + thisIngredient.objectName

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


def returnIngredientByType(ingredientType,ingredientList=[]):
    """
    Return a list of ingredients based upon their type. e.g. imagestack, sparsepoints, etc
    """
    verbose = False
    if len(ingredientList)==0:
        if verbose:
            print "returnIngredientByType finds no ingredients in list!"
        return False

    returnedIngredients=[]
    for thisIngredient in ingredientList:
        if thisIngredient.__module__.endswith(ingredientType):
            returnedIngredients.append(thisIngredient)


    if verbose and len(returnedIngredients)==0:
        print "returnIngredientByType finds no ingredients with type " + ingredientType
        return False
    else:
        return returnedIngredients


def returnIngredientByName(objectName,ingredientList=[]):
    """
    Return a specific ingredient based upon its object name.
    Returns False if the ingredient was not found
    """
    verbose = False
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
