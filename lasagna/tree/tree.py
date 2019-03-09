from lasagna.tree.node import Node


_ROOT, _DEPTH, _WIDTH = list(range(3))  # Used by classes to navigate the tree


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

    def is_leaf(self, identifier):
        """
        Is the node indexed by 'identifier' a leaf?
        returns True or False
        """
        n = 0
        for node_id in self.traverse(identifier):
            n += 1
            if n > 1:
                break

        if n == 1:
            return True
        else:
            return False

    def find_leaves(self, from_node=0):
        """
        Returns a list of nodes that are leaves, searching from
        the node "fromNode". To find all leaves, fromNode should
        be the root node.
        """
        return [node_id for node_id in self.traverse(from_node) if self.is_leaf(node_id)]

    def find_branches(self, from_node=0):
        """
        Is the node indexed by 'identifier' a branch?
        A branch is defined as a node with more than two children
        To find all branches, fromNode should be the root node.
        """
        return [node_id for node_id in self.traverse(from_node) if self.nodes[node_id].is_branch()]

    def find_segments(self, link_segments=1, node_ids=0, segments=()):
        """
        Return a list containing all unique segments of the tree

        If linkSegments is 1, then the branch node is added to each returned segement. This makes
        it possible to plot the data without gaps appearing. This is the default.
        If linksegments is 0, then the no duplicate points are returned.
        """
        # print "Calling find segments with nodeID %d" % nodeID

        if link_segments and node_ids > 0:
            _path = [self.nodes[node_ids].parent]
        else:
            _path = []

        if isinstance(node_ids, int):
            node_ids = [node_ids]

        while len(node_ids) == 1:
            # print "appending node %d" % nodeID[0]
            _path.append(node_ids[0])
            node_ids = self.nodes[node_ids[0]].children

        segments = segments + (_path,)  # Store this segment

        # Go into the branches with a recursive call
        for node in node_ids:
            segments = self.find_segments(link_segments, node, segments)

        return segments

    def path_to_root(self, from_node):
        """
        Path from node "fromNode" to the tree's root
        To achieve this we simply need to follow the tree back by looking
        each node's parent. Since a node can only have one parent, this is
        trivial and quick. No nee to exhaustively search the tree for the
        fastest path.
        """
        current_node = from_node
        path = [from_node]
        while self.nodes[current_node].parent is not None:
            path.append(self.nodes[current_node].parent)
            current_node = self.nodes[current_node].parent
        return path

    def __getitem__(self, key):
        return self.__nodes[key]

    def __setitem__(self, key, item):
        self.__nodes[key] = item
