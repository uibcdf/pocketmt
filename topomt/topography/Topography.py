from __future__ import annotations
from ..features.BaseFeature import BaseFeature, FeatureID, FeatureIndex, FeatureType, ShapeType, Dim

from .type_collections import TypeCollection
from collections.abc import Mapping, Iterator
from .validators import validate_parent_child_compat, validate_special_rules
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

    def add_feature(self, feature: BaseFeature) -> FeatureIndex:
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
        self._by_dim.setdefault(feature.dimensionality, set()).append(feature.feature_id)
        # derived index by shape
        self._by_shape.setdefault(feature.shape_type, set()).append(feature.feature_id)
        # derived index by type
        self._by_type.setdefault(feature.feature_type, set()).append(feature.feature_id)

        # init empty relations
        self._children_of.setdefault(feature.feature_id, set())
        self._parents_of.setdefault(feature.feature_id, set())


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # public: linking
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def connect_features(self, child: FeatureID | BaseFeature, parent: FeatureID | BaseFeature) -> None:
        """
        """

        if isinstance(child, str):
            child = self._features[child]
        if isinstance(parent, str):
            parent = self._features[parent]

        # external validators
        validate_parent_child_compat(child, parent)
        current_parents_ids = [
            self._by_index[p_idx].feature_id
            for p_idx in self._parents_of.get(child_idx, [])
        ]
        validate_special_rules(child, parent, current_parents_ids)

        # register relations
        self._children_of[parent_idx].append(child_idx)
        self._parents_of[child_idx].append(parent_idx)

        # sync parent lists if present
        if getattr(parent, "dimensionality", None) == 2:
            # child is 1D → boundary_ids
            if getattr(child, "dimensionality", None) == 1:
                current = getattr(parent, "boundary_ids", None)
                if current is None:
                    parent.boundary_ids = []
                if child.feature_id not in parent.boundary_ids:
                    parent.boundary_ids.append(child.feature_id)
            # child is 0D → point_ids
            if getattr(child, "dimensionality", None) == 0:
                current = getattr(parent, "point_ids", None)
                if current is None:
                    parent.point_ids = []
                if child.feature_id not in parent.point_ids:
                    parent.point_ids.append(child.feature_id)

        # write parent_id on child if present
        if hasattr(child, "parent_id"):
            setattr(child, "parent_id", parent.feature_id)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # public: lookups
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_by_id(self, feature_id: FeatureID) -> BaseFeature:
        """Return the feature object given its public id."""
        idx = self._ensure_index_from_id(feature_id)
        return self._by_index[idx]

    @property
    def features(self) -> tuple[BaseFeature, ...]:
        """All 2D features."""
        return tuple(self._by_index[idx] for idx in self._by_dim.get(2, []))

    @property
    def concavities(self) -> tuple[BaseFeature, ...]:
        return tuple(self._by_index[idx] for idx in self._by_shape.get("concavity", []))

    @property
    def convexities(self) -> tuple[BaseFeature, ...]:
        return tuple(self._by_index[idx] for idx in self._by_shape.get("convexity", []))

    @property
    def mixed(self) -> tuple[BaseFeature, ...]:
        return tuple(self._by_index[idx] for idx in self._by_shape.get("mixed", []))

    @property
    def interfaces(self) -> tuple[BaseFeature, ...]:
        return self.mixed

    @property
    def boundaries(self) -> tuple[BaseFeature, ...]:
        return tuple(self._by_index[idx] for idx in self._by_shape.get("boundary", []))

    @property
    def points(self) -> tuple[BaseFeature, ...]:
        return tuple(self._by_index[idx] for idx in self._by_shape.get("point", []))

    def of_type(self, feature_type: FeatureType) -> tuple[BaseFeature, ...]:
        return tuple(self._by_index[idx] for idx in self._by_type.get(feature_type, []))

    def of_dim(self, dim: int) -> tuple[BaseFeature, ...]:
        return tuple(self._by_index[idx] for idx in self._by_dim.get(dim, []))

    def of_shape(self, shape: ShapeType) -> tuple[BaseFeature, ...]:
        return tuple(self._by_index[idx] for idx in self._by_shape.get(shape, []))

    def children_of(self, feature_id: FeatureID) -> tuple[BaseFeature, ...]:
        idx = self._ensure_index_from_id(feature_id)
        return tuple(self._by_index[ch_idx] for ch_idx in self._children_of.get(idx, []))

    def parents_of(self, feature_id: FeatureID) -> tuple[BaseFeature, ...]:
        idx = self._ensure_index_from_id(feature_id)
        return tuple(self._by_index[p_idx] for p_idx in self._parents_of.get(idx, []))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # sugar collections
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @property
    def pockets(self) -> TypeCollection:
        return TypeCollection(self, "pocket")

    @property
    def voids(self) -> TypeCollection:
        return TypeCollection(self, "void")

    @property
    def mouths(self) -> TypeCollection:
        return TypeCollection(self, "mouth")

    @property
    def baserims(self) -> TypeCollection:
        return TypeCollection(self, "base_rim")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # family views (needs collections_views)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _family_types(self, shape: ShapeType) -> list[str]:
        declared = self._catalog.get(shape, [])
        discovered: set[str] = set()
        for idx in self._by_shape.get(shape, []):
            feat = self._by_index[idx]
            discovered.add(feat.feature_type)
        ordered = list(declared)
        for ft in sorted(discovered):
            if ft not in ordered:
                ordered.append(ft)
        return ordered

    @property
    def concavity_types(self):
        from .collections_views import ConcavityCollection
        return ConcavityCollection(self, self._family_types("concavity"))

    @property
    def convexity_types(self):
        from .collections_views import ConvexityCollection
        return ConvexityCollection(self, self._family_types("convexity"))

    @property
    def interface_types(self):
        from .collections_views import InterfaceCollection
        return InterfaceCollection(self, self._family_types("mixed"))


def _validate_child_parent_compat(child: BaseFeature, parent: BaseFeature) -> Bool:
    output = False
    if child.dimensionality == 0 and parent.dimensionality == 2:
        output = True
    elif child.dimensionality == 1 and parent.dimensionality == 2:
        output = True
    elif parent.dimensionality == 2:
        raise ValueError('Parent must be 2D (Feature2D)')
    if child.dimensionality not in (0, 1):
        raise ValueError('Child must be 0D or 1D')
    else:
        raise ValueError(f"{getattr(child, 'feature_type', '?')} does not apply to {getattr(parent, 'shape_type', '?')}")

