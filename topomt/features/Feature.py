def _dimensionality_from_shape_type(shape_type):

    if shape_type in ["boundary"]:
        return 1
    elif shape_type in ["cavity", "convexity", "mixed"]:
        return 2
    else:
        return None

class Feature():

    def __init__(self, atom_indices=None, shape_type=None, feature_type=None,
                 feature_index=None, feature_id=None, shape_index=None, shape_id=None,
                 type_index=None, type_id=None):

        self.atom_indices = atom_indices
        self.feature_type = feature_type
        self.shape_type = shape_type
        self.feature_index = feature_index
        self.feature_id = feature_id
        self.shape_index = shape_index
        self.shape_id = shape_id
        self.type_index = type_index
        self.type_id = type_id
        self.dimensionality = _dimensionality_from_shape_type(shape_type)

    def __repr__(self):
        return f"<Feature feature_index={self.feature_index} feature_type={self.feature_type} type_index={self.type_index} type_id={self.type_id}>"

    def info(self):
        return {
            "feature_index": self.feature_index,
            "feature_id": self.feature_id,
            "shape_type": self.shape_type,
        }


    @property
    def index(self):
        return self.feature_index

    @index.setter
    def index(self, value):
        self.feature_index = value

    @property
    def id(self):
        return self.feature_id

    @id.setter
    def id(self, value):
        self.feature_id = value

