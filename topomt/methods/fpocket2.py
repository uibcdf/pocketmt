import warnings

import molsysmt as msm
from scipy.spatial import cKDTree

from topomt import Topography
from topomt.alpha_spheres import AlphaSpheres
from topomt import pyunitwizard as puw
from topomt._private.digestion import digest
from topomt._private.edges_list import connected_components_union_find


@digest()
def fpocket2(
    molecular_system,
    selection: str = 'all',
    structure_indices: int = 0,
    min_radius: str = '3.0 angstroms',  # 3.0 en el paper original
    max_radius: str = '6.0 angstroms',  # 6.0 en el paper original
    max_neighbor_dist: str = '1.73 angstroms',  # ≤ 1.73 en fpocket
    max_cluster_dist: str = '4.5 angstroms',  # ≤ 4.5 en fpocket
    max_pair_dist: str = '2.5 angstroms',  # ≤ 2.5 en fpocket
    min_contacts: int = 2,  # 2 en el paper / código
    min_spheres_per_pocket: int = 36,  # 35 en paper / 36 en código
    pbc: bool = False,
    syntax: str = 'MolSysMT',
    skip_digestion: bool = False,
):
    """
    Detect pockets/cavities inspired by FPocket using alpha-spheres.

    Step 1: local clustering of nearby alpha-spheres.
    Step 2: merge clusters whose geometric centers are close.
    Step 3: refine by merging clusters that have enough sphere-sphere contacts.
    """

    # 0) topografía + selección
    topo = Topography(molecular_system=molecular_system, structure_indices=structure_indices)
    molsys = topo._molsys

    atom_indices = msm.select(molecular_system=molsys, selection=selection, syntax=syntax)

    # quitar agua/iones/small mols
    to_remove = msm.select(
        molecular_system=molsys,
        selection="group_type in ['water', 'ion', 'small molecule']",
        mask=atom_indices,
        syntax='MolSysMT',
    )
    if len(to_remove) > 0:
        n_waters, n_ions, n_small = msm.get(
            molecular_system=molsys,
            selection=to_remove,
            n_waters=True,
            n_ions=True,
            n_small_molecules=True,
        )
        warnings.warn(
            f"Removing {len(to_remove)} atoms from fpocket analysis "
            f"(waters={n_waters}, ions={n_ions}, small_molecules={n_small})."
        )
        atom_indices = list(set(atom_indices) - set(to_remove))

    # quitar H
    atom_indices = msm.select(
        molecular_system=molsys,
        selection='atom_type not in ["H"]',
        mask=atom_indices,
        syntax='MolSysMT',
    )

    # coords
    coordinates = msm.get(
        molecular_system=molsys,
        selection=atom_indices,
        structure_indices=structure_indices,
        coordinates=True,
    )
    coords = coordinates[0]

    # esferas alfa
    alpha_spheres = AlphaSpheres(points=coords, radii=None)

    # filtro de radio
    alpha_spheres.remove_small_alpha_spheres(min_radius)
    alpha_spheres.remove_big_alpha_spheres(max_radius)

    # ================================
    # PASO 1: clustering local
    # ================================
    neighbors = alpha_spheres.get_neighbors('edge')
    edges_step1 = []
    for ii, neighs in neighbors.items():
        for jj in neighs:
            # asumimos que get_neighbors no repite pares
            dd = alpha_spheres.get_centers_distance(ii, jj)
            if dd <= max_neighbor_dist:
                edges_step1.append([ii, jj])

    alpha_components_step1 = connected_components_union_find(edges_step1)
    # fuera los de tamaño 1 (una sola alpha-sphere no es pocket)
    alpha_components_step1 = [comp for comp in alpha_components_step1 if len(comp) > 1]

    # =====================================
    # PASO 2: agrupar clusters por distancia
    # =====================================
    cluster_centers = []
    for comp in alpha_components_step1:
        cluster_centers.append(alpha_spheres.centers[comp].mean(axis=0))

    cluster_centers = puw.utils.numpy.vstack(cluster_centers)
    cluster_centers_vals, cluster_centers_unit = puw.get_value_and_unit(cluster_centers)
    max_cluster_dist_val = puw.get_value(max_cluster_dist, to_unit=cluster_centers_unit)

    tree_clusters = cKDTree(cluster_centers_vals)
    cluster_edges = list(tree_clusters.query_pairs(r=max_cluster_dist_val))
    cluster_groups = connected_components_union_find(cluster_edges)

    alpha_components_step2 = []
    for group in cluster_groups:
        merged = []
        for idx in group:
            merged.extend(alpha_components_step1[idx])
        alpha_components_step2.append(merged)

    # ==========================================
    # PASO 3: refinar uniendo por pares de esferas
    # ==========================================

    # valores numéricos para las distancias
    centers_vals, centers_unit = puw.get_value_and_unit(alpha_spheres.centers)
    max_pair_dist_val = puw.get_value(max_pair_dist, to_unit=centers_unit)

    # ordenar clusters por tamaño (desc) para unir primero los grandes
    alpha_components_step2.sort(key=len, reverse=True)

    # construir un árbol por cluster provisional
    trees = []
    for comp in alpha_components_step2:
        pts = centers_vals[comp]
        trees.append(cKDTree(pts))

    comp_edges = []
    n_comp = len(alpha_components_step2)
    for i in range(n_comp):
        # early-out si el cluster es demasiado pequeño incluso para contactar
        if len(alpha_components_step2[i]) < min_contacts:
            continue
        for j in range(i + 1, n_comp):
            if len(alpha_components_step2[j]) < min_contacts:
                continue

            # contactos de esferas entre cluster i y j
            contacts = trees[i].query_ball_tree(trees[j], r=max_pair_dist_val)

            # AJUSTE 1:
            # contar TODAS las parejas (como hace fpocket en su single-linkage),
            # no el nº de esferas distintas en contacto.
            n_pairs = sum(len(lst) for lst in contacts)

            if n_pairs >= min_contacts:
                comp_edges.append([i, j])

    if comp_edges:
        pocket_groups = connected_components_union_find(comp_edges)
        pockets = []
        for group in pocket_groups:
            merged = []
            for idx in group:
                merged.extend(alpha_components_step2[idx])
            pockets.append(merged)
    else:
        pockets = alpha_components_step2

    # AJUSTE 2:
    # descartar pockets demasiado pequeños, como hace fpocket con min_pock_nb_asph
    pockets = [p for p in pockets if len(p) >= min_spheres_per_pocket]

    return pockets

