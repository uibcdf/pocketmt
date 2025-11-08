import pytest
import topomt as tmt
from molsysmt.native.molsys import MolSys

@pytest.fixture(scope="session")
def seed_topography_empty_1tcd():
    pdb_file = tmt.demo['TcTIM']['1tcd.pdb']
    topography = tmt.Topography(molecular_system=pdb_file)
    assert topography is not None
    return topography

@pytest.fixture(scope="function")
def topography_empty_1tcd(seed_topography_empty_1tcd):
    topography = seed_topography_empty_1tcd.copy(deep=True)
    assert topography is not None
    return topography
