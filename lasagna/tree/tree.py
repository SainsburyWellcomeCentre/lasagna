from lasagna.tree.tree_parser import _ROOT, _DEPTH, _WIDTH
from lasagna.tree.node import Node


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
        return [node_id for node_id in self.traverse(fromNode) if self.isLeaf(node_id)]

    def findBranches(self, fromNode=0):
        """
        Is the node indexed by 'identifier' a branch?
        A branch is defined as a node with more than two children
        To find all branches, fromNode should be the root node.
        """
        return [node_id for node_id in self.traverse(fromNode) if self.nodes[node_id].isbranch()]

    def findSegments(self, linkSegments=1, nodeID=0, segments=()):  # FIXME: nodeID to node_ids
        """
        Return a list containing all unique segments of the tree

        If linkSegments is 1, then the branch node is added to each returned segement. This makes
        it possible to plot the data without gaps appearing. This is the default.
        If linksegments is 0, then the no duplicate points are returned.
        """
        # print "Calling find segments with nodeID %d" % nodeID

        if linkSegments and nodeID > 0:
            _path = [self.nodes[nodeID].parent]
        else:
            _path = []

        if isinstance(nodeID, int):
            nodeID = [nodeID]

        while len(nodeID) == 1:
            # print "appending node %d" % nodeID[0]
            _path.append(nodeID[0])
            nodeID = self.nodes[nodeID[0]].children

        segments = segments + (_path,)  # Store this segment

        # Go into the branches with a recursive call
        for node in nodeID:
            segments = self.findSegments(linkSegments, node, segments)

        return segments

    def pathToRoot(self, fromNode):
        """
        Path from node "fromNode" to the tree's root
        To achieve this we simply need to follow the tree back by looking
        each node's parent. Since a node can only have one parent, this is
        trivial and quick. No nee to exhaustively search the tree for the
        fastest path.
        """
        current_node = fromNode
        path = [fromNode]
        while self.nodes[current_node].parent is not None:
            path.append(self.nodes[current_node].parent)
            current_node = self.nodes[current_node].parent
        return path

    def __getitem__(self, key):
        return self.__nodes[key]

    def __setitem__(self, key, item):
        self.__nodes[key] = item
