from __future__ import annotations
from .base_types import (
    BaseFeature,
    FeatureID,
    FeatureIndex,
    FeatureType,
    ShapeType,
    Dim,
)
from .type_collections import TypeCollection
from collections.abc import Mapping, Iterator
from .validators import validate_parent_child_compat, validate_special_rules
from typing import Any, Callable, ClassVar


def _import_molsysmt() -> Any:
    try:
        import molsysmt as msm  # type: ignore
    except ImportError as exc:  # pragma: no cover - executed only when dependency missing
        raise ImportError(
            "The 'molsysmt' package is required to convert molecular systems into 'molsysmt.MolSys'. "
            "Install it with 'pip install molsysmt'."
        ) from exc
    return msm


def _is_molsys_instance(candidate: Any) -> bool:
    cls = candidate.__class__
    name = getattr(cls, "__name__", "")
    module = getattr(cls, "__module__", "")
    return name == "MolSys" and module.startswith("molsysmt")



# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Main class
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Topography(Mapping[int, BaseFeature]):
    """
    Central registry of all features.

    Public API uses *feature_id*.
    Internal storage and relations use *feature_index* for efficiency.
    """

    def __init__(
        self,
        catalog: dict[str, list[str]] | None = None,
        *,
    ) -> None:
        # main store: index → feature
        self._by_index: dict[FeatureIndex, BaseFeature] = {}
        # auxiliary: id → index
        self._by_id: dict[FeatureID, FeatureIndex] = {}
        # registration order (indexes)
        self._order: list[FeatureIndex] = []

        # derived indexes
        self._by_dim: dict[int, list[FeatureIndex]] = {0: [], 1: [], 2: []}
        self._by_shape: dict[ShapeType, list[FeatureIndex]] = {
            "concavity": [],
            "convexity": [],
            "mixed": [],
            "boundary": [],
            "point": [],
        }
        self._by_type: dict[FeatureType, list[FeatureIndex]] = {}
        self._by_type_index: dict[FeatureType, dict[int, FeatureIndex]] = {}

        # parent/child relations (by index)
        self._children_of: dict[FeatureIndex, list[FeatureIndex]] = {}
        self._parents_of: dict[FeatureIndex, list[FeatureIndex]] = {}

        # optional catalog of known types per shape family
        self._catalog = catalog or {}

        # counter to assign feature_index when not present
        self._next_feature_index: int = 0

        # molecular system references
        self._molecular_system: Any | None = None
        self._molsys: Any | None = None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Mapping interface (index → feature)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def __getitem__(self, key: int) -> BaseFeature:
        """Allow: topo[3] → feature with feature_index == 3."""
        return self._by_index[key]

    def __iter__(self) -> Iterator[int]:
        """Iterate over feature indexes in registration order."""
        # puedes devolver iter(self._by_index), pero usar _order conserva el orden de registro
        return iter(self._order)

    def __len__(self) -> int:
        return len(self._by_index)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # internal helpers
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @property
    def molecular_system(self) -> Any | None:
        return self._molecular_system

    @molecular_system.setter
    def molecular_system(self, value: Any | None) -> None:
        if value is None:
            self._molecular_system = None
            self._molsys = None
            return
        molsys = msm.convert(value, to_form='molsysmt.MolSys')
        self._molecular_system = value
        self._molsys = molsys

    @property
    def molsys(self) -> Any | None:
        return self._molsys

    @molsys.setter
    def molsys(self, value: Any | None) -> None:
        if value is None:
            if _is_molsys_instance(self._molecular_system):
                self._molecular_system = None
            self._molsys = None
            return
        if not _is_molsys_instance(value):
            raise TypeError("Topography.molsys must be a 'molsysmt.MolSys' instance.")
        self._molsys = value
        if self._molecular_system is None or _is_molsys_instance(self._molecular_system):
            self._molecular_system = value

    def _ensure_index_from_id(self, feature_id: FeatureID) -> FeatureIndex:
        try:
            return self._by_id[feature_id]
        except KeyError:
            raise KeyError(f"Feature id '{feature_id}' is not registered")

    def _register_indices(self, feat: BaseFeature, idx: FeatureIndex) -> None:
        # by dimension
        self._by_dim.setdefault(feat.dimensionality, []).append(idx)
        # by shape
        self._by_shape.setdefault(feat.shape_type, []).append(idx)
        # by type
        self._by_type.setdefault(feat.feature_type, []).append(idx)
        # by (type, type_index)
        self._by_type_index.setdefault(feat.feature_type, {})[feat.type_index] = idx
        # init empty relations
        self._children_of.setdefault(idx, [])
        self._parents_of.setdefault(idx, [])

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # public: register
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def register(self, feat: BaseFeature) -> FeatureIndex:
        """
        Register a feature.
        - requires a feature_id
        - assigns an internal feature_index if missing
        """
        if not hasattr(feat, "feature_id"):
            raise ValueError("A feature must have a 'feature_id' attribute")

        # if user didn't define feature_index, we assign one
        raw_idx = getattr(feat, "feature_index", None)
        if raw_idx is None:
            idx = self._next_feature_index
            self._next_feature_index += 1
            setattr(feat, "feature_index", idx)
        else:
            idx = int(raw_idx)
            if idx in self._by_index:
                raise ValueError(f"Feature index {idx} is already registered")
            self._next_feature_index = max(self._next_feature_index, idx + 1)

        # store
        self._by_index[idx] = feat
        self._by_id[feat.feature_id] = idx
        self._order.append(idx)

        # ensure features share the topography references
        if hasattr(feat, "topography"):
            try:
                feat.topography = self  # type: ignore[attr-defined]
            except AttributeError:
                setattr(feat, "topography", self)
        else:
            setattr(feat, "topography", self)

        # derived indexes
        self._register_indices(feat, idx)

        return idx

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # public: linking
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def link(self, child_id: FeatureID, parent2d_id: FeatureID) -> None:
        """
        Link an already registered child feature to a 2D parent feature.
        Both ids are public IDs; internally we switch to indexes.
        """
        child_idx = self._ensure_index_from_id(child_id)
        parent_idx = self._ensure_index_from_id(parent2d_id)

        child = self._by_index[child_idx]
        parent = self._by_index[parent_idx]

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
