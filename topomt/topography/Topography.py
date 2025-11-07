from __future__ import annotations
from ..features.BaseFeature import BaseFeature, FeatureID, FeatureIndex, FeatureType, ShapeType, Dimensionality
from collections.abc import Mapping, Iterator
from typing import Any
import molsysmt as msm
from topomt.features.feature_id import make_feature_id as _make_feature_id
from topomt.features import _FEATURE_TYPE_REGISTRY

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

        if molecular_system is not None:
            self.molecular_system = molecular_system
            self.molsys = msm.convert(molecular_system, to_form='molsysmt.MolSys')

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

        self._molecular_system = value

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
    # public: add_feature and add_new_feature
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def add_feature(self, feature: BaseFeature) -> FeatureID | None:
        """
        Add a feature to the topography.
        - automatically updates dimensional, shape, and type registries
        """

        new_feature_id = False
        if feature.feature_id is None:
            feature_id = self._make_next_feature_id(feature.feature_type)
            feature.feature_id = feature_id
            new_feature_id = True
        else:
            feature_id = feature.feature_id
            if feature_id in self._features:
                raise ValueError(f"Feature with id '{feature_id}' is already in the topography.")

        # store
        self._features[feature_id] = feature

        # ensure features share the topography references
        feature._topography = self

        # derived index by dimension
        self._by_dimensionality.setdefault(feature.dimensionality, set()).add(feature_id)
        # derived index by shape
        self._by_shape.setdefault(feature.shape_type, set()).add(feature_id)
        # derived index by type
        self._by_type.setdefault(feature.feature_type, set()).add(feature_id)

        # init empty relations
        self._children_of.setdefault(feature_id, set())
        self._parents_of.setdefault(feature_id, set())

        if new_feature_id:
            return feature_id
        else:
            return None


    def add_new_feature(
        self,
        feature_type: str,
        feature_id: FeatureID | None = None,
        atom_indices: list[int] | None = None,
        atom_labels: list[str] | None = None,
        atom_label_format: str | None = None,
        **kwargs,
    ) -> FeatureType | None:
        """Create a feature of the given type and add it to the topography.
    
        Parameters
        ----------
        feature_type : str
            Name of the feature type, e.g. "Pocket", "Void", "Mouth".
        atom_indices : list[int], optional
            Atom indices associated to this feature, if relevant.
        **kwargs
            Extra arguments specific to the concrete feature class.
    
        Returns
        -------
        BaseFeature
            The created feature instance.
        """
        feature_class = _FEATURE_TYPE_REGISTRY.get(feature_type.lower())
        if feature_class is None:
            raise ValueError(f"Unknown feature_type {feature_type!r}")

        new_feature_id = False
        if feature_id is None:
            feature_id = self._make_next_feature_id(feature_type)
            new_feature_id = True

        new_feature = feature_class(feature_id=feature_id, atom_indices=atom_indices, atom_labels=atom_labels,
                                    atom_label_format=atom_label_format, **kwargs)

        self.add_feature(new_feature)

        if new_feature_id:
            return feature_id
        else:
            return None

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
        if feature_id not in self._features:
            raise ValueError(f"Feature with id '{feature_id}' is not in the topography.")
        else:
            return self._features[feature_id]

    def get_features_by_type(self, feature_type: FeatureType) -> set[BaseFeature]:
        if feature_type not in self._by_type:
            return set()
        else:
            return set(self._features[aux_id] for aux_id in self._by_type[feature_type])

    def get_features_by_dimensionality(self, dimensionality: Dimensionality) -> set[BaseFeature]:
        if dimensionality not in self._by_dimensionality:
            return set()
        else:
            return set(self._features[aux_id] for aux_id in self._by_dimensionality[dimensionality])

    def get_feature_ids_by_type(self, feature_type: FeatureType) -> set[FeatureId]:
        if feature_type not in self._by_type:
            return set()
        else:
            return self._by_type[feature_type]

    def get_feature_ids_by_dimensionality(self, dimensionality: Dimensionality) -> set[FeatureId]:
        if dimensionality not in self._by_dimensionality:
            return set()
        else:
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

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # auxiliary functions
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _make_next_feature_id(self, feature_type: FeatureType) -> FeatureID:
        """
        Generate the next default feature id for a given feature type.
        E.g., for feature_type 'pocket', returns 'POC-1', 'VOI-20', etc.
        """

        n_features_of_type = len(self._by_type.get(feature_type, []))
        return _make_feature_id(feature_type, n_features_of_type+1)


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

