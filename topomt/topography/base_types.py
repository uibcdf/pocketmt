"""
Core type definitions for TopoMT.

This module contains the base Protocols and type aliases shared across
the entire TopoMT ecosystem. It is intentionally lightweight and does
not import any other internal module to avoid circular dependencies.

Everything here should be safe to import from anywhere.
"""

from __future__ import annotations

from typing import Protocol, Literal

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Type aliases
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FeatureID = str
FeatureIndex = int
FeatureType = str
ShapeType = Literal["concavity", "convexity", "mixed", "boundary", "point"]
Dim = Literal[0, 1, 2]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Protocols (structural typing)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BaseFeature(Protocol):
    """
    Minimal shape every feature must have in order to be registered.
    The registry may add `feature_index` at registration time.
    """
    feature_id: FeatureID
    feature_type: FeatureType
    shape_type: ShapeType
    dimensionality: int
    type_index: int


class Feature2D(BaseFeature, Protocol):
    # These may or may not be present in user-defined classes; we guard with getattr.
    boundary_ids: List[FeatureID] | None
    point_ids: List[FeatureID] | None


class Feature1D(BaseFeature, Protocol):
    applies_to: Set[ShapeType] | None
    parent_id: FeatureID | None


class Feature0D(BaseFeature, Protocol):
    applies_to: Set[ShapeType] | None
    parent_id: FeatureID | None

