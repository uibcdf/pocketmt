import numpy as np
from topomt import pyunitwizard as puw
from ...exceptions import ArgumentError

def digest_max_radius(max_radius, caller=None):

    if puw.is_quantity(max_radius):
        if puw.check(max_radius, dimensionality={'[L]':1}):
            return puw.standardize(max_radius)

    raise ArgumentError('max_radius', value=max_radius, caller=caller, message=None)

