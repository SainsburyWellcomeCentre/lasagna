import json
import os

"""
Dumps ARA JSON as a flattened file that we can feed into our tree reader
"""


def importData(fname,verbose=False):
    """
    Import from ARA JSON
    """

    #Error check
    if os.path.exists(fname)==False:
        print "Can not find file " + fname
        return

    if fname.lower().endswith('json')==False:
        print "Data should be a JSON file"
        return

    #Build tree
    with open(fname) as f:
        obj = json.load(f)        

    return tree_flatten(obj[u'msg'][0])





class Node(object):
    def __init__(self, id=0, atlas_id=0, acronym=None, name=None, color_hex_triplet=None, graph_order=0, parent_structure_id=None, level=0):
        self.id = id
        self.atlas_id = atlas_id
        self.acronym = acronym
        self.name = name
        self.color_hex_triplet = color_hex_triplet
        self.graph_order = graph_order
        self.parent_structure_id = parent_structure_id
        self.level = level
        self.children  = []

    


def tree_flatten(obj,flattened=''):
    flattened = flattened+"{id}|{parent_id}|{atlas_id}|{acronym}|{name}|{color}\n".format( 
            id=obj[u'id'],
            parent_id=obj[u'parent_structure_id'],
            atlas_id=obj[u'atlas_id'],
            acronym=obj[u'acronym'],
            name=obj[u'name'],
            color=obj[u'color_hex_triplet'])

    for child in obj.get('children',[]):
        flattened = tree_flatten(child,  flattened=flattened)

    return flattened




#----------------------------------------------------------------------------
if __name__ == '__main__':
    flattened = importData('brain_area_names.json') #True to dump to standard output 
    print flattened
