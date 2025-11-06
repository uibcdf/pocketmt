from __future__ import annotations

FeatureID = str
FeatureIndex = int
FeatureType = str
ShapeType = Literal["concavity", "convexity", "mixed", "boundary", "point"]
Dim = Literal[0, 1, 2, None]


class BaseFeature():

    def __init__(self, feature_id, feature_type=None, atom_indices=None, atom_labels=None,
                 labels_format="atom_id/group_id/chain_id"):

        self.feature_id = feature_id
        self.feature_type = feature_type
        self.atom_indices = atom_indices
        self.atom_labels = atom_labels
        self._labels_format = labels_format
        self.shape_type = None
        self.dimensionality = None
        self._topography = None

        if self.feature_type is not None:
            self._set_shape_type()
            self._set_dimensionality()

    def __repr__(self):
        return f"<Feature feature_id={self.feature_id} feature_type={self.feature_type} shape_type={self.shape_type}>"

    def info(self):
        return {
            "feature_id": self.feature_index,
            "feature_type": self.shape_type,
            "shape_type": self.shape_type,
        }

    @property
    def id(self):
        return self.feature_id

    @id.setter
    def id(self, value):
        self.feature_id = value

    @property
    def topography(self) -> Topography | None:
        return self._topography

    @property
    def molecular_system(self) -> Any | None:
        if self._topography is None:
            return None
        return self._topography.molecular_system

    @property
    def molsys(self) -> Any | None:
        if self._topography is None:
            return None
        return self._topography.molsys

    def _set_dimensionality(self):

        if self.feature_type is None:
            self.dimensionality = None
            return

        from .catalog import dimensionality_by_feature_type
        self.dimensionality = dimensionality_by_feature_type[self.feature_type]

    def _set_shape_type(self):

        if self.feature_type is None:
            self.shape_type = None
            return

        from .catalog import shape_type_by_feature_type
        self.shape_type = shape_type_by_feature_type[self.feature_type]

