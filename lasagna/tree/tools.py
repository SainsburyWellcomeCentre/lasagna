def import_data(fname, displayTree=False, colSep=",", headerLine=False, verbose=False):
    """ Import tree data from a CSV (text) file or list. 

    The data should be in the following format:
    node_ID_number,node_parent_ID_number,data_item1,data_item2,...,data_itemN\n

    The separator can, optionally, be a character other than ","

    The root node must have a parent id of 0 and normally should also have an index of 1

    From MATLAB one can produce tree structures and dump data in the correct format
    using https://github.com/raacampbell13/matlab-tree and the tree.dumptree method

    Inputs:
    fname - if a string, import_data assumes it is a file name and tries to load the tree from file.
            if it is a list, import_data assumes that each line is a CSV data line and tries to 
            convert to a tree.        
    displayTree - if True the tree is printed to standard output after creation
    colSep - the data separator, a comma by default.
    headerLine - if True, the first line is stripped off and considered to be the column headings.
                headerLine can also be a CSV string or a list that defines the column headings. Must have the
                same number of columns as the rest of the file.
    verbose - prints diagnositic info to screen if true


    Return:
    A tree class
    """

    if verbose:
        print("tree.tools.import_data importing file %s" % fname)

    # Error check
    if isinstance(fname, str):
        if os.path.exists(fname) == False:
            print("Can not find file " + fname)
            return

        # Read in data
        fid = open(fname, "r")
        contents = fid.read().split("\n")
        fid.close()

    elif isinstance(fname, list):
        contents = fname  # assume that fname is data rather than a file name

    # Get header data if present
    if headerLine == True:
        header = contents.pop(0)
        header = header.rstrip("\n").split(colSep)
    elif isinstance(headerLine, str):
        header = headerLine.rstrip("\n").split(colSep)
    elif isinstance(headerLine, list):
        header = headerLine
    else:
        header = False

    data = []
    for line in contents:
        if len(line) == 0:
            continue

        dataLine = line.split(colSep)
        if len(header) != len(dataLine):
            print(
                "\nTree file appears corrupt! header length is %d but data line length is %d.\ntree.tools.import_data is aborting.\n"
                % (len(header), len(dataLine))
            )
            return False

        theseData = list(
            map(int, dataLine[0:2])
        )  # add index and parent to the first two columns

        # Add data to the third column. Either as a list or as a dictionary (if header names were provided)
        if header != False:  # add as dictionary
            dataCol = dict()

            for ii in range(len(header) - 2):
                ii += 2
                dataCol[header[ii]] = dataTypeFromString.convertString(dataLine[ii])

        else:
            dataCol = dataLine[2:]  # add as list of strings

        theseData.append(dataCol)
        data.append(theseData)

    if verbose:
        print(
            "tree.tools.import_data read %d rows of data from %s" % (len(data), fname)
        )

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
