"""
Module to handle tree data. 
Defines a tree and a node class as well as functions for importing data
"""
import os.path

from lasagna import dataTypeFromString


(_ROOT, _DEPTH, _WIDTH) = list(range(3))  # Used by classes to navigate the tree


def importData(fname, displayTree=False, colSep=',', headerLine=None, verbose=False):
    """
    Import tree data from a CSV (text) file or list. 

    The data should be in the following format:
    node_ID_number,node_parent_ID_number,data_item1,data_item2,...,data_itemN\n

    The separator can, optionally, be a character other than ","

    The root node must have a parent id of 0 and normally should also have an index of 1

    From MATLAB one can produce tree structures and dump data in the correct format
    using https://github.com/raacampbell13/matlab-tree and the tree.dumptree method

    Inputs:
    fname - if a string, importData assumes it is a file name and tries to load the tree from file.
            if it is a list, importData assumes that each line is a CSV data line and tries to 
            convert to a tree.        
    displayTree - if True the tree is printed to standard output after creation
    colSep - the data separator, a comma by default.
    headerLine - if True, the first line is stripped off and considered to be the column headings.
                headerLine can also be a CSV string or a list that defines the column headings. Must have the
                same number of columns as the rest of the file.
    verbose - prints diagnositic info to screen if true
    """
    if verbose:
        print("tree.importData importing file %s" % fname)

    # Error check
    if isinstance(fname, str):
        if not os.path.exists(fname):
            print("Can not find file " + fname)
            return
        # Read in data
        fid = open(fname, 'r')
        contents = fid.read().split('\n')
        fid.close()
    elif isinstance(fname, list):
        contents = fname  # assume that fname is data rather than a file name

    # Get header data if present
    if headerLine is None:
        header = contents.pop(0)
        header = header.rstrip('\n').split(colSep)
    elif isinstance(headerLine, str):
        header = headerLine.rstrip('\n').split(colSep)
    elif isinstance(headerLine, list):
        header = headerLine
    else:
        header = False

    data = []
    for line in contents:
        if not line:
            continue

        dataLine = line.split(colSep)
        if len(header) != len(dataLine):
            print("\nTree file appears corrupt! header length is %d but data line length is %d."
                  "\ntree.importData is aborting.\n" % (len(header), len(dataLine)))
            return False

        theseData = list(map(int, dataLine[0:2]))  # add index and parent to the first two columns

        # Add data to the third column. Either as a list or as a dictionary (if header names were provided)
        if header:  # add as dictionary
            dataCol = dict()
            for i in range(len(header)-2):
                i += 2
                dataCol[header[i]] = dataTypeFromString.convertString(dataLine[i])
        else:
            dataCol = dataLine[2:]  # add as list of strings

        theseData.append(dataCol) 
        data.append(theseData)

    if verbose:
        print("tree.importData read %d rows of data from %s" % (len(data), fname))

    # Build tree
    tree = Tree()
    tree.add_node(0)
    for thisNode in data:
        tree.add_node(thisNode[0], thisNode[1])
        tree[thisNode[0]].data = thisNode[2]

    # Optionally dump the tree to screen (unlikely to be useful for large trees)
    if displayTree:
        tree.display(0)

        for nodeID in tree.traverse(0):
            print("%s - %s" % (nodeID, tree[nodeID].data))

    return tree


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
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
        node = Node(identifier, parent=parent)
        self[identifier] = node

        if parent is not None:
            self[parent].add_child(identifier)

        return node

    # TODO: replace with  __repr__(self): ?
    def display(self, identifier, depth=_ROOT):
        """
        Very (very) simple tree display
        """
        children = self[identifier].children
        if depth == _ROOT:
            print(("{0}".format(identifier)))
        else:
            print(("    "*depth, "{0}".format(identifier)))

        depth += 1
        for child in children:
            self.display(child, depth)  # recursive call

    def traverse(self, identifier, mode=_DEPTH):
        """
        traverse the tree in depth first or width first modes
        using a yield-based generator
        """
        # Python generator using yield
        yield identifier  # return the root of this list
        queue = self[identifier].children
        while queue:
            yield queue[0]
            expansion = self[queue[0]].children
            if mode == _DEPTH:
                queue = expansion + queue[1:]  # depth-first
            elif mode == _WIDTH:
                queue = queue[1:] + expansion  # width-first

    def isLeaf(self, identifier):
        """
        Is the node indexed by 'identifier' a leaf?
        returns True or False
        """
        n = 0
        for nodeID in self.traverse(identifier):
            n += 1
            if n > 1:
                break

        if n == 1:
            return True
        else:
            return False

    def findLeaves(self, fromNode=0):
        """
        Returns a list of nodes that are leaves, searching from 
        the node "fromNode". To find all leaves, fromNode should 
        be the root node.
        """
        nodesThatAreLeaves = []
        for nodeID in self.traverse(fromNode):
            if self.isLeaf(nodeID):
                nodesThatAreLeaves.append(nodeID)

        return nodesThatAreLeaves

    def findBranches(self, fromNode=0):
        """
        Is the node indexed by 'identifier' a branch?
        A branch is defined as a node with more than two children
        To find all branches, fromNode should be the root node.
        """
        nodesThatAreBranches = []
        for nodeID in self.traverse(fromNode):
            if self.nodes[nodeID].isbranch():
                nodesThatAreBranches.append(nodeID)

        return nodesThatAreBranches

    def findSegments(self, linkSegments=1, nodeID=0, segments=()):
        """ 
        Return a list containing all unique segments of the tree

        If linkSegments is 1, then the branch node is added to each returned segement. This makes
        it possible to plot the data without gaps appearing. This is the default. 
        If linksegments is 0, then the no duplicate points are returned.
        """
        # print "Calling find segments with nodeID %d" % nodeID

        if linkSegments and nodeID > 0:
            thisPath = [self.nodes[nodeID].parent]
        else:
            thisPath = []

        if isinstance(nodeID, int):
            nodeID = [nodeID]

        while len(nodeID) == 1:
            # print "appending node %d" % nodeID[0]
            thisPath.append(nodeID[0])
            nodeID = self.nodes[nodeID[0]].children
            
        segments = segments + (thisPath,)  # Store this segment

        # Go into the branches with a recursive call
        for thisNode in nodeID:
            segments = self.findSegments(linkSegments, thisNode, segments)

        return segments

    def pathToRoot(self, fromNode):
        """
        Path from node "fromNode" to the tree's root
        To achieve this we simply need to follow the tree back by looking 
        each node's parent. Since a node can only have one parent, this is 
        trivial and quick. No nee to exhaustively search the tree for the 
        fastest path.
        """
        currentNode = fromNode
        path = [fromNode]
        while self.nodes[currentNode].parent is not None:
            path.append(self.nodes[currentNode].parent)
            currentNode = self.nodes[currentNode].parent
        return path

    def __getitem__(self, key):
        return self.__nodes[key]

    def __setitem__(self, key, item):
        self.__nodes[key] = item


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Node(object):
    """
    A simple node class
    """
    def __init__(self, identifier, data=None, parent=None):
        self.__identifier = identifier
        self.__children = []
        self.__data = data  # The node's data payload. Can be anything.
        self.parent = parent

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        self.__data = value
    
    @property
    def identifier(self):
        return self.__identifier

    @property
    def children(self):
        return self.__children

    def add_child(self, identifier):
        self.__children.append(identifier)

    def isbranch(self):
        """
        Is this node a branch?
        A branch is defined as a node with more than two children
        returns True or False
        """
        return len(self.children) > 1


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Generate an example if run from the command line
if __name__ == '__main__':
    from lasagna.tree import Tree
    (_ROOT, _DEPTH, _WIDTH) = list(range(3))

    print("\n\n   --------- Tree of life --------- \n")
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
    treeOfLife.add_node("Sponges", "Animals")
    treeOfLife.add_node("Flatworms", "Animals")
    treeOfLife.add_node("Arthropods", "Animals")
    treeOfLife.add_node("Insects", "Arthropods")
    treeOfLife.add_node("Crustaceans", "Arthropods")
    treeOfLife.add_node("Vertebrates", "Animals")
    treeOfLife.add_node("Fish", "Vertebrates")
    treeOfLife.add_node("Amphibians", "Vertebrates")
    treeOfLife.add_node("Reptiles", "Vertebrates")
    treeOfLife.add_node("Mammals", "Vertebrates")

    # Add some data to the vertebrates
    treeOfLife["Vertebrates"].data = 'they have backbones'
    treeOfLife["Fish"].data = 'they swim'
    treeOfLife["Amphibians"].data = 'they croak'
    treeOfLife["Reptiles"].data = 'they stick to walls'
    treeOfLife["Mammals"].data = 'they have udders'

    print("List of nodes:")
    print(list(treeOfLife.nodes.keys()))
    print("")

    print("Children of node 'Vertebrates'")
    print(treeOfLife.nodes['Vertebrates'].children)
    print("")

    print(treeOfLife.display('Life'))

    print("\n***** Depth-first *****")
    for nodeID in treeOfLife.traverse("Life"):
        print(nodeID)

    print("\n***** Width-first *****")
    for nodeID in treeOfLife.traverse("Life", mode=_WIDTH):
        print(nodeID)
    
    print("\n***** Width-first of all data in vertebrates *****")
    for nodeID in treeOfLife.traverse("Vertebrates", mode=_WIDTH):
        print("%s - %s" % (nodeID, treeOfLife[nodeID].data))

    print("\nLeaves:")
    print(treeOfLife.findLeaves('Life'))

    print("\nBranches:")
    print(treeOfLife.findBranches('Life'))

    print("\nPath to root from Fish:")
    print(treeOfLife.pathToRoot('Fish'))

    # - - - - - - -
    print("\n\n   --------- Tree of Fibonacci numbers --------- \n")
    treeOfN = Tree()

    treeOfN.add_node(1)  # root node
    treeOfN.add_node(2, 1)
    treeOfN.add_node(3, 2)
    treeOfN.add_node(5, 3)
    treeOfN.add_node(8, 5)
    treeOfN.add_node(13, 8)
    treeOfN.add_node(21, 13)

    treeOfN.display(1)
