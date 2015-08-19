import json
import os
import sys
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



def tree_flatten(obj,flattened=''):
    if obj[u'parent_structure_id']==None:
        obj[u'parent_structure_id']=0

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
    if len(sys.argv)>1:
        fname = sys.argv[1]

    flattened = importData(fname)
    print flattened
