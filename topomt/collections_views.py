# collections_views.py
# TopoMT — Family collections (hybrid: explicit popular props + dynamic fallback)
from __future__ import annotations

from typing import Any
from .type_collections import TypeCollection


class _BaseFamilyCollection:
    FAMILY_KEY: str = ''  # to be set by subclasses, e.g., 'concavity_types'

    def __init__(self, topo, catalog: dict[str, list[str]]):
        self._topo = topo
        self._catalog = catalog
        self._cache: dict[str, TypeCollection] = {}

    # Get or create a cached TypeCollection for a given feature_type
    def _type(self, feature_type: str) -> TypeCollection:
        if feature_type not in self._cache:
            self._cache[feature_type] = TypeCollection(self._topo, feature_type)
        return self._cache[feature_type]

    def __getattr__(self, name: str) -> Any:
        ft = self._resolve_feature_type(name)
        if ft is None:
            raise AttributeError(name)
        return self._type(ft)

    def __dir__(self) -> list[str]:
        base = set(super().__dir__())
        family_types = set(self._catalog.get(self.FAMILY_KEY, []))
        base |= family_types | {self._pluralize(t) for t in family_types}
        return sorted(base)

    def _resolve_feature_type(self, name: str) -> str | None:
        # normalize plural/singular + some irregulars
        norm_map = {
            'ampullae': 'ampulla',
            'vestibules': 'vestibule',
            'funnels': 'funnel',
            'niches': 'niche',
            'pockets': 'pocket',
            'voids': 'void',
            'channels': 'channel',
            'grooves': 'groove',
            'clefts': 'cleft',
            'branched_channels': 'branched_channel',
            'protrusions': 'protrusion',
            'vexities': 'vexity',
            'domes': 'dome',
            'spines': 'spine',
            'knobs': 'knob',
            'buttresses': 'buttress',
            'pinnacles': 'pinnacle',
            'patches': 'patch',
            'joints': 'joint',
            'saddles': 'saddle',
            'trenches': 'trench',
        }
        norm = norm_map.get(name, name)
        family = set(self._catalog.get(self.FAMILY_KEY, []))
        return norm if norm in family else None

    def _pluralize(self, t: str) -> str:
        irregular = {'ampulla': 'ampullae', 'niche': 'niches', 'patch': 'patches'}
        if t in irregular:
            return irregular[t]
        if t.endswith('y'):
            return t[:-1] + 'ies'
        return t + 's'


class ConcavityCollection(_BaseFamilyCollection):
    FAMILY_KEY = 'concavity_types'

    # Explicit popular properties for better autocomplete
    @property
    def pockets(self) -> TypeCollection:           return self._type('pocket')
    @property
    def voids(self) -> TypeCollection:             return self._type('void')
    @property
    def channels(self) -> TypeCollection:          return self._type('channel')
    @property
    def branched_channels(self) -> TypeCollection: return self._type('branched_channel')
    @property
    def grooves(self) -> TypeCollection:           return self._type('groove')
    @property
    def clefts(self) -> TypeCollection:            return self._type('cleft')
    @property
    def funnels(self) -> TypeCollection:           return self._type('funnel')
    @property
    def vestibules(self) -> TypeCollection:        return self._type('vestibule')
    @property
    def ampullae(self) -> TypeCollection:          return self._type('ampulla')
    @property
    def niches(self) -> TypeCollection:            return self._type('niche')

    # Singular aliases
    pocket = pockets
    void = voids
    channel = channels
    branched_channel = branched_channels
    groove = grooves
    cleft = clefts
    funnel = funnels
    vestibule = vestibules
    ampulla = ampullae
    niche = niches


class ConvexityCollection(_BaseFamilyCollection):
    FAMILY_KEY = 'convexity_types'

    @property
    def vexities(self) -> TypeCollection:    return self._type('vexity')
    @property
    def protrusions(self) -> TypeCollection: return self._type('protrusion')
    @property
    def domes(self) -> TypeCollection:       return self._type('dome')
    @property
    def spines(self) -> TypeCollection:      return self._type('spine')
    @property
    def knobs(self) -> TypeCollection:       return self._type('knob')
    @property
    def buttresses(self) -> TypeCollection:  return self._type('buttress')
    @property
    def pinnacles(self) -> TypeCollection:   return self._type('pinnacle')

    vexity = vexities
    protrusion = protrusions
    dome = domes
    spine = spines
    knob = knobs
    buttress = buttresses
    pinnacle = pinnacles


class MixedCollection(_BaseFamilyCollection):
    FAMILY_KEY = 'mixed_types'

    @property
    def interfaces(self) -> TypeCollection: return self._type('interface')
    @property
    def patches(self) -> TypeCollection:    return self._type('patch')
    @property
    def joints(self) -> TypeCollection:     return self._type('joint')
    @property
    def saddles(self) -> TypeCollection:    return self._type('saddle')
    @property
    def trenches(self) -> TypeCollection:   return self._type('trench')

    interface = interfaces
    patch = patches
    joint = joints
    saddle = saddles
    trench = trenches
