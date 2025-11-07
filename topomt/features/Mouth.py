from .Feature1D import Feature1D

class Mouth(Feature1D):

    def __init__(self, feature_id, atom_indices=None, surfaces=None,
                atom_labels=None, atom_label_format=None):
        super().__init__(feature_id, feature_type='mouth', atom_indices=atom_indices,
                        surfaces=surfaces, atom_labels=atom_labels, atom_label_format=atom_label_format)
