from .Boundary import Boundary

class BaseRim(Boundary):

    def __init__(self, atom_indices=None, index=None, id=None,
                 shape_index=None, shape_id=None, feature_index=None, feature_id=None):
        super().__init__(atom_indices=atom_indices,
                         feature_index=feature_index, feature_id=feature_id, shape_index=shape_index, shape_id=shape_id,
                         type_index=index, type_id=id)
        self.feature_type = "base_rim"

    @property
    def index(self):
        return self.type_index

    @id.setter
    def index(self, value):
        self.type_index = value

    @property
    def id(self):
        return self.type_id

    @id.setter
    def id(self, value):
        self.type_id = value
