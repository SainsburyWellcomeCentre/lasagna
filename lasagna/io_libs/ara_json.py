import os
import sys

import json

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


def import_data(fname, verbose=False):
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


def flatten_tree(obj, flattened_tree=''):
    if obj['parent_structure_id'] is None:
        obj['parent_structure_id'] = 0

    flattened_tree += "{id}|{parent_id}|{atlas_id}|{acronym}|{name}|{color}\n".format(
            id=obj['id'],
            parent_id=obj['parent_structure_id'],
            atlas_id=obj['atlas_id'],
            acronym=obj['acronym'],
            name=obj['name'],
            color=obj['color_hex_triplet'])

    for child in obj.get('children', []):
        flattened_tree = flatten_tree(child, flattened_tree=flattened_tree)  # FIXME: check if shouldn't bee +=

    return flattened_tree


# ----------------------------------------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        sys.exit()

    flattened_ara_tree, header = import_data(file_name)

    return_tree = True

    # Optionally run flattened structure through tree
    if return_tree:
        from lasagna.tree import tree_parser

        tree_parser.parse_file(flattened_ara_tree.split('\n'), colSep='|', displayTree=True, headerLine=header)
    else:
        print(flattened_ara_tree)
