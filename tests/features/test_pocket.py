"""
"""

import topomt as tmt
import pytest

# 12 cases with atom_indices and not boundaries or points:
# 1. instant Pocket with feature_id and no topography
# 2. instant Pocket with no feature_id and no topography
# 3. instant Pocket with feature_id and topography
# 4. instant Pocket with no feature_id and topography
# 5. add existing Pocket with feature_id and no topography to topography
# 6. add existing Pocket with no feature_id and no topography to topography
# 7. add existing Pocket with feature_id and topography to topography
# 8. add existing Pocket with no feature_id and topography to topography
# 9. add new Pocket with feature_id and no topography to topography
# 10. add new Pocket with no feature_id and no topography to topography
# 11. add new Pocket with feature_id and topography to topography
# 12. add new Pocket with no feature_id and topography to topography



# 1. instant Pocket with feature_id and no topography
def test_pocket_with_atom_indices_1():

    pocket = tmt.features.Pocket(feature_id='P1', atom_indices=[1,2,3])

    assert pocket.boundaries == set()
    assert pocket.points == set()
    assert pocket.solvent_accessible_area == None
    assert pocket.solvent_accessible_volume == None
    assert pocket.molecular_surface_area == None
    assert pocket.molecular_surface_volume == None
    assert pocket.length == None
    assert pocket.corner_points_count == None
    assert pocket.feature_id == 'P1'
    assert pocket.feature_type == 'pocket'
    assert pocket.feature_label == None
    assert pocket.source == 'TopoMT'
    assert pocket.source_id == 'P1'
    assert pocket.atom_indices == [1,2,3]
    assert pocket.atom_labels == None
    assert pocket.atom_label_format == tmt.config.defaults.atom_label_format
    assert pocket.shape_type == 'concavity'
    assert pocket.dimensionality == 2
    assert pocket._topography is None

# 2. instant Pocket with no feature_id and no topography
def test_pocket_with_atom_indices_2():

    pocket = tmt.features.Pocket(feature_id=None, atom_indices=[1,2,3])

    assert pocket.boundaries == set()
    assert pocket.points == set()
    assert pocket.solvent_accessible_area == None
    assert pocket.solvent_accessible_volume == None
    assert pocket.molecular_surface_area == None
    assert pocket.molecular_surface_volume == None
    assert pocket.length == None
    assert pocket.corner_points_count == None
    assert pocket.feature_id == None
    assert pocket.feature_type == 'pocket'
    assert pocket.feature_label == None
    assert pocket.source == 'TopoMT'
    assert pocket.source_id == None
    assert pocket.atom_indices == [1,2,3]
    assert pocket.atom_labels == None
    assert pocket.atom_label_format == tmt.config.defaults.atom_label_format
    assert pocket.shape_type == 'concavity'
    assert pocket.dimensionality == 2
    assert pocket._topography is None

# 3. instant Pocket with feature_id and topography
def test_pocket_with_atom_indices_3(topography_empty_1tcd):

    topography = topography_empty_1tcd
    pocket = tmt.features.Pocket(feature_id='P1', atom_indices=[1,2,3], topography=topography)

    assert pocket.boundaries == set()
    assert pocket.points == set()
    assert pocket.solvent_accessible_area == None
    assert pocket.solvent_accessible_volume == None
    assert pocket.molecular_surface_area == None
    assert pocket.molecular_surface_volume == None
    assert pocket.length == None
    assert pocket.corner_points_count == None
    assert pocket.feature_id == 'P1'
    assert pocket.feature_type == 'pocket'
    assert pocket.feature_label == None
    assert pocket.source == 'TopoMT'
    assert pocket.source_id == 'P1'
    assert pocket.atom_indices == [1,2,3]
    assert pocket.atom_labels == None
    assert pocket.atom_label_format == tmt.config.defaults.atom_label_format
    assert pocket.shape_type == 'concavity'
    assert pocket.dimensionality == 2
    assert id(pocket._topography) == id(topography)
    assert id(topography['P1']) == id(pocket)

# 4. instant Pocket with no feature_id and topography
def test_pocket_with_atom_indices_4(topography_empty_1tcd):

    topography = topography_empty_1tcd
    feature_id = topography._make_next_feature_id('pocket')
    pocket = tmt.features.Pocket(feature_id=None, atom_indices=[1,2,3], topography=topography)

    assert pocket.boundaries == set()
    assert pocket.points == set()
    assert pocket.solvent_accessible_area == None
    assert pocket.solvent_accessible_volume == None
    assert pocket.molecular_surface_area == None
    assert pocket.molecular_surface_volume == None
    assert pocket.length == None
    assert pocket.corner_points_count == None
    assert pocket.feature_id == feature_id
    assert pocket.feature_type == 'pocket'
    assert pocket.feature_label == None
    assert pocket.source == 'TopoMT'
    assert pocket.source_id == feature_id
    assert pocket.atom_indices == [1,2,3]
    assert pocket.atom_labels == None
    assert pocket.atom_label_format == tmt.config.defaults.atom_label_format
    assert pocket.shape_type == 'concavity'
    assert pocket.dimensionality == 2
    assert id(pocket._topography) == id(topography)
    assert id(topography[feature_id]) == id(pocket)


# 5. add existing Pocket with feature_id and no topography to topography
def test_pocket_with_atom_indices_5(topography_empty_1tcd):

    topography = topography_empty_1tcd
    pocket = tmt.features.Pocket(feature_id='P1', atom_indices=[1,2,3], topography=None)
    print(topography.features)
    topography.add_feature(pocket)

    assert id(pocket._topography) == id(topography)
    assert id(topography['P1']) == id(pocket)


# def test_add_new_pocket_1(topography_empty_1tcd):
# 
#     topography = topography_empty_1tcd
#     feature_id = topography.add_new_feature(feature_type='pocket', atom_indices=[1,2,3])
#     new_feature = topography[feature_id]
# 
#     assert new_feature.boundaries == set()
#     assert new_feature.points == set()
#     assert new_feature.solvent_accessible_area == None
#     assert new_feature.solvent_accessible_volume == None
#     assert new_feature.molecular_surface_area == None
#     assert new_feature.molecular_surface_volume == None
#     assert new_feature.length == None
#     assert new_feature.corner_points_count == None
#     assert new_feature.feature_id == feature_id
#     assert new_feature.feature_type == 'pocket'
#     assert new_feature.feature_label == None
#     assert new_feature.source == 'TopoMT'
#     assert new_feature.source_id == feature_id
#     assert new_feature.atom_indices == [1,2,3]
#     assert new_feature.atom_labels == None
#     assert new_feature.atom_label_format == tmt.config.defaults.atom_label_format
#     assert new_feature.shape_type == 'concavity'
#     assert new_feature.dimensionality == 2
#     assert id(new_feature._topography) == id(topography)

