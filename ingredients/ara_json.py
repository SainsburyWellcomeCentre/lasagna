import json
import os
# http://stackoverflow.com/questions/15196449/build-a-tree-in-python-through-recursion-by-taking-in-json-object
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
    print "Importing JSON data from " + fname
    with open(fname) as f:
        obj = json.load(f)        

    return tree_builder(obj[u'msg'][0],verbose=verbose)





class Node(object):
    def __init__(self, id=None, atlas_id=None, acronym=None, name=None, color_hex_triplet=None, graph_order=0, parent_structure_id=None, level=0):
        self.id = id
        self.atlas_id = atlas_id
        self.acronym = acronym
        self.name = name
        self.color_hex_triplet = color_hex_triplet
        self.graph_order = graph_order
        self.parent_structure_id = parent_structure_id
        self.level = level
        self.children  = []

    def __repr__(self):        
        return '\n{indent}Node({component},{status},{children})'.format(
                                         indent = self.level*'  ', 
                                         component = self.id,
                                         status = self.name,
                                         children = repr(self.children))
    def add_child(self, child):
        self.children.append(child)    


def tree_builder(obj, level=0,verbose=False):
    if verbose:
        print "{id}|{parent_id}|{atlas_id}|{acronym}|{name}|{color}".format( 
                id=obj[u'id'],
                parent_id=obj[u'parent_structure_id'],
                atlas_id=obj[u'atlas_id'],
                acronym=obj[u'acronym'],
                name=obj[u'name'],
                color=obj[u'color_hex_triplet'])


    node = Node(level=level)

    for child in obj.get('children',[]):
        node.add_child(tree_builder(child, level=level+1,verbose=verbose))
    return node




#----------------------------------------------------------------------------
if __name__ == '__main__':
    tree = importData('brain_area_names.json',verbose=True)
    

