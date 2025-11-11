import numpy as np
from topomt import pyunitwizard as puw
from ...exceptions import ArgumentError

def digest_max_components_center_distance(max_components_center_distance, caller=None):

    if puw.is_quantity(max_components_center_distance):
        if puw.check(max_components_center_distance, dimensionality={'[L]':1}):
            return puw.standardize(max_components_center_distance)

    raise ArgumentError('max_components_center_distance', value=max_components_center_distance, caller=caller, message=None)

