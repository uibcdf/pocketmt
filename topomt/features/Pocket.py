from .Feature2D import Feature2D

class Pocket(Feature2D):

    def __init__(self, feature_id, atom_indices=None, atom_labels=None, atom_label_format=None):
        super().__init__(feature_id, feature_type='pocket', atom_indices=atom_indices,
                        atom_labels=atom_labels, atom_label_format=atom_label_format)

