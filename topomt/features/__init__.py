from .BaseFeature import BaseFeature
from .Feature0D import Feature0D
from .Feature1D import Feature1D
from .Feature2D import Feature2D
from .Void import Void
from .Pocket import Pocket
from .Channel import Channel
from .BranchedChannel import BranchedChannel
from .Mouth import Mouth

_FEATURE_TYPE_REGISTRY = {
    'base_feature': BaseFeature,
    'feature_0d': Feature0D,
    'feature_1d': Feature1D,
    'feature_2d': Feature2D,
    'pocket': Pocket,
    'void': Void,
    'mouth': Mouth,
    'channel': Channel,
    'branched_channel': BranchedChannel,
}

_FEATURE_TYPE_ALIASES = {
    'BaseFeature': 'base_feature',
    'Feature0D': 'feature_0d',
    'Feature1D': 'feature_1d',
    'Feature2D': 'feature_2d',
    'Pocket': 'pocket',
    'Void': 'void',
    'Mouth': 'mouth',
    'Channel': 'channel',
    'BranchedChannel': 'branched_channel',
}
