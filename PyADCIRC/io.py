r"""Data reading functions for ADCIRC data

TODO:
 - Eventually probably should create objects and stick these reading functions
   in there.
 - Add ability to also write these files.
 - Add boundary condition reading to `read_grid_data`
"""

import logging

import numpy


def file_len(fname):
    r"""Find number of lines in a file *fname*"""
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def read_grid_data(path):
    r"""
    Read a grid specification file (fort.14)

    :Note: This function currently only reads in the grid itself and not the 
           boundary specifications.

    :Input:
     - *path* (string) - Path to grid data file.

    :Output:
     - (numpy.ndarray(num_nodes, 2)) - Coordinates of each node.
     - (numpy.ndarray(num_nodes)) - Array containing depths at each node.
     - (numpy.ndarray(num_elements, 3)) - Numpy array containg specifcation of 
       each element's nodal points in counter-clockwise fashion.
    """

    grid_file = open(path, 'r')

    # Read header
    grid_file.readline()
    num_elements, num_nodes = [int(value) for value in grid_file.readline().split()]
    
    # Create necessary array storage
    coords = numpy.empty((num_nodes,2))
    depth = numpy.empty((num_nodes))
    triangles = numpy.empty((num_elements,3),dtype='int32')

    # Read in coordinates of each node
    logging.info("Reading coordinates and depths of each node...")
    for n in xrange(num_nodes):
        line = grid_file.readline().split()
        coords[n,0] = float(line[1])
        coords[n,1] = float(line[2])
        depth[n] = float(line[3])

    # Read in triangles
    logging.info("Reading in elements...")
    for n in xrange(num_elements):
        line = grid_file.readline().split()
        # Construct triangles
        triangles[n,0] = int(line[2]) - 1
        triangles[n,1] = int(line[3]) - 1
        triangles[n,2] = int(line[4]) - 1

    # Read in boundary data
    logging.warning("Boundary data reading has not been implemented, continuing.")

    grid_file.close()

    return coords, depth, triangles


def read_data_file(path, mask_dry_values=False, dry_data_value=-99999.0, 
                         masked_fill_value=0.0):
    r"""
    Read any of the ADCIRC data files with *columns* number of data
    
    :Input:
     - *path* (string) - Path to data file to be read in
     - *mask_dry_values* (bool) - Whether to mask dry elements, default is 
       `False`.
     - *dry_data_value* (float) - Value used to find cells to mask, default is 
       `-99999.0`.
     - *masked_fill_value* (float) - Value to set the masked elements to, 
       default is `-99999.0`.

    :Output:
     - (numpy.ndarray(num_times)) Array containing times that each field was at.
     - (numpy.ndarray(num_nodes, num_columns, num_times)) Array containing 
       values of each field at each time.
    """

    # Open data file and parse header
    data_file = open(path, 'r')
    data_file.readline()
    header_line = data_file.readline().split()
    num_times = int(header_line[0])
    num_nodes = int(header_line[1])
    unknown = float(header_line[2])
    unknown = int(header_line[3])
    num_columns = int(header_line[4])

    # Create data arrays
    t = numpy.empty((num_times))
    data_field = numpy.empty((num_nodes, num_columns, num_times))

    # Read in data
    for n in xrange(num_times):
        t[n] = float(data_file.readline().split()[0])
        for i in xrange(num_nodes):
            data_field[i,:,n] = [float(data_value) 
                            for data_value in data_file.readline().split()[1:]]

    # If num_columns is one, get rid of extraneous dimension
    if num_columns == 1:
        data_field = data_field[:,0,:]

    # Mask dry values
    if mask_dry_values:
        data_field = numpy.ma.masked_values(data_field, dry_data_value, 
                                            copy=False)
        data_field.fill_value = masked_fill_value

    return t, data_field