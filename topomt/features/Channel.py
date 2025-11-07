from .Feature2D import Feature2D

class Channel(Feature2D):

    def __init__(self, feature_id, atom_indices=None, boundaries=None, points=None,
                atom_labels=None, atom_labels_format=None):
        super().__init__(feature_id, feature_type='channel', atom_indices=atom_indices,
                        boundaries=boundaries, points=points, atom_labels=atom_labels,
                        atom_labels_format=atom_labels_format)
