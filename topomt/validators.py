# validators.py
# TopoMT — Geometry/ontology validations (energy-agnostic), Python >= 3.10

from __future__ import annotations

from typing import Any
from Topography import BaseFeature, Feature0D, Feature1D, Feature2D, ShapeType


def _shape(feat: BaseFeature) -> str:
    return str(getattr(feat, 'shape_type', ''))


def _dim(feat: BaseFeature) -> int:
    try:
        return int(getattr(feat, 'dimensionality', -1))
    except Exception:
        return -1


def _applies(child: BaseFeature, parent: BaseFeature) -> bool:
    applies_to = getattr(child, 'applies_to', None)
    if applies_to is None:
        return True
    parent_shape = _shape(parent)
    vals: set[str] = set()
    for v in applies_to:
        vals.add(getattr(v, 'value', v))
    return parent_shape in vals


def validate_parent_child_compat(child: BaseFeature, parent: BaseFeature) -> None:
    """Only 1D/0D attach to 2D; child.applies_to must include parent.shape_type."""
    if _dim(parent) != 2:
        raise TypeError('Parent must be 2D (Feature2D)')
    if _dim(child) not in (0, 1):
        raise TypeError('Child must be 0D or 1D')
    if not _applies(child, parent):
        raise ValueError(f"{getattr(child, 'feature_type', '?')} does not apply to {getattr(parent, 'shape_type', '?')}")


def validate_special_rules(child: BaseFeature, parent: BaseFeature, current_parents: list[str]) -> None:
    """Special ontology rules by feature_type/shape_type."""
    ctype = str(getattr(child, 'feature_type', ''))
    pshape = _shape(parent)

    if ctype == 'mouth' and pshape != 'concavity':
        raise ValueError('Mouth must attach to a concavity')

    if ctype == 'base_rim' and pshape != 'convexity':
        raise ValueError('BaseRim must attach to a convexity')

    if ctype == 'seam':
        if pshape != 'mixed':
            raise ValueError('Seam must attach to an interface (mixed)')
        if len(current_parents) >= 2:
            raise ValueError('Seam must connect exactly two interface patches (already has two parents)')
