import numpy as np
from topomt import pyunitwizard as puw
from ...exceptions import ArgumentError

def digest_max_alpha_sphere_radius(max_alpha_sphere_radius, caller=None):

    if puw.is_quantity(max_alpha_sphere_radius):
        if puw.check(max_alpha_sphere_radius, dimensionality={'[L]':1}):
            return puw.standardize(max_alpha_sphere_radius)

    raise ArgumentError('max_alpha_sphere_radius', value=max_alpha_sphere_radius, caller=caller, message=None)

