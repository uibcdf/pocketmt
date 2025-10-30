from .Feature import Feature

class Vexity(Feature):

    def __init__(self, atom_indices=None, base_rim_indices=None, n_base_rims=None,
                 feature_index=None, feature_id=None, shape_index=None, shape_id=None,
                 type_index=None, type_id=None):
        super().__init__(atom_indices=atom_indices, shape_type='vexity', feature_type='vexity',
                         feature_index=feature_index, feature_id=feature_id,
                         shape_index=shape_index, shape_id=shape_id,
                         type_index=type_index, type_id=type_id)
        self.base_rim_indices = base_rim_indices
        self.n_base_rims = n_base_rims
        if base_rim_indices is not None:
            self.n_base_rims = len(base_rim_indices)
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

