import numpy as np
from topomt import pyunitwizard as puw
from ...exceptions import ArgumentError

def digest_min_alpha_sphere_radius(min_alpha_sphere_radius, caller=None):

    if puw.is_quantity(min_alpha_sphere_radius):
        if puw.check(min_alpha_sphere_radius, dimensionality={'[L]':1}):
            return puw.standardize(min_alpha_sphere_radius)

    raise ArgumentError('min_alpha_sphere_radius', value=min_alpha_sphere_radius, caller=caller, message=None)

