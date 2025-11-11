import molsysmt as msm
from topomt import pyunitwizard as puw
from topomt._private.digestion import digest
from topomt._private.variables import is_all
from topomt._private.edges_list import connected_components_union_find
from scipy.spatial import cKDTree

@digest()
def fpocket(molecular_system, selection='all', structure_indices=0, min_alpha_sphere_radius='3 angstroms',
            max_alpha_sphere_radius='6 angstroms', max_neighbor_center_distance='1.73 angstroms',
            max_components_center_distance='4.5 angstroms', pbc=False, syntax='MolSysMT', skip_digestion=False):

    # pbc=True debería asegurar que el sistema es completo, sin moléculas partidas por las fronteras de la caja.

    from topomt import Topography
    from topomt.alpha_spheres import AlphaSpheres

    topography = Topography(molecular_system=molecular_system, structure_indices=structure_indices)

    molsys = topography._molsys

    # Tengo que asegurarme de que el sistema molecular a analizar no tiene aguas, cosolventes, small_molecules, etc.

    atom_indices = msm.select(molecular_system=molsys, selection=selection, syntax=syntax)

    posible_atoms_to_be_removed = msm.select(molecular_system=molsys, selection="group_type in ['water', 'ion', 'small molecule']",
                                             mask=atom_indices, syntax='MolSysMT')

    # The system could be only water, ions, small molecules, etc.
    if len(posible_atoms_to_be_removed) > 0:
        n_waters, n_ions, n_small_molecules = msm.get(molecular_system=molsys, selection=posible_atoms_to_be_removed,
                                                      n_waters=True, n_ions=True, n_small_molecules=True)
        warning_msg = (f"Removing {len(posible_atoms_to_be_removed)} atoms from the fpocket ",
                       f"analysis. These atoms belong to the following groups: n_waters={n_waters}, n_ions={n_ions}, ",
                       f"n_small_molecules={n_small_molecules}.")
        atom_indices = list(set(atom_indices) - set(posible_atoms_to_be_removed))

    # Only heavy atoms in the analysis

        atom_indices = msm.select(molecular_system=molsys, selection='atom_type not in ["H"]', mask=atom_indices)

    coordinates = msm.get(molecular_system=molsys, selection=atom_indices, structure_indices=structure_indices,
                          coordinates=True)
    #radii = molsys.get_radii(selection=selection)

    alpha_spheres = AlphaSpheres(points=coordinates[0], radii=None)

    alpha_spheres.remove_small_alpha_spheres(min_alpha_sphere_radius)
    alpha_spheres.remove_big_alpha_spheres(max_alpha_sphere_radius)

    neighbors = alpha_spheres.get_neighbors('edge')
    edges_alpha_spheres = []

    for ii, list_of_neighbors in neighbors.items():
        for jj in list_of_neighbors:
            if ii < jj:
                distance = alpha_spheres.get_centers_distance(ii, jj)
                if distance <= max_neighbor_center_distance:
                    edges_alpha_spheres.append([ii,jj])

    components = connected_components_union_find(edges_alpha_spheres)
    components_1_filter = [component for component in components if len(component)>1]

    geometric_centers_components = []
    for component in components_1_filter:
            geometric_centers_components.append(alpha_spheres.centers[component].mean(axis=0))

    geometric_centers_components = puw.utils.numpy.vstack(geometric_centers_components)
    aux_dists, aux_unit = puw.get_value_and_unit(geometric_centers_components)
    aux_threshold = puw.get_value(max_components_center_distance, to_unit=aux_unit)
    tree = cKDTree(aux_dists)
    edges_components = tree.query_pairs(r=aux_threshold)
    lumped_components = connected_components_union_find(edges_components)
    components_2_filter = [] 
    for lumped_component in lumped_components:
        lumped_component_combined = []
        for index in lumped_component:
            lumped_component_combined.extend(components_1_filter[index])
        components_2_filter.append(lumped_component_combined)

    return components_2_filter
#    return components_not_single_alpha_sphere
