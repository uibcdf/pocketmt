from .BaseFeature import BaseFeature

class Feature2D(BaseFeature):

    def __init__(self, feature_id, feature_type='feature_2d', atom_indices=None, boundaries=None, points=None,
                 atom_labels=None, atom_labels_format='atom_id/group_id/chain_id'):
        super().__init__(feature_id, feature_type=feature_type, atom_indices=atom_indices,
                         atom_labels=atom_labels, atom_labels_format=atom_labels_format)

        self.boundaries = []  # List of boundary objects
        self.points = []      # List of points

        self.solvent_accessible_area = None
        self.solvent_accessible_volume = None
        self.molecular_surface_area = None
        self.molecular_surface_volume = None
        self.length = None
        self.corner_points_count = None

        if boundaries is not None:
            for boundary in boundaries:
                self.add_boundary(boundary)

        if points is not None:
            for point in points:
                self.add_point(point)

    def add_boundary(self, boundary):

        from .Feature1D import Feature1D

        if not isinstance(boundary, Feature1D):
            raise TypeError(f"Boundary {boundary} is not a 1 dimensional feature.")

        if self._topography is not None:
            self._topography.connect_features(boundary, self)
        else:
            already_exists = False
            for existing_boundary in self.boundaries:
                if existing_boundary.feature_id == boundary.feature_id:
                    already_exists = True
                    warn_msg = f"Boundary with feature_id '{boundary.feature_id}' already exists. Skipping addition."
                    print(warn_msg)
                    exit
            if not already_exists:
                self.boundaries.append(boundary)
                boundary.add_surface(self)

    def add_point(self, point):

        from .Feature0D import Feature1D

        if not isinstance(boundary, Feature0D):
            raise TypeError(f"Point {point} is not a 0 dimensional feature.")

        if self._topography is not None:
            self._topography.connect_features(point, self)
        else:
            already_exists = False
            for existing_point in self.points:
                if existing_point.feature_id == point.feature_id:
                    already_exists = True
                    warn_msg = f"Point with feature_id '{point.feature_id}' already exists. Skipping addition."
                    print(warn_msg)
                    exit
            if not already_exists:
                self.points.append(boundary)
                point.add_surface(self)

