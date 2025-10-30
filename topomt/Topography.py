# Topography.py
# TopoMT — Registry and hybrid view system with modern typing (Python >= 3.10)

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping, Iterator
from typing import Any, Protocol, TypeAlias, runtime_checkable, Literal

# ---------- Type aliases ----------
FeatureID: TypeAlias = str
FeatureType: TypeAlias = str
ShapeType: TypeAlias = Literal['concavity', 'convexity', 'mixed', 'boundary', 'point']
Dim: TypeAlias = Literal[0, 1, 2]
Index: TypeAlias = int


# ---------- Protocols (structural typing) ----------
@runtime_checkable
class BaseFeature(Protocol):
    feature_id: FeatureID
    feature_type: FeatureType
    shape_type: ShapeType
    dimensionality: int  # 0, 1, 2
    type_index: Index


@runtime_checkable
class Feature2D(BaseFeature, Protocol):
    # Optional containers on parent (2D)
    boundary_ids: list[FeatureID] | None
    point_ids: list[FeatureID] | None


@runtime_checkable
class Feature1D(BaseFeature, Protocol):
    # Applies to which 2D shape_types (if declared)
    applies_to: set[ShapeType] | None
    # Optional convenience backref
    parent_id: FeatureID | None


@runtime_checkable
class Feature0D(BaseFeature, Protocol):
    applies_to: set[ShapeType] | None
    parent_id: FeatureID | None


# ---------- Validators (import late to avoid cycles) ----------
from validators import validate_parent_child_compat, validate_special_rules


@dataclass
class Topography:
    """
    Canonical registry of all features (2D surfaces, 1D boundaries, 0D points).

    The registry is duck-typed via Protocols; objects need not inherit any base class,
    they only must provide the expected attributes (see BaseFeature/Feature2D/1D/0D).
    """
    # Optional catalog to enhance discovery for family collections
    # e.g. {'concavity_types': ['pocket','void',...], 'convexity_types': [...], 'mixed_types': [...]}
    catalog: Mapping[str, list[str]] | None = None

    # ---- Canonical storage ----
    _by_id: dict[FeatureID, BaseFeature] = field(default_factory=dict)
    _order: list[FeatureID] = field(default_factory=list)

    # ---- Derived indices ----
    _by_dim: dict[int, list[FeatureID]] = field(default_factory=lambda: {0: [], 1: [], 2: []})
    _by_shape: dict[ShapeType, list[FeatureID]] = field(default_factory=lambda: {
        'concavity': [], 'convexity': [], 'mixed': [], 'boundary': [], 'point': []
    })
    _by_type: dict[FeatureType, list[FeatureID]] = field(default_factory=dict)

    # (feature_type -> {type_index -> feature_id})
    _by_type_index: dict[FeatureType, dict[Index, FeatureID]] = field(default_factory=dict)

    # relations
    _children_of: dict[FeatureID, list[FeatureID]] = field(default_factory=dict)  # parent2d_id -> [child_ids]
    _parents_of: dict[FeatureID, list[FeatureID]] = field(default_factory=dict)   # child_id -> [parent2d_ids]

    # -------------------- Registration --------------------
    def register(self, feat: BaseFeature) -> None:
        fid = getattr(feat, 'feature_id', None)
        if not isinstance(fid, str) or not fid:
            raise ValueError("Feature must have a string 'feature_id'")
        if fid in self._by_id:
            raise ValueError(f"Feature id already exists: {fid}")

        ftype = getattr(feat, 'feature_type', None)
        if not isinstance(ftype, str) or not ftype:
            raise ValueError("Feature must have a string 'feature_type'")

        dim = int(getattr(feat, 'dimensionality', -1))
        if dim not in (0, 1, 2):
            raise ValueError("Feature must have 'dimensionality' in {0,1,2}")

        shape = str(getattr(feat, 'shape_type', ''))
        if shape not in ('concavity','convexity','mixed','boundary','point'):
            raise ValueError("Feature must have valid 'shape_type'")

        tindex = getattr(feat, 'type_index', None)
        if tindex is None:
            raise ValueError("Feature must have 'type_index' unique within its feature_type")
        tindex = int(tindex)

        # Canonical store
        self._by_id[fid] = feat
        self._order.append(fid)

        # Indices
        self._by_dim[dim].append(fid)
        self._by_shape[shape].append(fid)
        self._by_type.setdefault(ftype, []).append(fid)

        self._by_type_index.setdefault(ftype, {})
        if tindex in self._by_type_index[ftype]:
            raise ValueError(f"Duplicated type_index for {ftype}: {tindex}")
        self._by_type_index[ftype][tindex] = fid

        # Relations
        self._children_of.setdefault(fid, [])
        self._parents_of.setdefault(fid, [])

    # -------------------- Linking (1D/0D -> 2D) --------------------
    def link(self, child_id: FeatureID, parent2d_id: FeatureID) -> None:
        child = self._by_id[child_id]
        parent = self._by_id[parent2d_id]

        validate_parent_child_compat(child, parent)
        current_parents = self._parents_of[child_id]
        validate_special_rules(child, parent, current_parents)

        if parent2d_id not in current_parents:
            current_parents.append(parent2d_id)
            self._children_of[parent2d_id].append(child_id)

        # Sync parent with child lists if available
        if getattr(parent, 'dimensionality', None) == 2:
            if getattr(child, 'dimensionality', None) == 1:
                if not hasattr(parent, 'boundary_ids'):
                    setattr(parent, 'boundary_ids', [])
                if child_id not in parent.boundary_ids:
                    parent.boundary_ids.append(child_id)
            elif getattr(child, 'dimensionality', None) == 0:
                if not hasattr(parent, 'point_ids'):
                    setattr(parent, 'point_ids', [])
                if child_id not in parent.point_ids:
                    parent.point_ids.append(child_id)

        # Convenience backref (single parent)
        if hasattr(child, 'parent_id'):
            setattr(child, 'parent_id', parent2d_id)

    # -------------------- Views (read-only tuples) --------------------
    @property
    def features(self) -> tuple[BaseFeature, ...]:
        """All 2D features (concavity, convexity, mixed)."""
        return tuple(self._by_id[fid] for fid in self._by_dim[2])

    @property
    def concavities(self) -> tuple[BaseFeature, ...]:
        return tuple(self._by_id[fid] for fid in self._by_shape['concavity'])

    @property
    def convexities(self) -> tuple[BaseFeature, ...]:
        return tuple(self._by_id[fid] for fid in self._by_shape['convexity'])

    @property
    def mixed(self) -> tuple[BaseFeature, ...]:
        return tuple(self._by_id[fid] for fid in self._by_shape['mixed'])

    @property
    def interfaces(self) -> tuple[BaseFeature, ...]:
        # Alias for mixed (structural biology naming)
        return self.mixed

    @property
    def boundaries(self) -> tuple[BaseFeature, ...]:
        return tuple(self._by_id[fid] for fid in self._by_shape['boundary'])

    @property
    def points(self) -> tuple[BaseFeature, ...]:
        return tuple(self._by_id[fid] for fid in self._by_shape['point'])

    # -------------------- Queries --------------------
    def of_type(self, feature_type: FeatureType) -> tuple[BaseFeature, ...]:
        return tuple(self._by_id[fid] for fid in self._by_type.get(feature_type, []))

    def of_dim(self, d: Dim) -> tuple[BaseFeature, ...]:
        return tuple(self._by_id[fid] for fid in self._by_dim[d])

    def of_shape(self, shape: ShapeType) -> tuple[BaseFeature, ...]:
        return tuple(self._by_id[fid] for fid in self._by_shape[shape])

    def children_of(self, parent2d_id: FeatureID) -> tuple[BaseFeature, ...]:
        return tuple(self._by_id[fid] for fid in self._children_of.get(parent2d_id, []))

    def parents_of(self, child_id: FeatureID) -> tuple[BaseFeature, ...]:
        return tuple(self._by_id[fid] for fid in self._parents_of.get(child_id, []))

    # -------------------- Type-indexed collections (sugar) --------------------
    @property
    def pockets(self) -> 'TypeCollection':
        return TypeCollection(self, 'pocket')

    @property
    def voids(self) -> 'TypeCollection':
        return TypeCollection(self, 'void')

    @property
    def mouths(self) -> 'TypeCollection':
        return TypeCollection(self, 'mouth')

    @property
    def baserims(self) -> 'TypeCollection':
        return TypeCollection(self, 'base_rim')

    # -------------------- Family collections (hybrid) --------------------
    @property
    def concavity_types(self):
        # Lazy import to avoid circular import at module load time
        from collections_views import ConcavityCollection
        return ConcavityCollection(self, self._family_types('concavity'))

    @property
    def convexity_types(self):
        from collections_views import ConvexityCollection
        return ConvexityCollection(self, self._family_types('convexity'))

    @property
    def mixed_types(self):
        from collections_views import MixedCollection
        return MixedCollection(self, self._family_types('mixed'))

    # Build family type lists (catalog-aware + discovered)
    def _family_types(self, shape: ShapeType) -> dict[str, list[str]]:
        key = f'{shape}_types'
        listed: list[str] = list(self.catalog.get(key, [])) if self.catalog and key in self.catalog else []
        discovered: set[str] = {self._by_id[fid].feature_type for fid in self._by_shape.get(shape, [])}
        union = sorted(set(listed) | discovered)
        return {key: union}


class TypeCollection:
    """Indexable view over a specific feature_type using type_index.

    Example:
        topo.pockets[3] -> Pocket with type_index=3
    """
    def __init__(self, topo: Topography, feature_type: FeatureType):
        self._topo = topo
        self._ftype = feature_type

    def __getitem__(self, type_index: Index) -> BaseFeature:
        ids_map = self._topo._by_type_index.get(self._ftype, {})
        if type_index not in ids_map:
            raise KeyError(f"{self._ftype}[{type_index}] not found")
        fid = ids_map[type_index]
        return self._topo._by_id[fid]

    def __len__(self) -> int:
        return len(self._topo._by_type_index.get(self._ftype, {}))

    def __iter__(self) -> Iterator[BaseFeature]:
        ids_map = self._topo._by_type_index.get(self._ftype, {})
        for k in sorted(ids_map.keys()):
            yield self[k]

    def get(self, type_index: Index, default: Any = None) -> BaseFeature | Any:
        ids_map = self._topo._by_type_index.get(self._ftype, {})
        fid = ids_map.get(type_index)
        return self._topo._by_id.get(fid) if fid is not None else default
