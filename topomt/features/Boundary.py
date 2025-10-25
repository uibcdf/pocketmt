from .Feature import Feature

class Boundary(Feature):

    def __init__(self, atom_indices=None,
                 feature_index=None, feature_id=None, shape_index=None, shape_id=None,
                 type_index=None, type_id=None):
        super().__init__(atom_indices=atom_indices, shape_type='boundary', feature_type='boundary',
                         feature_index=feature_index, feature_id=feature_id,
                         shape_index=shape_index, shape_id=shape_id,
                         type_index=type_index, type_id=type_id)
        self.solvent_accessible_area = None
        self.molecular_surface_area = None
        self.solvent_accessible_length = None
        self.molecular_surface_length = None
        self.n_triangles = None

    @property
    def index(self):
        return self.shape_index

    @id.setter
    def index(self, value):
        self.shape_index = value

    @property
    def id(self):
        return self.shape_id

    @id.setter
    def id(self, value):
        self.shape_id = value

