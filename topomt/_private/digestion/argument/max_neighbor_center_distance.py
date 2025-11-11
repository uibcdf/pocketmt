import numpy as np
from topomt import pyunitwizard as puw
from ...exceptions import ArgumentError

def digest_max_neighbor_center_distance(max_neighbor_center_distance, caller=None):

    if puw.is_quantity(max_neighbor_center_distance):
        if puw.check(max_neighbor_center_distance, dimensionality={'[L]':1}):
            return puw.standardize(max_neighbor_center_distance)

    raise ArgumentError('max_neighbor_center_distance', value=max_neighbor_center_distance, caller=caller, message=None)

