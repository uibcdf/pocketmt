"""
"""

import topomt as tmt
from molsysmt.native.molsys import MolSys
from topomt.features import Pocket
import pytest

def test_empty_Topography():

    topography = tmt.Topography()

    assert type(topography) == tmt.Topography
    assert len(topography) == 0
    assert topography.features == {}
    assert topography.molecular_system is None
    assert topography._molsys is None
    assert topography.get_features(by='type', value='pocket')==set()
    assert topography.get_features(by='type', value='pocket', as_feature_ids=True)==set()
    assert topography.get_features(by='dimensionality', value=2)==set()
    assert topography.get_features(by='dimensionality', value=2, as_feature_ids=True)==set()
    assert topography.get_features(by='shape', value='concavity')==set()
    assert topography.get_features(by='shape', value='convexity')==set()
    assert topography.get_features(by='shape', value='mixed')==set()
    assert topography.get_features(by='shape', value='boundary')==set()
    assert topography.get_features(by='shape', value='point')==set()
    assert topography._make_next_feature_id('pocket')=='POC-1'


def test_empty_Topography_with_molecular_system(topography_empty_1tcd):

    topography = topography_empty_1tcd

    assert type(topography) == tmt.Topography
    assert len(topography) == 0
    assert topography.features == {}
    assert topography.molecular_system == tmt.demo['TcTIM']['1tcd.pdb']
    assert type(topography._molsys) == MolSys
    assert topography.get_features(by='type', value='pocket')==set()
    assert topography.get_features(by='type', value='pocket', as_feature_ids=True)==set()
    assert topography.get_features(by='dimensionality', value=2)==set()
    assert topography.get_features(by='dimensionality', value=2, as_feature_ids=True)==set()
    assert topography.get_features(by='shape', value='concavity')==set()
    assert topography.get_features(by='shape', value='convexity')==set()
    assert topography.get_features(by='shape', value='mixed')==set()
    assert topography.get_features(by='shape', value='boundary')==set()
    assert topography.get_features(by='shape', value='point')==set()
    assert topography._make_next_feature_id('pocket')=='POC-1'

def test_Topography_new_pocket(topography_empty_1tcd):

    pdb_file = tmt.demo['TcTIM']['1tcd.pdb']
    topography = topography_empty_1tcd

    feature_id = topography.add_new_feature(feature_type='pocket', atom_indices=[1,2,3])    
    new_feature = topography.features[feature_id]

    assert feature_id == 'POC-1'
    assert type(topography) == tmt.Topography
    assert len(topography) == 1
    assert list(topography.features.keys()) == ['POC-1']
    assert isinstance(list(topography.features.values())[0], Pocket)
    assert isinstance(topography['POC-1'], Pocket)
    assert topography.molecular_system == tmt.demo['TcTIM']['1tcd.pdb']
    assert type(topography._molsys) == MolSys
    assert topography.get_features(by='type', value='pocket')==set([new_feature])
    assert topography.get_features(by='type', value='pocket', as_feature_ids=True)==set(['POC-1'])
    assert topography.get_features(by='dimensionality', value=2)==set([new_feature])
    assert topography.get_features(by='dimensionality', value=2, as_feature_ids=True)==set(['POC-1'])
    assert topography.get_features(by='shape', value='concavity')==set([new_feature])
    assert topography.get_features(by='shape', value='concavity', as_feature_ids=True)==set(['POC-1'])
    assert topography.get_features(by='shape', value='convexity')==set()
    assert topography.get_features(by='shape', value='convexity', as_feature_ids=True)==set()
    assert topography.get_features(by='shape', value='mixed')==set()
    assert topography.get_features(by='shape', value='mixed', as_feature_ids=True)==set()
    assert topography.get_features(by='shape', value='boundary')==set()
    assert topography.get_features(by='shape', value='boundary', as_feature_ids=True)==set()
    assert topography.get_features(by='shape', value='point')==set()
    assert topography.get_features(by='shape', value='point', as_feature_ids=True)==set()
    assert topography._make_next_feature_id('pocket')=='POC-2'
    assert topography._make_next_feature_id('void')=='VOI-1'

