
"""
Type-level collections for TopoMT.

This module defines the TypeCollection class — a thin view over the
Topography registry that exposes all features of a given feature_type.
"""

from __future__ import annotations
from typing import Iterator, Any

from .base_types import FeatureID, FeatureType, BaseFeature


class TypeCollection:
    """
    A view over all features of a given feature_type in a Topography.

    Parameters
    ----------
    topo : Topography
        The Topography instance that owns the features.
    feature_type : str
        The feature_type of the features contained in this collection.
    """

    def __init__(self, topo: Any, feature_type: FeatureType):
        self._topo = topo
        self._feature_type = feature_type

    # ─────────────────────────────────────────────────────────
    # Core accessors
    # ─────────────────────────────────────────────────────────

    def __iter__(self) -> Iterator[BaseFeature]:
        """Iterate over all features of this type."""
        for feature_idx in self._topo._by_type_index.get(self._feature_type, []):
            yield self._topo._by_index[feature_idx]

    def __len__(self) -> int:
        """Number of features of this type."""
        return len(self._topo._by_type_index.get(self._feature_type, []))

    def __getitem__(self, index: int) -> BaseFeature:
        """Get a specific feature by its position in this collection."""
        indices = self._topo._by_type_index.get(self._feature_type, [])
        try:
            feature_idx = indices[index]
            return self._topo._by_index[feature_idx]
        except IndexError as exc:
            raise IndexError(f"Index {index} out of range for type '{self._feature_type}'") from exc

    # ─────────────────────────────────────────────────────────
    # Representation
    # ─────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        count = len(self)
        return f"<TypeCollection type='{self._feature_type}' size={count}>"

    # ─────────────────────────────────────────────────────────
    # Introspection helpers
    # ─────────────────────────────────────────────────────────

    @property
    def ids(self) -> list[FeatureID]:
        """List of feature IDs belonging to this type."""
        return [
            self._topo._by_index[i].feature_id
            for i in self._topo._by_type_index.get(self._feature_type, [])
        ]

    @property
    def features(self) -> list[BaseFeature]:
        """List of actual feature objects."""
        return list(self)
