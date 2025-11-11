import numpy as np
from ...exceptions import ArgumentError
from ...variables import is_all

def digest_method(method, caller=None):

    if caller=='topomt.methods.fpocket.fpocket':
        if isinstance(method, str):
            return method

    return ArgumentError('method', value=method, caller=caller, message=None)

