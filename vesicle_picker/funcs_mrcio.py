# A library of utilities for working with MRC format files.
# Originally written by John Rubinstein, edited by Ryan Karimi.

import numpy as n

# i = image
# rd = read
# wr = write
# sec = section (z slice)
# pas = part of a section (part of a z slice)
# lin = line
# hdr = header


def iwrsec_opened(data, filename):

    """
    Image Write Section (opened) -
    write a section of a stack to an MRC file that is already opened.
    """

    n.require(n.reshape(data, (-1,), order='F'),
              dtype=n.float32).tofile(filename)


def iwrhdr_opened(filename, nxyz=0, dmin=0, dmax=0,
                  dmean=0, mode=2, psize=1):

    """
    Image Write Header (opened) -
    write header to a file that is already opened.
    """

    # Go to the beginning of the file
    filename.seek(0)

    # 1024 byte header (integer values)
    header = n.zeros(256, dtype=n.int32)

    # floating point values
    header_f = header.view(n.float32)
    header[:3] = nxyz

    # mode, 2 = float32 datatype
    header[3] = mode

    # mx, my, mz (grid size)
    header[7:10] = nxyz

    # xlen, ylen, zlen
    header_f[10:13] = [psize*i for i in nxyz]

    # CELLB
    header_f[13:16] = 90.0

    # axis order
    header[16:19] = [1, 2, 3]

    # data stats
    header_f[19:22] = [dmin, dmax, dmean]

    # 'MAP ' chars
    header[52] = 542130509
    header[53] = 16708
    header.tofile(filename)


def irdvol_opened(filename):

    """
    Image Read Volume (opened) -
    read opened MRC volume into memory in ROW MAJOR order.
    """

    hdr = irdhdr_opened(filename)
    nx = hdr['nx']
    ny = hdr['ny']
    nz = hdr['nz']
    dtype = {0: n.int8, 1: n.int16, 2: n.float32,
             6: n.uint16}[hdr['datatype']]
    filename.seek(1024)
    data = n.reshape(n.fromfile(filename, dtype, count=nx*ny*nz),
                     (nz, ny, nx), order='C')
    return data


def irdsec_opened(filename, sec):

    """
    Image Read Section (opened) -
    read a section from an MRC file that is already opened.
    """

    hdr = irdhdr_opened(filename)
    nx = hdr['nx']
    ny = hdr['ny']
    dtype = {0: n.int8, 1: n.int16, 2: n.float32,
             6: n.uint16}[hdr['datatype']]
    if hdr['datatype'] == 0:
        nbytes = 1
    elif hdr['datatype'] == 1 or hdr['datatype'] == 6:
        nbytes = 2
    else:
        nbytes = 4
    position = nx*ny*(sec)*nbytes+1024
    filename.seek(position)
    data = n.reshape(n.fromfile(filename, dtype, count=nx*ny),
                     (nx, ny), order='F')
    return data


def irdhdr_opened(fname):

    """
    Image Reader Header (opened) -
    read header from an MRC file that is already opened.
    """

    fname.seek(0)
    hdr = None
    hdr = {}
    header = n.fromfile(fname, dtype=n.int32, count=256)
    header_f = header.view(n.float32)
    [hdr['nx'], hdr['ny'], hdr['nz'], hdr['datatype']] = header[:4]
    [hdr['xlen'], hdr['ylen'], hdr['zlen']] = header_f[10:13]
    return hdr


def irdpas_opened(filename, xstart, xstop, ystart, ystop, sec):

    """
    Image Read Part of section (opened) -
    read part of a section from an MRC stack already opened.
    """

    hdr = irdhdr_opened(filename)
    nx = hdr['nx']
    ny = hdr['ny']

    # Return to beginning of file
    filename.seek(0)
    dtype = {0: n.int8, 1: n.int16, 2: n.float32,
             6: n.uint16}[hdr['datatype']]
    if hdr['datatype'] == 0:
        nbytes = 1
    elif hdr['datatype'] == 1 or hdr['datatype'] == 6:
        nbytes = 2
    else:
        nbytes = 4
    # Assumes Python numbering
    xsize = xstop - xstart
    ysize = ystop - ystart
    data = n.zeros([xsize, ysize], dtype=n.float32)
    position = nx*ny*sec*nbytes + ystart*nx*nbytes + 1024
    for line in range(ysize):
        position = position + xstart*nbytes
        filename.seek(position)
        data[:, line] = n.fromfile(filename, dtype, count=xsize)
        position = position + xsize*nbytes+nx*nbytes - xstop*nbytes
    return data


def irdsec_closed(filename, sec):

    """
    Image Read Section (closed) -
    open an MRC file and then read a section.
    """

    hdr = readMRCheader(filename)
    nx = hdr['nx']
    ny = hdr['ny']
    dtype = {0: n.int8, 1: n.int16, 2: n.float32,
             6: n.uint16}[hdr['datatype']]
    data = n.zeros([nx, ny], dtype)
    with open(filename) as f:
        position = nx*ny*(sec) + 1024
        f.seek(position)
        data = n.reshape(n.fromfile(f, dtype, count=nx*ny),
                         (nx, ny), order='F')
    return data


def readMRCmemmap(fname, inc_header=False):

    """Read a memory mapped MRC file and header."""

    hdr = readMRCheader(fname)
    nx = hdr['nx']
    ny = hdr['ny']
    nz = hdr['nz']
    dtype = {0: n.int8, 1: n.int16, 2: n.float32,
             6: n.uint16}[hdr['datatype']]
    mm = n.memmap(fname, dtype, 'r',
                  offset=1024, shape=(nx, ny, nz), order='F')
    return (mm, hdr) if inc_header else mm


def readMRCheader(fname):

    """Read values from MRC header into an array."""

    hdr = None
    with open(fname) as f:
        hdr = {}
        header = n.fromfile(f, dtype=n.int32, count=256)
        header_f = header.view(n.float32)
        [hdr['nx'], hdr['ny'], hdr['nz'], hdr['datatype']] = header[:4]
        [hdr['xlen'], hdr['ylen'], hdr['zlen']] = header_f[10:13]
    return hdr


def irdpasMRC(filename, xstart, xstop, ystart, ystop, sec):

    """Image Read Part of a Section: Read part of an MRC section."""

    hdr = readMRCheader(filename)
    nx = hdr['nx']
    ny = hdr['ny']
    dtype = {0: n.int8, 1: n.int16, 2: n.float32,
             6: n.uint16}[hdr['datatype']]
    if hdr['datatype'] == 0:
        nbytes = 1
    elif hdr['datatype'] == 1 or hdr['datatype'] == 6:
        nbytes = 2
    else:
        nbytes = 4
    # Assumes Python numbering
    xsize = xstop - xstart
    ysize = ystop - ystart
    data = n.zeros([xsize, ysize], dtype=n.float32)
    with open(filename) as f:
        position = nx*ny*sec*nbytes + ystart*nx*nbytes + 1024
        for line in range(ysize):
            position = position + xstart*nbytes
            f.seek(position)
            data[:, line] = n.fromfile(f, dtype, count=xsize)
            position = position + xsize*nbytes + nx*nbytes - xstop*nbytes
    return data
