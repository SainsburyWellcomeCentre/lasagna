"""
Module to handle tree data. 
Defines a tree and a node class as well as functions for importing data
"""
import os

from lasagna.tree.tree import Tree
from lasagna.utils import data_type_from_string


def parse_file(fname, display_tree=False, col_sep=',', header_line=None, verbose=False):
    """
    Import tree data from a CSV (text) file or list. 

    The data should be in the following format:
    node_ID_number,node_parent_ID_number,data_item1,data_item2,...,data_itemN\n

    The separator can, optionally, be a character other than ","

    The root node must have a parent id of 0 and normally should also have an index of 1

    From MATLAB one can produce tree structures and dump data in the correct format
    using https://github.com/raacampbell13/matlab-tree and the tree.dumptree method

    Inputs:
    fname - if a string, parse_file assumes it is a file name and tries to load the tree from file.
            if it is a list, parse_file assumes that each line is a CSV data line and tries to
            convert to a tree.        
    displayTree - if True the tree is printed to standard output after creation
    colSep - the data separator, a comma by default.
    headerLine - if True, the first line is stripped off and considered to be the column headings.
                headerLine can also be a CSV string or a list that defines the column headings. Must have the
                same number of columns as the rest of the file.
    verbose - prints diagnostic info to screen if true
    """
    if verbose:
        print("tree.tree_parser.parse_file importing file %s" % fname)

    # Error check
    if isinstance(fname, str):
        if not os.path.exists(fname):
            print("Can not find file " + fname)
            return
        with open(fname, 'r') as fid:  # Read in data
            contents = fid.read().split('\n')
    elif isinstance(fname, list):
        contents = fname  # assume that fname is data rather than a file name

    # Get header data if present
    if header_line is None:
        header = contents.pop(0)
        header = header.rstrip('\n').split(col_sep)
    elif isinstance(header_line, str):
        header = header_line.rstrip('\n').split(col_sep)
    elif isinstance(header_line, list):
        header = header_line
    else:
        header = False

    data = []
    for line in contents:
        if not line:
            continue

        data_line = line.split(col_sep)
        if len(header) != len(data_line):
            print("\nTree file appears corrupt! header length is %d but data line length is %d."
                  "\ntree.tree_parser.parse_file is aborting.\n" % (len(header), len(data_line)))
            return False

        # Add data to the third column. Either as a list or as a dictionary (if header names were provided)
        if header:  # add as dictionary
            data_col = dict()
            for i in range(len(header)-2):
                i += 2
                data_col[header[i]] = data_type_from_string.convert_string(data_line[i])
        else:
            data_col = data_line[2:]  # add as list of strings

        line_data = [int(d) for d in data_line[0:2]]  # add index and parent to the first two columns
        line_data.append(data_col)
        data.append(line_data)

    if verbose:
        print("tree.tree_parser.parse_file read %d rows of data from %s" % (len(data), fname))

    # Build tree
    tree = Tree()
    tree.add_node(0)
    for thisNode in data:
        tree.add_node(thisNode[0], thisNode[1])
        tree[thisNode[0]].data = thisNode[2]

    # Optionally dump the tree to screen (unlikely to be useful for large trees)
    if display_tree:
        tree.display(0)
        for node_id in tree.traverse(0):
            print("%s - %s" % (node_id, tree[node_id].data))

    return tree
