import molsysmt as msm
from molsysmt._private.digestion import digest
from molsysmt._private.variables import is_all

@digest()
def fpocket(molecular_system, selection='all', structure_indices=0, min_alpha_sphere_radius='3 angstroms',
            max_alpha_sphere_radius='6 angstroms', syntax='MolSysMT'):

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



    return alpha_spheres
