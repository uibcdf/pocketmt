from .BaseFeature import BaseFeature

class Feature0D(BaseFeature):

    def __init__(self, feature_id, feature_type='feature_0d', atom_indices=None,
                 atom_labels=None, atom_labels_format='atom_id/group_id/chain_id'):
        super().__init__(feature_id, feature_type=feature_type, atom_indices=atom_indices,
                        atom_labels=atom_labels, atom_labels_format=atom_labels_format)

        self.surfaces = set()

    def add_connected_surface(self, feature_or_id: 'BaseFeature | str'):

        if self._topograpy is None:
            raise ValueError('Topography is not set for this feature. Cannot add connected surface.')

        self._topograpy.connect_features(self.feature_id, feature_or_id)

    def _add_surface_id(self, surface_id: str):

        self.surfaces.add(surface_id)
