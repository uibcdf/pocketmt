class Pocket():

    def __init__(self, atom_indices=None, index=None, id=None):

        self.atom_indices = atom_indices
        self.index = index
        self.id = id
        self.n_mouths = None
        self.solvent_accessible_area = None
        self.solvent_accessible_volume = None
        self.molecular_surface_area = None
        self.molecular_surface_volume = None
        self.length = None
        self.corner_points_count = None

