from .BaseFeature import BaseFeature

class Feature2D(BaseFeature):

    def __init__(self, feature_id=None, feature_type='feature_2d', atom_indices=None,
                 atom_labels=None, atom_label_format=None, **kwargs):
        super().__init__(feature_id=feature_id, feature_type=feature_type, atom_indices=atom_indices,
                         atom_labels=atom_labels, atom_label_format=atom_label_format)

        self.boundaries = set()
        self.points = set()

        self.solvent_accessible_area = None
        self.solvent_accessible_volume = None
        self.molecular_surface_area = None
        self.molecular_surface_volume = None
        self.length = None
        self.corner_points_count = None

        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def add_connected_boundary(self, feature_or_id: 'BaseFeature | str'):

        if self._topograpy is None:
            raise ValueError('Topography is not set for this feature. Cannot add connected boundary.')

        self._topograpy.connect_features(feature_or_id, self.feature_id)

    def add_connected_point(self, feature_or_id: 'BaseFeature | str'):

        if self._topograpy is None:
            raise ValueError('Topography is not set for this feature. Cannot add connected boundary.')

        self._topograpy.connect_features(feature_or_id, self.feature_id)

    def _add_boundary_id(self, boundary_id: str):

        self.boundaries.add(boundary_id)

    def _add_point_id(self, point_id: str):

        self.points.add(point_id)
