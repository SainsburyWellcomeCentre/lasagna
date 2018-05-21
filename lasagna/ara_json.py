import json
import os
import sys
"""
Dumps ARA JSON as a flattened file that we can feed into our tree reader
"""


def is_valid_json_file_path(fname):
    if not os.path.exists(fname):
        print("Can not find file " + fname)
        return False
    if not fname.lower().endswith('json'):
        print("Data should be a JSON file")
        return False
    return True


def importData(fname, verbose=False):
    """
    Import from ARA JSON
    """
    if not is_valid_json_file_path(fname):
        return

    with open(fname) as f:
        obj = json.load(f)

    flattened_tree = flatten_tree(obj['msg'][0])
    col_names = 'id|parent|atlas_id|acronym|name|color'
    return flattened_tree, col_names


def flatten_tree(obj, flattened=''):
    if obj['parent_structure_id'] is None:
        obj['parent_structure_id'] = 0

    flattened += "{id}|{parent_id}|{atlas_id}|{acronym}|{name}|{color}\n".format(
            id=obj['id'],
            parent_id=obj['parent_structure_id'],
            atlas_id=obj['atlas_id'],
            acronym=obj['acronym'],
            name=obj['name'],
            color=obj['color_hex_triplet'])

    for child in obj.get('children', []):
        flattened = flatten_tree(child, flattened=flattened)

    return flattened


# ----------------------------------------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) > 1:
        fname = sys.argv[1]

    (flattened, colNames) = importData(fname)

    returnTree = True

    # Optionally run flattened structure through tree
    if returnTree:
        from lasagna import tree

        tree.importData(flattened.split('\n'), colSep='|', displayTree=True, headerLine=colNames)
    else:
        print(flattened)
