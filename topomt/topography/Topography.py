from __future__ import annotations
from ..features.BaseFeature import BaseFeature, FeatureID, FeatureIndex, FeatureType, ShapeType, Dim
from collections.abc import Mapping, Iterator
from typing import Any
import molsysmt as msm


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Main class
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Topography(Mapping[str, BaseFeature]):
    """
    Central registry of all features.

    Public API uses *feature_id*.
    Internal storage and relations use *feature_index* for efficiency.
    """

    def __init__(self, molecular_system: Any | None = None, features: list[BaseFeature] | None = None) -> None:
        # main store: id → feature
        self._features: dict[FeatureID, BaseFeature] = {}

        # derived indexes
        self._by_dimensionality: dict[int, set[FeatureId]] = {0: set(), 1: set(), 2: set()}
        self._by_shape: dict[ShapeType, set[FeatureId]] = {
            "concavity": set(),
            "convexity": set(),
            "mixed": set(),
            "boundary": set(),
            "point": set(),
        }
        self._by_type: dict[FeatureType, set[FeatureId]] = {}

        # parent/child relations (by id)
        self._children_of: dict[FeatureId, set[FeatureId]] = {}
        self._parents_of: dict[FeatureId, set[FeatureId]] = {}

        # molecular system references
        self._molecular_system: Any | None = None
        self._molsys: Any | None = None

    # -----------------
    # Mapping interface
    # -----------------

    def __getitem__(self, feature_id: FeatureId) -> BaseFeature:
        """Allow: topo["Pock001"] → feature with feature_id == "Pock001"."""
        return self._features[feature_id]

    def __iter__(self) -> Iterator[int]:
        """Iterate over features in insertion order."""
        return iter(self._features.values())

    def __len__(self) -> int:
        return len(self._features)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # internal helpers
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @property
    def features(self) -> dict[FeatureID, BaseFeature]:
        return self._features

    @property
    def molecular_system(self) -> Any | None:
        return self._molecular_system

    @molecular_system.setter
    def molecular_system(self, value: Any | None) -> None:
        if value is None:
            self._molecular_system = None
            self._molsys = None
            return

        if msm.form.molsysmt_MolSys.is_form(value):
            molsys = value
        else:
            molsys = msm.convert(value, to_form="molsysmt.MolSys")

        self._molecular_system = value
        self._molsys = molsys

    @property
    def molsys(self) -> Any | None:
        return self._molsys

    @molsys.setter
    def molsys(self, value: Any | None) -> None:
        if value is None:
            self._molsys = None
        else:
            if msm.form.molsysmt_MolSys.is_form(value):
                self._molsys = value
            else:
                raise ValueError("Assigned value is not a molsysmt.MolSys object")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # public: add_feature
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def add_feature(self, feature: BaseFeature) -> None:
        """
        Add a feature to the topography.
        - automatically updates dimensional, shape, and type registries
        """

        if feature.feature_id in self._features:
            raise ValueError(f"Feature with id '{feature.feature_id}' is already in the topography.")

        # store
        self._features[feature.feature_id] = feature

        # ensure features share the topography references
        feature._topography = self

        # derived index by dimension
        self._by_dim.setdefault(feature.dimensionality, set()).add(feature.feature_id)
        # derived index by shape
        self._by_shape.setdefault(feature.shape_type, set()).add(feature.feature_id)
        # derived index by type
        self._by_type.setdefault(feature.feature_type, set()).add(feature.feature_id)

        # init empty relations
        self._children_of.setdefault(feature.feature_id, set())
        self._parents_of.setdefault(feature.feature_id, set())


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # public: connect_features
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def connect_features(self, child_feature_or_id: FeatureID | BaseFeature, parent_feature_or_id: FeatureID | BaseFeature) -> None:
        """
        """

        child_id= None
        parent_id= None

        if isinstance(child_feature_or_id, BaseFeature):
            if child.feature_id not in self._features:
                self.add_feature(child)
            child_id = child_feature_or_id.feature_id
        elif isinstance(child_feature_or_id, str):
            child_id = child_feature_or_id
            if child_id not in self._features:
                raise ValueError(f"Child feature with id '{child_id}' is not in the topography.")

        if isinstance(parent_feature_or_id, BaseFeature):
            if parent.feature_id not in self._features:
                self.add_feature(parent)
            parent_id = parent_feature_or_id.feature_id
        elif isinstance(parent_feature_or_id, str):
            parent_id = parent_feature_or_id
            if parent_id not in self._features:
                raise ValueError(f"Parent feature with id '{parent_id}' is not in the topography.")

        child = self._features[child_id]
        parent = self._features[parent_id]

        # external validators
        validate_parent_child_compat(child, parent)

        # register relations
        self._children_of[parent.feature_id].add(child_id)
        self._parents_of[child.feature_id].add(parent_id)

        # sync connections in feature objects
        if parent.dimensionality == 2:
            child._add_surface(parent_id)
            if child.dimensionality == 0:
                parent._add_point(child_id)
            elif child.dimensionality == 1:
                parent._add_boundary(child_id)
        else:
            raise ValueError('Parent feature must be 2D (Feature2D)')

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # public: lookups
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_feature_by_id(self, feature_id: FeatureID) -> BaseFeature:
        return self._features[feature_id]

    def get_features_by_type(self, feature_type: FeatureType) -> set[BaseFeature]:
        return set(self._features[aux_id] for aux_id in self._by_type[feature_type])

    def get_features_by_dimensionality(self, dimensionality: int) -> set[BaseFeature]:
        return set(self._features[aux_id] for aux_id in self._by_dimensionality[feature_type])

    def get_features_id_by_type(self, feature_type: FeatureType) -> set[FeatureId]:
        return self._by_type[feature_type]

    def get_features_id_by_dimensionality(self, dimensionality: int) -> set[FeatureId]:
        return self._by_dimensionality[dimensionality]

    def children_of(self, feature_id: FeatureID) -> set[BaseFeature]:
        return self._children_of[feature_id]

    def parents_of(self, feature_id: FeatureID) -> tuple[BaseFeature, ...]:
        return self._parents_of[feature_id]

    @property
    def concavities(self) -> set[FeatureID]:
        return self._by_shape["concavity"]

    @property
    def convexities(self) -> set[FeatureID]:
        return self._by_shape["convexity"]

    @property
    def mixed(self) -> set[FeatureID]:
        return self._by_shape["convexity"]

    @property
    def boundaries(self) -> set[FeatureID]:
        return self._by_shape["boundary"]

    @property
    def points(self) -> set[FeatureID]:
        return self._by_shape["point"]

def _validate_child_parent_compat(child: BaseFeature, parent: BaseFeature) -> Bool:

    if child.dimensionality == 0 and parent.dimensionality == 2:
        pass
    elif child.dimensionality == 1 and parent.dimensionality == 2:
        pass
    elif parent.dimensionality == 2:
        raise ValueError('Parent must be 2D (Feature2D)')
    if child.dimensionality not in (0, 1):
        raise ValueError('Child must be 0D or 1D')
    else:
        raise ValueError(f"{getattr(child, 'feature_type', '?')} does not apply to {getattr(parent, 'shape_type', '?')}")

    if child.feature_type == 'mouth' and parent.shape_type != 'concavity':
        raise ValueError('Mouth must attach to a concavity feature')

    if child.feature_type == 'base_rim' and parent.shape_type != 'convexity':
        raise ValueError('BaseRim must attach to a convexity')

