from .Feature import Feature

class Cavity(Feature):

    def __init__(self, atom_indices=None, index=None, id=None, mouth_indices=None, n_mouths=None,
                 feature_index=None, feature_id=None, shape_index=None, shape_id=None):
        super().__init__(atom_indices=atom_indices, shape_type='concavity', feature_type='cavity',
                         feature_index=feature_index, feature_id=feature_id,
                         shape_index=shape_index, shape_id=shape_id,
                         type_index=index, type_id=id)
        self.mouth_indices = mouth_indices
        self.n_mouths = n_mouths
        if mouth_indices is not None:
            self.n_mouths = len(mouth_indices)
        self.solvent_accessible_area = None
        self.solvent_accessible_volume = None
        self.molecular_surface_area = None
        self.molecular_surface_volume = None
        self.length = None
        self.corner_points_count = None

    @property
    def index(self):
        return self.shape_index

    @index.setter
    def index(self, value):
        self.shape_index = value

    @property
    def id(self):
        return self.shape_id

    @id.setter
    def id(self, value):
        self.shape_id = value

