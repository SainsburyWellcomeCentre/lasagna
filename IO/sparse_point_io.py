"""
Functions to read and write
"""
import os
import yaml


def read_pts_file(file_name):
    """ Read an elastix pts file

    :param file_name:
    :return pts_coord: list of list with pts coordinates
    :return pts_type: coordinate system, 'point' or 'index'
    """

    pts_coord = []
    with open(file_name, 'r') as in_file:
        pts_type = in_file.readline().strip()
        npts = int(in_file.readline().strip())
        for line in in_file.readlines():
            line = line.strip()
            if not len(line):  # skip last empty line
                break
            coords = [float(c) for c in line.split(' ')]
            pts_coord.append([coords[i] for i in [2, 0, 1]])  # reorder in lasagna order (Z,X,Y)
    if len(pts_coord) != npts:
        print('!!! Warning found %i points but file says there are %i!!!' % (len(pts_coord), npts))
    return pts_coord, pts_type


def read_transformix_output(file_path):
    """ read outputpoints.txt of transformix

    :param file_path: path to outputpoints.txt
    :return: a list of dictionary with one element per point
    """

    with open(file_path, 'r') as in_file:
        out = []
        for line in in_file.readlines():
            parts = line.strip().split(';')
            parts = [p.strip() for p in parts]
            pts_dict = dict(pts_index=int(parts[0].split('\t')[1]))
            for part in parts[1:]:
                what, value = part.split('=')
                # Values are always a list of numbers, space separated
                value = value.strip()[1:-1]  # remove the []
                value = [float(v) for v in value.strip().split(' ')]
                pts_dict[what.strip()] = value
            out.append(pts_dict)
    return out


def write_pts_file(file_name, Xs, Ys, Zs=None, index=False, force=False):
    """ Write a pts file for elastix

    :param file_name: target file
    :param Xs: list of X values
    :param Ys: list of Y values
    :param Zs: list of Z value (or None for 2D)
    :param index: coordinates is pixel coordinate (not real world coordinates) default False
    :param force: erase file is name already exists (default False)
    :return:
    """

    if os.path.exists(file_name) and not force:
        raise IOError("File %s already exists. Use force to replace")

    assert(len(Xs) == len(Ys))
    to_zip = [Xs, Ys]

    if Zs is not None:
        assert(len(Xs) == len(Ys))
        to_zip.append(Zs)

    with open(file_name, 'w') as out_file:
        # write the first line. VV should return thing in real world coordinate
        pts_type = 'index' if index else 'point'
        out_file.write('%s\n' % pts_type)
        # write the number of points
        out_file.write('%i\n' % len(Xs))
        # Write all the line
        for data in zip(*to_zip):
            out_file.write(' '.join([str(d) for d in data]) + '\n')
        # Add a last line
        out_file.write('\n')


def read_vv_txt_landmarks(path2file):
    """ Read a VV landmark file

    :param path2file:
    :return:
    """
    # read the vv file
    with open(path2file, 'r') as in_file:
        # get rid of useless first line
        header = in_file.readline()
        if not header.strip().lower().startswith('landmarks1'):
            print('Weird first line. Is it really a landmark file for vv?')
        data = []
        for line in in_file.readlines():
            line_data = line.strip()
            if len(line_data):
                line_data = line_data.split(' ')
                assert(len(line_data) == 6)
                data.append([line_data[i] for i in [2, 0, 1]])  # reorder in lasagna Z,X,Y system
    return data


def read_masiv_roi(path2file):
    """ Read a masiv roi file

    :param path2file: path to the masiv file
    :return roi_coords: a list of list with 4 elements (X,Y,Z, cell type)
    """

    roi_coords = []
    with open(path2file, 'r') as in_file:
        data = yaml.load(in_file)
        for ctype, pts_prop in data.items():
            # keep only cell type with at least one point
            if not 'markers' in pts_prop:
                continue
            coords = pts_prop['markers']
            for i, c in enumerate(coords):
                roi_coords.append([c['x'], c['y'], c['z'], int(ctype[4:])])
    return roi_coords


def read_lasagna_pts(fname):
    """ Read default lasagna pts format

    It is just a list of space separated coordinante

    :param fname: path to file (usually .pts)
    :return data: a list of coordinates
    """
    with open(str(fname), 'r') as fid:
        contents = fid.read()

    # a list of strings with each string being one line from the file
    asList = contents.split('\n')
    data = []
    for ii in range(len(asList)):
        if len(asList[ii]) == 0:
            continue
        data.append([float(x) for x in asList[ii].split(',')])
    return data