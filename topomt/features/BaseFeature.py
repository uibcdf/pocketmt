from __future__ import annotations
from topomt.config import atom_label_format as default_atom_label_format
from typing import Any, Literal
from ._feature_constants import _FEATURE_TYPE_TO_CLASS_NAME, _DIMENSIONALITY_BY_FEATURE_TYPE, \
        _SHAPE_TYPE_BY_FEATURE_TYPE
import copy

FeatureID = str
FeatureIndex = int
FeatureType = str
ShapeType = Literal["concavity", "convexity", "mixed", "boundary", "point"]
Dimensionality = Literal[0, 1, 2, None]


class BaseFeature():

    def __init__(self, feature_id=None, feature_type=None, atom_indices=None, atom_labels=None,
                 atom_label_format=None, feature_label=None, source=None, source_id=None, topography=None):
        """
            atom_label_format : str, optional
            Format string for atom labels, e.g. `"{atom_name}-{atom_id}"`.
        """

        if atom_label_format is None:
            atom_label_format = default_atom_label_format

        self.feature_id = feature_id
        self.feature_type = feature_type
        self.feature_label = feature_label
        self.source = source
        self.source_id = source_id
        self.atom_indices = atom_indices
        self.atom_labels = atom_labels
        self.atom_label_format = atom_label_format
        self.shape_type = None
        self.dimensionality = None
        self._topography = None

        if self.feature_type is not None:
            self._set_shape_type()
            self._set_dimensionality()

        if topography is not None:
            self._topography = topography
            feature_id = self._topography.add_feature(self)

        if source is None:
            self.source = "TopoMT"
            self.source_id = self.feature_id

    def __repr__(self):
        class_name = _FEATURE_TYPE_TO_CLASS_NAME.get(self.feature_type)
        return f"<TopoMT {class_name} with feature_id={self.feature_id}>"


    def copy(self, deep: bool = True) -> 'BaseFeature':
        """Return a copy of the Topography object.

        Parameters
        ----------
        deep : bool, optional
            If True (default), perform a deep copy of all internal
            data structures. If False, only a shallow copy is made.
        """
        return copy.deepcopy(self) if deep else copy.copy(self)


    def __copy__(self):

        new_feature = BaseFeature()
        new_feature.feature_id = copy.copy(self.feature_id)
        new_feature.feature_type = copy.copy(self.feature_type)
        new_feature.feature_label = copy.copy(self.feature_label)
        new_feature.source = copy.copy(self.source)
        new_feature.source_id = copy.copy(self.source_id)
        new_feature.atom_indices = copy.copy(self.atom_indices)
        new_feature.atom_labels = copy.copy(self.atom_labels)
        new_feature.atom_label_format = copy.copy(self.atom_label_format)
        new_feature.shape_type = copy.copy(self.shape_type)
        new_feature.dimensionality = copy.copy(self.dimensionality)
        new_feature._topography = None

        return new_feature


    def __deepcopy__(self, memo):

        new_feature = BaseFeature()
        new_feature.feature_id = copy.deepcopy(self.feature_id, memo)
        new_feature.feature_type = copy.deepcopy(self.feature_type, memo)
        new_feature.feature_label = copy.deepcopy(self.feature_label, memo)
        new_feature.source = copy.deepcopy(self.source, memo)
        new_feature.source_id = copy.deepcopy(self.source_id, memo)
        new_feature.atom_indices = copy.deepcopy(self.atom_indices, memo)
        new_feature.atom_labels = copy.deepcopy(self.atom_labels, memo)
        new_feature.atom_label_format = copy.deepcopy(self.atom_label_format, memo)
        new_feature.shape_type = copy.deepcopy(self.shape_type, memo)
        new_feature.dimensionality = copy.deepcopy(self.dimensionality, memo)
        new_feature._topography = None

        return new_feature


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

        self.dimensionality = _DIMENSIONALITY_BY_FEATURE_TYPE[self.feature_type]

    def _set_shape_type(self):

        if self.feature_type is None:
            self.shape_type = None
            return

        self.shape_type = _SHAPE_TYPE_BY_FEATURE_TYPE[self.feature_type]

#                atom_index = topography.molecular_system.topology.get_atom_indices(atom_id=atom_id, atom_name=atom_name,
#
#
#                if len(atom_index) == 0:
#                    raise ValueError(f"Atom with id {atom_id}, name {atom_name}, group {group_name}, chain {chain_id} not found.")
#                elif len(atom_index) > 1:
#                    raise ValueError(f"Multiple atoms found for id {atom_id}, name {atom_name}, group {group_name}, chain {chain_id}.")
#                else:
#                    atom_index = atom_index[0]


