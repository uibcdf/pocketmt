import numpy as np
from topomt import pyunitwizard as puw
from ...exceptions import ArgumentError

def digest_min_radius(min_radius, caller=None):

    if puw.is_quantity(min_radius):
        if puw.check(min_radius, dimensionality={'[L]':1}):
            return puw.standardize(min_radius)

    raise ArgumentError('min_radius', value=min_radius, caller=caller, message=None)

