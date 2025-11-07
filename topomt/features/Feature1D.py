from .BaseFeature import BaseFeature

class Feature1D(BaseFeature):

    def __init__(self, feature_id=None, feature_type='feature1D', atom_indices=None,
                 atom_labels=None, atom_label_format=None, **kwargs):
        super().__init__(feature_id=feature_id, feature_type=feature_type, atom_indices=atom_indices,
                         atom_labels=atom_labels, atom_label_format=atom_label_format)

        self.surfaces = set()

        self.solvent_accessible_area = None
        self.solvent_accessible_length = None
        self.molecular_surface_area = None
        self.molecular_surface_length = None
        self.n_triangles = None

        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_connected_surface(self, feature_or_id: 'BaseFeature | str'):

        if self._topograpy is None:
            raise ValueError('Topography is not set for this feature. Cannot add connected surface.')

        self._topograpy.connect_features(self.feature_id, feature_or_id)

    def _add_surface_id(self, surface_id: str):

        self.surfaces.add(surface_id)
