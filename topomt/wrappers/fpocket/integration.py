
# topomt/fpocket/integration.py
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Sequence, Any

from .runner import run_fpocket
from .parser import parse_fpocket_output
from .model import FpocketResult

# Ajusta estas importaciones según tu repo real
try:
    from topomt.topography import Topography  # o topomt.Topography
except ImportError:  # fallback por si tu ruta es otra
    from topomt import Topography  # type: ignore

# intentamos tener una feature más específica
try:
    from topomt.features import Cavity  # type: ignore
    _HAS_CAVITY = True
except Exception:
    _HAS_CAVITY = False


def get_topography_with_fpocket(
    pdb_file: str | Path,
    extra_args: Sequence[str] | None = None,
) -> "Topography":
    """
    Ejecuta fpocket en un directorio temporal sobre `pdb_file`,
    parsea los pockets y los mete en una instancia de Topography.
    El directorio temporal se borra al final.

    Parameters
    ----------
    pdb_file:
        Ruta al PDB de entrada.
    extra_args:
        Argumentos extra para pasar a fpocket (por ejemplo switches de radio, etc.)

    Returns
    -------
    Topography
        Objeto topográfico con una feature por pocket.
    """
    pdb_file = Path(pdb_file).resolve()

    # creamos topografía vacía desde el principio
    topo = Topography()

    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)

        # copiar el pdb al tmp, para que fpocket genere ahí su *_out
        local_pdb = tmpdir / pdb_file.name
        shutil.copy2(pdb_file, local_pdb)

        # 1) correr fpocket en el tmp
        out_dir = run_fpocket(
            local_pdb,
            workdir=tmpdir,
            extra_args=extra_args,
        )

        # 2) parsear salida
        fp_res: FpocketResult = parse_fpocket_output(local_pdb, out_dir)

        # 3) convertir pockets -> features topoMT
        for pocket in fp_res.pockets:
            feature_obj = _pocket_to_feature(pocket)
            # aquí supongo un método add_feature; ajusta al tuyo
            topo.add_feature(feature_obj)

        # al salir del with, el tmp se borra

    return topo


def _pocket_to_feature(pocket) -> Any:
    """
    Convierte un Pocket (del modelo de fpocket) en una feature de TopoMT.
    Aquí puedes enriquecer con más campos según tu jerarquía real.
    """
    data = {
        "feature_type": "pocket",
        "shape_type": "concavity",
        "pocket_id": pocket.pocket_id,
        "atom_serials": pocket.atom_serials,
        "center": pocket.center,
        "score": pocket.score,
        "druggability_score": pocket.druggability_score,
        "volume_mc": pocket.volume_mc,
        "volume_hull": pocket.volume_hull,
    }

    if _HAS_CAVITY:
        # si tienes una clase concreta, úsala
        return Cavity(
            feature_id=pocket.pocket_id,
            center=pocket.center,
            atom_serials=pocket.atom_serials,
            score=pocket.score,
            volume=pocket.volume_mc,
            extra=data,
        )
    else:
        # fallback: devuelvo un dict; el Topography deberá aceptar dicts
        return data
