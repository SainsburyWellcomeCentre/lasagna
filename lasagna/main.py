#! /usr/bin/env python3


"""
Show coronal, transverse and saggital plots in different panels


Depends on:
vtk
pyqtgraph
numpy
tifffile
argparse
tempfile
urllib
"""

__author__ = "Sainsbury Wellcome Centre"
__license__ = "GPL v3"
__maintainer__ = "Sainsbury Wellcome Centre"


import os
import sys
import argparse
from PyQt5.QtWidgets import QApplication
import pyqtgraph as pg
from lasagna.lasagna_object import Lasagna


def get_parser():
    """
    Parse command-line input arguments

    :return: The argparse parser object
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i', '--image-stacks', dest='image_stacks', type=str, nargs='+',
                        help='File name(s) of image stacks to load')

    parser.add_argument('-S', '--sparse-points', dest='sparse_points', type=str, nargs='+',
                        help='File names of sparse points file(s) to load')
    parser.add_argument('-L', '--lines', type=str, nargs='+',
                        help='File names of lines file(s) to load')
    parser.add_argument('-T', '--tree', type=str, nargs='+',
                        help='File names of tree file(s) to load')

    parser.add_argument('-P', '--plugin', type=str,
                        help="Start plugin of this name. Use string from plugins menu as the argument")

    parser.add_argument('-C', '--console', action='store_true',  # Store true makes it False by default
                        help='Start a ipython console')
    parser.add_argument('-D', '--demo', action='store_true',
                        help='Load demo images')
    return parser


def download_sample_stacks():
    """ Downloads example data stacks from mouse.vision
        This method runs if the user asks for -D or --demo
    """
    import tempfile
    import urllib.request, urllib.parse, urllib.error
    tmp_dir = tempfile.gettempdir()
    img_stacks_filenames = [os.path.join(tmp_dir, 'reference.tiff'),
                            os.path.join(tmp_dir, 'sample.tiff')]
    base_url = 'http://mouse.vision/lasagna/'
    for fname in img_stacks_filenames:
        if not os.path.exists(fname):
            url = base_url + os.path.basename(fname)
            print('Downloading {} to {}'.format(url, fname))
            urllib.request.urlretrieve(url, fname)
    return img_stacks_filenames


# Set up the figure window
def main(im_stack_fnames_to_load=None, sparse_points_to_load=None, lines_to_load=None, trees_to_load=None,
         plugin_to_start=None, embed_console=False):

    app = QApplication([])

    tasty = Lasagna(embed_console=embed_console)
    tasty.app = app

    # Data from command line input if the user specified this
    if im_stack_fnames_to_load is not None:
        for fname in im_stack_fnames_to_load:
            print("Loading stack {}".format(fname))
            tasty.loadImageStack(fname)

    if sparse_points_to_load is not None:
        for fname in sparse_points_to_load:
            print("Loading points {}".format(fname))
            tasty.loadActions['sparse_point_reader'].showLoadDialog(fname)

    if lines_to_load is not None:
        for fname in lines_to_load:
            print("Loading lines {}".format(fname))
            tasty.loadActions['lines_reader'].showLoadDialog(fname)

    if trees_to_load is not None:
        for fname in trees_to_load:
            print("Loading tree {}".format(fname))
            tasty.loadActions['tree_reader'].showLoadDialog(fname)

    tasty.initialiseAxes()

    if plugin_to_start is not None:
        if plugin_to_start in tasty.plugins:
            tasty.startPlugin(plugin_to_start)
            tasty.pluginActions[plugin_to_start].setChecked(True)
        else:
            print("No plugin {}: not starting".format(plugin_to_start))

    # Link slots to signals
    # connect views to the mouseMoved slot. After connection this runs in the background.
    sigProxies = []  # This list will be populated this with pyqtgraph.SignalProxy objects for linking signals and slots
    for i in range(3):
        thisProxy = pg.SignalProxy(tasty.axes2D[i].view.scene().sigMouseMoved, rateLimit=30, slot=tasty.mouseMoved)
        thisProxy.axisID = i  # this is picked up the mouseMoved slot
        sigProxies.append(thisProxy)

        thisProxy = pg.SignalProxy(tasty.axes2D[i].view.getViewBox().mouseClicked, rateLimit=30, slot=tasty.axisClicked)
        thisProxy.axisID = i  # this is picked up the mouseMoved slot
        sigProxies.append(thisProxy)

    if embed_console:
        from traitlets.config import Config
        cfg = Config()
        cfg.InteractiveShellApp.gui = 'qt5'
        import IPython
        IPython.start_ipython(config=cfg, argv=[], user_ns=dict(tasty=tasty, app=app))
    else:
        sys.exit(app.exec_())


def run():
    print('Starting')
    sys.path.append(os.path.abspath('.'))
    args = get_parser().parse_args()

    # Either load the demo stacks or a user-specified stacks
    if args.demo:
        img_stack_fnames_to_load = download_sample_stacks()
    else:
        img_stack_fnames_to_load = args.image_stacks

    main(im_stack_fnames_to_load=img_stack_fnames_to_load, sparse_points_to_load=args.sparse_points,
         lines_to_load=args.lines, trees_to_load=args.tree,
         plugin_to_start=args.plugin, embed_console=args.console)


# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    run()
