FEATURE_PREFIXES = {
    'base_feature': 'BSF',
    'feature_0d': 'F0D',
    'feature_1d': 'F1D',
    'feature_2d': 'F2D',
    'pocket': 'POC',
    'void': 'VOI',
    'mouth': 'MOU',
    'channel': 'CHA',
    'branched_channel': 'BCH',
}

def make_feature_id(feature_type: str, index: int) -> str:
    prefix = FEATURE_PREFIXES.get(feature_type, feature_type[:3].upper())
    return f'{prefix}-{index}'
