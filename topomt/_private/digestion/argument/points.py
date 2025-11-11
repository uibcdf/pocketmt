from ...exceptions import ArgumentError
import numpy as np
from molsysmt import pyunitwizard as puw

functions_where_boolean = (
    )

def digest_points(points, caller=None):

    if caller is not None:

        if caller.endswith(functions_where_boolean):
            if isinstance(points, bool):
                return points

    if points is None:
        return None

    value, unit = puw.get_value_and_unit(points)

    if not puw.check(unit, dimensionality={'[L]':1}):
        raise ArgumentError('points', value=points, caller=caller, message=None)

    if not isinstance(value, np.ndarray):
        value = np.array(value)

    value = value.astype(np.float64)
    shape = value.shape

    if len(shape) == 1:
        if shape[0] == 3:
            return puw.quantity(value[np.newaxis, :], unit, standardized=True)
    elif len(shape) == 2:
        if shape[1] == 3:
            return puw.quantity(value, unit, standardized=True)
    elif len(shape)>2:
        if shape[-1] == 3:
            raise ArgumentError('points', value=points, caller=caller,
                                message='The object needs to be 2 dimensional: [n_points, 3]')

    raise ArgumentError('points', value=points, caller=caller, message=None)

