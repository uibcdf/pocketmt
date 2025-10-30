class Topography():

    def __init__(self, molecular_system=None, selection='all'):
        self.molecular_system = None
        self.selection = selection
        self.features = []
        self.
        self.point
        self.pockets = []
        self.cavities = []
        self.channels = []
        self.mouths = []
        if molecular_system is not None:
            self.molecular_system = msm.convert(molecular_system)

    def add_feature(feature, **kwargs):

        feature_type = type(feature)

        match feature_type:
            case str:

                if feature_type == 'pocket':

                    

        if isinstance(feature, Pocket):
            self.pockets.append(feature)
        elif isinstance(feature, Cavity):
            self.cavities.append(feature)
        elif isinstance(feature, Channel):
            self.channels.append(feature)
        elif isinstance(feature, Mouth):
            self.mouths.append(feature)
        else:
            raise ValueError("Unknown feature type")
