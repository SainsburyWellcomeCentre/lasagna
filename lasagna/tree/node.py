class Node(object):
    """ A simple node class used for building a tree

     
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

    def is_branch(self):
        """
        Is this node a branch?
        A branch is defined as a node with more than two children
        returns True or False
        """
        return len(self.children) > 1
