class Mouth():

    def __init__(self, atom_indices=None, index=None, id=None):

        self.atom_indices = atom_indices
        self.index = index
        self.id = id
        self.solvent_accessible_area = None
        self.molecular_surface_area = None
        self.solvent_accessible_length = None
        self.molecular_surface_length= None
        self.n_triangles = None

