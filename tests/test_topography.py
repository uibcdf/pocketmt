"""
"""

import topomt as tmt
from molsysmt.native.molsys import MolSys
from topomt.features import Pocket
import pytest

@pytest.fixture
def topography_empty_1tcd():
    pdb_file = tmt.demo['TcTIM']['1tcd.pdb']
    topography = tmt.Topography(molecular_system=pdb_file)
    return topography

def test_empty_Topography():

    topography = tmt.Topography()

    assert type(topography) == tmt.Topography
    assert len(topography) == 0
    assert topography.features == {}
    assert topography.molecular_system is None
    assert topography.molsys is None
    assert topography.get_features_by_type('pocket')==set()
    assert topography.get_features_by_dimensionality(2)==set()
    assert topography.get_feature_ids_by_type('pocket')==set()
    assert topography.get_feature_ids_by_dimensionality(2)==set()
    assert topography.concavities==set()
    assert topography.convexities==set()
    assert topography.mixed==set()
    assert topography.boundaries==set()
    assert topography.points==set()
    assert topography._make_next_feature_id('pocket')=='POC-1'


def test_empty_Topography_with_molecular_system(topography_empty_1tcd):

    pdb_file = tmt.demo['TcTIM']['1tcd.pdb']
    topography = topography_empty_1tcd

    assert type(topography) == tmt.Topography
    assert len(topography) == 0
    assert topography.features == {}
    assert topography.molecular_system == pdb_file
    assert type(topography.molsys) == MolSys
    assert topography.get_features_by_type('pocket')==set()
    assert topography.get_features_by_dimensionality(2)==set()
    assert topography.get_feature_ids_by_type('pocket')==set()
    assert topography.get_feature_ids_by_dimensionality(2)==set()
    assert topography.concavities==set()
    assert topography.convexities==set()
    assert topography.mixed==set()
    assert topography.boundaries==set()
    assert topography.points==set()
    assert topography._make_next_feature_id('pocket')=='POC-1'

def test_Topography_new_pocket(topography_empty_1tcd):

    pdb_file = tmt.demo['TcTIM']['1tcd.pdb']
    topography = topography_empty_1tcd

    feature_id = topography.add_new_feature(feature_type='pocket', atom_indices=[1,2,3])    
    new_feature = topography.features[feature_id]

    assert type(topography) == tmt.Topography
    assert len(topography) == 1
    assert list(topography.features.keys()) == ['POC-1']
    assert type(list(topography.features.values())[0] == Pocket)
    assert feature_id == 'POC-1'
    assert topography.molecular_system == pdb_file
    assert type(topography.molsys) == MolSys
    assert topography.get_features_by_type('pocket')==set([new_feature])
    assert topography.get_features_by_type('void')==set()
    assert topography.get_features_by_dimensionality(0)==set()
    assert topography.get_features_by_dimensionality(1)==set()
    assert topography.get_features_by_dimensionality(2)==set([new_feature])
    assert topography.get_feature_ids_by_type('pocket')==set(['POC-1'])
    assert topography.get_feature_ids_by_dimensionality(0)==set()
    assert topography.get_feature_ids_by_dimensionality(1)==set()
    assert topography.get_feature_ids_by_dimensionality(2)==set(['POC-1'])
    assert topography.concavities==set(['POC-1'])
    assert topography.convexities==set()
    assert topography.mixed==set()
    assert topography.boundaries==set()
    assert topography.points==set()
    assert topography._make_next_feature_id('pocket')=='POC-2'
    assert topography._make_next_feature_id('void')=='VOI-1'
    assert new_feature.boundaries == set()
    assert new_feature.points == set()
    assert new_feature.solvent_accessible_area == None
    assert new_feature.solvent_accessible_volume == None
    assert new_feature.molecular_surface_area == None
    assert new_feature.molecular_surface_volume == None
    assert new_feature.length == None
    assert new_feature.corner_points_count == None
    assert new_feature.feature_id == feature_id
    assert new_feature.feature_type == 'pocket'
    assert new_feature.feature_label == None
    assert new_feature.source == 'TopoMT'
    assert new_feature.source_id == feature_id
    assert new_feature.atom_indices == [1,2,3]
    assert new_feature.atom_labels == None
    assert new_feature.atom_label_format == topomt.config.defaults.atom_label_format
    assert new_feature.shape_type == 'concavity'
    assert new_feature.dimensionality == 2
    assert new_feature._topography == topography

