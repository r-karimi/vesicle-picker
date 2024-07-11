# Helper functions for vesicle picking with segment-anything

import matplotlib.pyplot as plt
import numpy as np
import configparser
from math import prod
from functools import reduce


def blockshaped(arr, nrows, ncols):

    """
    Return an array of shape (n, nrows, ncols) where
    n * nrows * ncols = arr.size

    If arr is a 2D array, the returned array should look like n subblocks with
    each subblock preserving the "physical" layout of arr.

    Taken from:
    https://stackoverflow.com/questions/16856788/slice-2d-array-into-smaller-2d-arrays
    """

    h, w = arr.shape
    assert h % nrows == 0, f"{h} rows is not evenly divisible by {nrows}"
    assert w % ncols == 0, f"{w} cols is not evenly divisible by {ncols}"
    return (arr.reshape(h//nrows, nrows, -1, ncols)
               .swapaxes(1, 2)
               .reshape(-1, nrows, ncols))


def unblockshaped(arr, h, w):

    """
    Return an array of shape (h, w) where
    h * w = arr.size

    If arr is of shape (n, nrows, ncols), n sublocks of shape (nrows, ncols),
    then the returned array preserves the "physical" layout of the sublocks.

    Taken from:
    https://stackoverflow.com/questions/16856788/slice-2d-array-into-smaller-2d-arrays
    """

    n, nrows, ncols = arr.shape
    return (arr.reshape(h//nrows, -1, nrows, ncols)
               .swapaxes(1, 2)
               .reshape(h, w))


def show_anns(anns):

    """Adapted from the segment-anything Github repository."""

    if len(anns) == 0:
        return
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    ax = plt.gca()
    ax.set_autoscale_on(False)

    img = np.ones((sorted_anns[0]['segmentation'].shape[0],
                   sorted_anns[0]['segmentation'].shape[1], 4))
    img[:, :, 3] = 0
    for ann in sorted_anns:
        m = ann['segmentation']
        color_mask = np.concatenate([np.random.random(3), [0.35]])
        img[m] = color_mask
    ax.imshow(img)


def sum_masks(masks, key):

    """Sum arrays stored in a list of masks by a given dictionary key."""

    return sum(mask.get(key, 0) for mask in masks)


def multiply_masks(masks, key):

    """Multiply arrays stored in a list of masks by a given dictionary key."""

    return prod(mask.get(key, 0) for mask in masks)


def read_config(config_file_path):

    """Parse configs given a filepath to a config file."""

    config = configparser.ConfigParser()
    config.read(config_file_path)
    return config


def factors(n):

    """
    Algorithm to find the factors of a given number. Taken from:
    https://stackoverflow.com/questions/6800193/what-is-the-most-
    efficient-way-of-finding-all-the-factors-of-a-number-in-python/
    """

    return np.array(
        reduce(
            list.__add__,
            ([i, n // i] for i in range(1, int(n**0.5) + 1) if n % i == 0)
        )
    )
