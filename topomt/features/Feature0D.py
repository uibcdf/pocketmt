from .BaseFeature import BaseFeature

class Feature0D(BaseFeature):

    def __init__(self, feature_id, feature_type='feature_0d', atom_indices=None, surfaces=None,
                 atom_labels=None, atom_labels_format='atom_id/group_id/chain_id'):
        super().__init__(feature_id, feature_type=feature_type, atom_indices=atom_indices,
                        atom_labels=atom_labels, atom_labels_format=atom_labels_format)

        self.surfaces = []  # List of boundary objects

        if surfaces is not None:
            for surface in surfaces:
                self.add_surface(surface)

    def add_surface(self, surface):

        from .Feature2D import Feature2D

        if not isinstance(boundary, Feature2D):
            raise TypeError(f'Surface {boundary} is not a 2 dimensional feature.')

        if self._topography is not None:
            self._topography.connect_features(self, surface)
        else:
            already_exists = False
            for existing_surface in self.surfaces:
                if existing_surface.feature_id == surface.feature_id:
                    already_exists = True
                    warn_msg = f'Surface with feature_id {surface.feature_id} already exists. Skipping addition.'
                    print(warn_msg)
                    exit
            if not already_exists:
                self.surfaces.append(surface)
                surface.add_point(self)

