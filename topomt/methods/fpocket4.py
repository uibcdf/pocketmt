import warnings
import numpy as np
import molsysmt as msm
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster

from topomt import Topography
from topomt.alpha_spheres import AlphaSpheres
from topomt import pyunitwizard as puw
from topomt._private.digestion import digest


_LINKAGE_MAP = {
    's': 'single',    # single-linkage
    'm': 'complete',  # maximum/complete-linkage
    'a': 'average',   # average-linkage (UPGMA)
    'c': 'centroid',  # centroid-linkage
}

_METRIC_MAP = {
    'e': 'euclidean',
    'b': 'cityblock',
    'c': 'correlation',
    # Otros códigos del help (a,u,x,s,k) no son apropiados para coords 3D de esferas;
    # si se pasan, caemos a 'euclidean' con aviso.
}


@digest()
def fpocket4(
    molecular_system,
    selection: str = 'all',
    structure_indices: int = 0,
    # Radios por defecto (FPocket4)
    min_radius: str = '3.4 angstroms',
    max_radius: str = '6.2 angstroms',
    # Corte del dendrograma (equivale al -D de FP4)
    clust_cut_dist: str = '2.4 angstroms',
    # Método de enlace (-C) y métrica (-e)
    linkage_method: str = 's',   # 's'|'m'|'a'|'c'
    distance_metric: str = 'e',  # 'e'|'b'|'c' (euclidean default)
    # Filtros finales
    min_pock_nb_asph: int = 15,      # -i 15
    apolar_min_ratio: float | None = None,  # FP4 por defecto desactiva filtro (0.0 en help => keep all)
    # Varios
    pbc: bool = False,
    syntax: str = 'MolSysMT',
    skip_digestion: bool = False,
):
    """
    FPocket4-like pipeline usando HAC:
      1) Genera alfa-esferas y filtra por radios [min_radius, max_radius].
      2) Construye matriz de distancias entre centros de alfa-esferas (métrica -e).
      3) HAC con método de enlace -C; corta dendrograma a distancia clust_cut_dist (-D).
      4) Filtra bolsillos por tamaño mínimo (>= min_pock_nb_asph) y, opcionalmente, por fracción apolar.
    Devuelve: lista de listas de índices de alfa-esferas por pocket.
    """
    # --- Selección y limpieza básica (sin aguas/iones/small, sin H) ---
    topo = Topography(molecular_system=molecular_system, structure_indices=structure_indices)
    molsys = topo._molsys

    atom_indices = msm.select(molecular_system=molsys, selection=selection, syntax=syntax)
    remove_idx = msm.select(
        molecular_system=molsys,
        selection="group_type in ['water', 'ion', 'small molecule']",
        mask=atom_indices, syntax='MolSysMT',
    )
    if len(remove_idx) > 0:
        atom_indices = list(set(atom_indices) - set(remove_idx))

    atom_indices = msm.select(
        molecular_system=molsys,
        selection='atom_type not in ["H"]',
        mask=atom_indices, syntax='MolSysMT',
    )

    coords = msm.get(
        molecular_system=molsys,
        selection=atom_indices,
        structure_indices=structure_indices,
        coordinates=True,
    )[0]

    # --- Alfa-esferas + filtros de radio ---
    alpha = AlphaSpheres(points=coords, radii=None)
    alpha.remove_small_alpha_spheres(min_radius)
    alpha.remove_big_alpha_spheres(max_radius)

    n_as = alpha.centers.shape[0]
    if n_as == 0:
        return []
    if n_as == 1:
        return [[]] if min_pock_nb_asph <= 1 else []

    # --- Métrica y método de enlace ---
    link = _LINKAGE_MAP.get(linkage_method.lower(), None)
    if link is None:
        warnings.warn(f"linkage_method '{linkage_method}' no reconocido; usando 'single'.")
        link = 'single'

    metric = _METRIC_MAP.get(distance_metric.lower(), None)
    if metric is None:
        warnings.warn(f"distance_metric '{distance_metric}' no apropiada para coords 3D; usando 'euclidean'.")
        metric = 'euclidean'

    # --- Distancias y corte en unidades coherentes ---
    centers_vals, centers_unit = puw.get_value_and_unit(alpha.centers)
    cut_val = puw.get_value(clust_cut_dist, to_unit=centers_unit)

    # pdist exige ndarray float (sin unidades)
    D = pdist(centers_vals, metric=metric)

    # SciPy: 'centroid' requiere euclidiana; avisamos si no cuadra
    if link == 'centroid' and metric != 'euclidean':
        warnings.warn("Centroid linkage requiere distancia euclídea; forzando 'euclidean'.")
        D = pdist(centers_vals, metric='euclidean')

    # --- Clustering jerárquico y corte por distancia ---
    Z = linkage(D, method=link)
    # criterion='distance' => umbral directo en la misma unidad que D (centers_unit)
    labels = fcluster(Z, t=cut_val, criterion='distance')

    # Agrupar índices por etiqueta
    pockets = []
    for lab in np.unique(labels):
        comp = np.where(labels == lab)[0].tolist()
        pockets.append(comp)

    # --- Filtro tamaño mínimo ---
    pockets = [p for p in pockets if len(p) >= min_pock_nb_asph]

    # --- Filtro apolar opcional (desactivado por defecto) ---
    if apolar_min_ratio is not None:
        ap_mask = getattr(alpha, 'is_apolar', None)
        types = getattr(alpha, 'types', None) if ap_mask is None else None
        out = []
        if ap_mask is None and types is None:
            warnings.warn("AlphaSpheres no expone tipado apolar; se omite filtro apolar.")
            return pockets
        for comp in pockets:
            if len(comp) == 0:
                continue
            if ap_mask is not None:
                nap = int(np.sum(ap_mask[np.array(comp, int)]))
            else:
                # Ajusta si tu codificación de 'types' marca apolar de otra forma
                nap = int(np.sum((types[np.array(comp, int)] == 1)))
            if (nap / len(comp)) >= apolar_min_ratio:
                out.append(comp)
        pockets = out

    return pockets

