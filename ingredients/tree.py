

(_ROOT, _DEPTH, _BREADTH) = range(3)


class Tree(object):
    """
    A simple tree class
    """

    def __init__(self):
        self.__nodes = {}

    @property
    def nodes(self):
        return self.__nodes

    def add_node(self, identifier, parent=None):
        node = Node(identifier)
        self[identifier] = node

        if parent is not None:
            self[parent].add_child(identifier)

        return node


    def display(self, identifier, depth=_ROOT):
        """
        Very (very) simple tree display
        """
        children = self[identifier].children
        if depth == _ROOT:
            print("{0}".format(identifier))
        else:
            print("    "*depth, "{0}".format(identifier))

        depth += 1
        for child in children:
            self.display(child, depth)  # recursive call


    def traverse(self, identifier, mode=_DEPTH):
        """
        traverse the tree in depth first or width first modes
        using a yield-based generator
        """
        # Python generator using yield
        yield identifier #return the root first 
        queue = self[identifier].children
        while queue:
            yield queue[0]
            expansion = self[queue[0]].children
            if mode == _DEPTH:
                queue = expansion + queue[1:]  # depth-first
            elif mode == _BREADTH:
                queue = queue[1:] + expansion  # width-first



    def __getitem__(self, key):
        return self.__nodes[key]


    def __setitem__(self, key, item):
        self.__nodes[key] = item



class Node(object):
    """
    A simple node class
    """
    def __init__(self, identifier, data=None):
        self.__identifier = identifier
        self.__children = []
        self.__data = data #The node's data payload. Can be anything.

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self,value):
        self.__data = value
    
    @property
    def identifier(self):
        return self.__identifier

    @property
    def children(self):
        return self.__children

    def add_child(self, identifier):
        self.__children.append(identifier)





#Generate an example if run from the command line
if __name__ == '__main__':

    from tree import Tree

    (_ROOT, _DEPTH, _BREADTH) = range(3)

    print "\n\n   --------- Tree of life --------- \n"
    treeOfLife = Tree()

    treeOfLife.add_node("Life")  # root node
    treeOfLife.add_node("Archaebacteria", "Life")
    treeOfLife.add_node("Eukaryotes", "Life")
    treeOfLife.add_node("Protista", "Eukaryotes")
    treeOfLife.add_node("Plants", "Eukaryotes")
    treeOfLife.add_node("Fungi", "Eukaryotes")
    treeOfLife.add_node("Algae", "Plants")
    treeOfLife.add_node("Mosses", "Plants")
    treeOfLife.add_node("Ferns", "Plants")
    treeOfLife.add_node("Animals", "Eukaryotes")
    treeOfLife.add_node("Sponges","Animals")
    treeOfLife.add_node("Flatworms","Animals")
    treeOfLife.add_node("Arthropods","Animals")
    treeOfLife.add_node("Insects","Arthropods")
    treeOfLife.add_node("Crustaceans","Arthropods")
    treeOfLife.add_node("Vertebrates","Animals")
    treeOfLife.add_node("Fish","Vertebrates")
    treeOfLife.add_node("Amphibians","Vertebrates")
    treeOfLife.add_node("Reptiles","Vertebrates")
    treeOfLife.add_node("Mammals","Vertebrates")


    #Add some data to the vertebrates
    treeOfLife["Vertebrates"].data = 'they have backbones'
    treeOfLife["Fish"].data = 'they swim'
    treeOfLife["Amphibians"].data = 'they croak'
    treeOfLife["Reptiles"].data = 'they stick to walls'
    treeOfLife["Mammals"].data = 'they have udders'


    treeOfLife.display('Life')

    print("\n***** DEPTH-FIRST ITERATION *****")
    for nodeID in treeOfLife.traverse("Life"):
        print(nodeID)

    print("\n***** BREADTH-FIRST ITERATION *****")
    for node in treeOfLife.traverse("Life", mode=_BREADTH):
        print(nodeID)

    print("\n***** BREADTH-FIRST ITERATION OF DATA IN ALL VERTEBRATES *****")
    for nodeID in treeOfLife.traverse("Vertebrates", mode=_BREADTH):
        print "%s - %s" % (nodeID, treeOfLife[nodeID].data)



    # - - - - - - -
    print "\n\n   --------- Tree of Fibonacci numbers --------- \n"
    treeOfN = Tree()

    treeOfN.add_node(1)  # root node
    treeOfN.add_node(2,1)
    treeOfN.add_node(3,2)
    treeOfN.add_node(5,3)
    treeOfN.add_node(8,5)
    treeOfN.add_node(13,8)
    treeOfN.add_node(21,13)

    treeOfN.display(1)