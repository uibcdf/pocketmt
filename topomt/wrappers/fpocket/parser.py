from __future__ import annotations
from pathlib import Path
from typing import Any
import re

from .model import FpocketResult, Pocket


def parse_fpocket_output(pdb_file: str | Path, output_dir: str | Path) -> FpocketResult:
    pdb_file = Path(pdb_file).resolve()
    output_dir = Path(output_dir).resolve()

    pockets_dir = output_dir / "pockets"
    pockets: list[Pocket] = []

    if pockets_dir.exists():
        for pocket_atm in sorted(pockets_dir.glob("pocket*_atm.pdb")):
            pocket_id = _extract_pocket_id(pocket_atm.stem)
            props, atom_serials = _parse_pocket_atm(pocket_atm)

            # intentar centro desde el vert.pqr
            pocket_vert = pockets_dir / f"pocket{pocket_id}_vert.pqr"
            center = _parse_pocket_center_from_vert(pocket_vert) if pocket_vert.exists() else None

            pocket = Pocket(
                pocket_id=pocket_id,
                atom_serials=atom_serials,
                center=center,
                score=props.get("Pocket Score"),
                druggability_score=props.get("Drug Score"),
                volume_mc=props.get("Pocket volume (Monte Carlo)"),
                volume_hull=props.get("Pocket volume (convex hull)"),
                raw=props,
            )
            pockets.append(pocket)

    # info global (opcional, por si quieres guardar número de pockets, etc.)
    info_file = output_dir / f"{pdb_file.stem}_info.txt"
    metadata = _parse_global_info(info_file)

    return FpocketResult(
        source_pdb=pdb_file,
        output_dir=output_dir,
        pockets=pockets,
        metadata=metadata,
    )


def _extract_pocket_id(stem: str) -> int:
    # e.g. 'pocket12_atm' -> 12
    m = re.search(r"pocket(\d+)", stem)
    return int(m.group(1)) if m else -1


def _parse_pocket_atm(pocket_file: Path) -> tuple[dict[str, Any], list[int]]:
    """
    Lee el pocketX_atm.pdb de fpocket (como el que subiste) y extrae:
      - propiedades del HEADER
      - seriales de átomos (ATOM/HETATM)
    """
    props: dict[str, Any] = {}
    atom_serials: list[int] = []

    with pocket_file.open() as fh:
        for line in fh:
            if line.startswith("HEADER"):
                # ejemplo:
                # 'HEADER 0  - Pocket Score                      : 0.2657'
                content = line[6:].strip()
                m = re.match(r"\d+\s*-\s*(.+?):\s*(.+)", content)
                if m:
                    key = m.group(1).strip()
                    val = m.group(2).strip()
                    # intenta pasar a float
                    try:
                        val_f = float(val)
                        props[key] = val_f
                    except ValueError:
                        props[key] = val
            elif line.startswith(("ATOM  ", "HETATM")):
                serial = int(line[6:11])
                atom_serials.append(serial)

    return props, atom_serials


def _parse_pocket_center_from_vert(pocket_vert: Path) -> tuple[float, float, float] | None:
    """
    pocketX_vert.pqr tiene las “voronoi vertices” como ATOMs.
    Calculamos un centro simple como la media de esos puntos.
    """
    coords: list[tuple[float, float, float]] = []
    with pocket_vert.open() as fh:
        for line in fh:
            if line.startswith(("ATOM", "HETATM")):
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                coords.append((x, y, z))
    if not coords:
        return None
    cx = sum(c[0] for c in coords) / len(coords)
    cy = sum(c[1] for c in coords) / len(coords)
    cz = sum(c[2] for c in coords) / len(coords)
    return (cx, cy, cz)


def _parse_global_info(info_file: Path) -> dict[str, Any]:
    """
    El <pdb>_info.txt que genera fpocket tiene bloques 'Pocket N :' y luego
    'Score : ...'. Aquí podemos simplemente guardarlo para referencia.
    Si luego quieres mapearlo por pocket_id, aquí se puede refinar.
    """
    if not info_file.exists():
        return {}
    meta: dict[str, Any] = {}
    with info_file.open() as fh:
        current_pocket: str | None = None
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith("Pocket"):
                current_pocket = line.rstrip(":")
                meta.setdefault(current_pocket, {})
            elif ":" in line and current_pocket is not None:
                k, v = line.split(":", 1)
                k = k.strip()
                v = v.strip()
                try:
                    v = float(v)
                except ValueError:
                    pass
                meta[current_pocket][k] = v
    return meta

