from .Feature2D import Feature2D

class Void(Feature2D):

    def __init__(self, feature_id, atom_indices=None, boundaries=None, points=None,
                atom_labels=None, atom_label_format=None):
        super().__init__(feature_id, feature_type='void', atom_indices=atom_indices,
                        boundaries=boundaries, points=points, atom_labels=atom_labels,
                        atom_label_format=atom_label_format)
