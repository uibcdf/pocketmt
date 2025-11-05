from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from topomt import pyunitwizard as puw
from topomt.features import Mouth, Pocket
from topomt.topography.Topography import Topography


def _import_molsysmt() -> Any:
    try:
        import molsysmt as msm  # type: ignore
    except ImportError as exc:  # pragma: no cover - executed only when dependency missing
        raise ImportError(
            "The 'molsysmt' package is required to load CASTp data when only a PDB file is provided. "
            "Install it with 'pip install molsysmt'."
        ) from exc
    return msm


def _ensure_exists(path: Path, description: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"The {description} '{path}' does not exist.")
    if not path.is_file():
        raise ValueError(f"The {description} '{path}' is not a file.")


def _discover_castp_files(base_path: Path) -> dict[str, Path]:
    discovered: dict[str, Path] = {}
    extension_to_key = {
        ".poc": "poc",
        ".pocInfo": "poc_info",
        ".mouth": "mouth",
        ".mouthInfo": "mouth_info",
        ".pdb": "pdb",
    }
    for file_path in base_path.rglob("*"):
        if not file_path.is_file():
            continue
        key = extension_to_key.get(file_path.suffix)
        if key and key not in discovered:
            discovered[key] = file_path
    return discovered


def _token_to_int(token: str) -> int:
    return int(token.rstrip(":,"))


def _token_to_float(token: str) -> float:
    return float(token.rstrip(":,"))


def _get_atom_index(molecular_system: Any, atom_id: int, atom_name: str, group_name: str, chain_id: str) -> int:
    atom_indices = molecular_system.topology.get_atom_indices(
        atom_id=atom_id,
        atom_name=atom_name,
        group_name=group_name,
        chain_id=chain_id,
    )
    if not atom_indices:
        raise ValueError(
            "Atom not found in molecular system: "
            f"id={atom_id}, name={atom_name}, group={group_name}, chain={chain_id}."
        )
    if len(atom_indices) > 1:
        raise ValueError(
            "Multiple atoms found in molecular system for the combination: "
            f"id={atom_id}, name={atom_name}, group={group_name}, chain={chain_id}."
        )
    return int(atom_indices[0])


def _parse_castp_atom_file(
    file_path: Path,
    expected_marker: str,
    molecular_system: Any,
) -> dict[int, list[int]]:
    mapping: dict[int, list[int]] = {}
    with file_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            fields = line.split()
            if len(fields) < 13:
                raise ValueError(
                    f"Malformed CASTp entry in '{file_path}': expected at least 13 columns, got {len(fields)}."
                )
            atom_id = _token_to_int(fields[1])
            atom_name = fields[2]
            group_name = fields[3]
            chain_id = fields[4]
            poc_or_mouth_id = _token_to_int(fields[11])
            marker = fields[12]
            if marker != expected_marker:
                raise ValueError(
                    f"Unexpected marker '{marker}' in '{file_path}'. Expected '{expected_marker}'."
                )
            atom_index = _get_atom_index(molecular_system, atom_id, atom_name, group_name, chain_id)
            mapping.setdefault(poc_or_mouth_id, []).append(atom_index)
    return mapping


def _parse_poc_info(file_path: Path) -> dict[int, dict[str, Any]]:
    data: dict[int, dict[str, Any]] = {}
    with file_path.open("r", encoding="utf-8") as handle:
        header_skipped = False
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            if not header_skipped:
                header_skipped = True
                continue
            fields = line.split()
            if len(fields) < 10:
                raise ValueError(
                    f"Malformed entry in '{file_path}': expected at least 10 columns, got {len(fields)}."
                )
            poc_id = _token_to_int(fields[2])
            entry = {
                "n_mouths": _token_to_int(fields[3]),
                "solvent_accessible_area": puw.quantity(_token_to_float(fields[4]), "angstroms**2"),
                "molecular_surface_area": puw.quantity(_token_to_float(fields[5]), "angstroms**2"),
                "solvent_accessible_volume": puw.quantity(_token_to_float(fields[6]), "angstroms**3"),
                "molecular_surface_volume": puw.quantity(_token_to_float(fields[7]), "angstroms**3"),
                "length": puw.quantity(_token_to_float(fields[8]), "angstroms"),
                "corner_points_count": _token_to_int(fields[9]),
            }
            if len(fields) > 10:
                mouth_ids: list[int] = []
                for token in fields[10:]:
                    cleaned = token.rstrip(",")
                    if cleaned.isdigit():
                        mouth_ids.append(int(cleaned))
                if mouth_ids:
                    entry["mouth_ids"] = sorted(set(mouth_ids))
            data[poc_id] = entry
    return data


def _parse_mouth_info(file_path: Path) -> dict[int, dict[str, Any]]:
    data: dict[int, dict[str, Any]] = {}
    with file_path.open("r", encoding="utf-8") as handle:
        header_skipped = False
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            if not header_skipped:
                header_skipped = True
                continue
            fields = line.split()
            if len(fields) < 9:
                raise ValueError(
                    f"Malformed entry in '{file_path}': expected at least 9 columns, got {len(fields)}."
                )
            mouth_id = _token_to_int(fields[2])
            entry = {
                "pocket_ids": [
                    _token_to_int(fields[3])
                ] if fields[3].rstrip(":,").isdigit() else [],
                "solvent_accessible_area": puw.quantity(_token_to_float(fields[4]), "angstroms**2"),
                "molecular_surface_area": puw.quantity(_token_to_float(fields[5]), "angstroms**2"),
                "solvent_accessible_length": puw.quantity(_token_to_float(fields[6]), "angstroms"),
                "molecular_surface_length": puw.quantity(_token_to_float(fields[7]), "angstroms"),
                "n_triangles": _token_to_int(fields[8]),
            }
            if len(fields) > 9:
                for token in fields[9:]:
                    cleaned = token.rstrip(",")
                    if cleaned.isdigit():
                        entry.setdefault("pocket_ids", []).append(int(cleaned))
            if entry.get("pocket_ids"):
                entry["pocket_ids"] = sorted(set(entry["pocket_ids"]))
            data[mouth_id] = entry
    return data


def load_CASTp(
    poc_file: str | Path | None = None,
    pocInfo_file: str | Path | None = None,
    mouth_file: str | Path | None = None,
    mouthInfo_file: str | Path | None = None,
    pdb_file: str | Path | None = None,
    zip_file: str | Path | None = None,
    dir_path: str | Path | None = None,
    molecular_system: Any | None = None,
) -> Topography:
    """Load a CASTp result set into a :class:`Topography` instance.

    Parameters
    ----------
    poc_file, pocInfo_file, mouth_file, mouthInfo_file, pdb_file
        Individual CASTp files. Each argument can be a path-like object or ``None``.
    zip_file
        Optional path to the ZIP archive provided by CASTp. When given, files are extracted
        to a temporary directory and automatically removed afterwards.
    dir_path
        Directory containing the CASTp files. When provided, missing file arguments are
        discovered automatically.
    molecular_system
        Pre-loaded ``molsysmt.MolSys`` instance. If not provided, a ``pdb_file`` must be
        available so that a molecular system can be created via :mod:`molsysmt`.

    Returns
    -------
    Topography
        Populated with :class:`Pocket` and :class:`Mouth` features derived from the CASTp
        output.
    """

    temp_dir: TemporaryDirectory[str] | None = None
    try:
        poc_path = Path(poc_file) if poc_file is not None else None
        poc_info_path = Path(pocInfo_file) if pocInfo_file is not None else None
        mouth_path = Path(mouth_file) if mouth_file is not None else None
        mouth_info_path = Path(mouthInfo_file) if mouthInfo_file is not None else None
        pdb_path = Path(pdb_file) if pdb_file is not None else None

        base_dir: Path | None = None
        if zip_file is not None:
            from zipfile import ZipFile

            temp_dir = TemporaryDirectory()
            with ZipFile(Path(zip_file)) as archive:
                archive.extractall(temp_dir.name)
            base_dir = Path(temp_dir.name)
        elif dir_path is not None:
            base_dir = Path(dir_path)
            if not base_dir.exists() or not base_dir.is_dir():
                raise ValueError(f"The provided dir_path '{dir_path}' is not a valid directory.")

        if base_dir is not None:
            discovered = _discover_castp_files(base_dir)
            poc_path = poc_path or discovered.get("poc")
            poc_info_path = poc_info_path or discovered.get("poc_info")
            mouth_path = mouth_path or discovered.get("mouth")
            mouth_info_path = mouth_info_path or discovered.get("mouth_info")
            pdb_path = pdb_path or discovered.get("pdb")

        topography = Topography()

        if molecular_system is not None:
            topography.molecular_system = molecular_system
        elif pdb_path is not None:
            _ensure_exists(pdb_path, "PDB file")
            topography.molecular_system = str(pdb_path)
        elif poc_path is not None or mouth_path is not None:
            raise ValueError(
                "A molecular_system or a PDB file is required to locate atom indices for CASTp data."
            )

        molsys_obj = topography.molsys

        pocket_atoms: dict[int, list[int]] = {}
        if poc_path is not None:
            _ensure_exists(poc_path, "CASTp .poc file")
            if molsys_obj is None:
                raise ValueError("A molecular system is required to interpret the .poc file.")
            pocket_atoms = _parse_castp_atom_file(poc_path, "POC", molsys_obj)

        mouth_atoms: dict[int, list[int]] = {}
        if mouth_path is not None:
            _ensure_exists(mouth_path, "CASTp .mouth file")
            if molsys_obj is None:
                raise ValueError("A molecular system is required to interpret the .mouth file.")
            mouth_atoms = _parse_castp_atom_file(mouth_path, "M4P", molsys_obj)

        pocket_info: dict[int, dict[str, Any]] = {}
        if poc_info_path is not None:
            _ensure_exists(poc_info_path, "CASTp .pocInfo file")
            pocket_info = _parse_poc_info(poc_info_path)

        mouth_info: dict[int, dict[str, Any]] = {}
        if mouth_info_path is not None:
            _ensure_exists(mouth_info_path, "CASTp .mouthInfo file")
            mouth_info = _parse_mouth_info(mouth_info_path)

        pocket_feature_ids: dict[int, str] = {}
        for type_index, poc_id in enumerate(sorted(pocket_atoms)):
            feature_id = f"castp-pocket-{poc_id}"
            pocket = Pocket(
                atom_indices=pocket_atoms[poc_id],
                mouth_index=None,
                index=type_index,
                id=poc_id,
                feature_id=feature_id,
            )
            pocket.mouth_indices = []
            pocket.n_mouths = 0
            topography.register(pocket)
            pocket_feature_ids[poc_id] = feature_id

        mouth_feature_ids: dict[int, str] = {}
        for type_index, mouth_id in enumerate(sorted(mouth_atoms)):
            feature_id = f"castp-mouth-{mouth_id}"
            mouth = Mouth(
                atom_indices=mouth_atoms[mouth_id],
                index=type_index,
                id=mouth_id,
                feature_id=feature_id,
            )
            topography.register(mouth)
            mouth_feature_ids[mouth_id] = feature_id

        for poc_id, feature_id in pocket_feature_ids.items():
            pocket_feature = topography.get_by_id(feature_id)
            info = pocket_info.get(poc_id, {})
            if "mouth_ids" in info:
                mouth_ids = info["mouth_ids"]
                mouth_feature_ids_list: list[str] = [
                    mouth_feature_ids[mid]
                    for mid in mouth_ids
                    if mid in mouth_feature_ids
                ]
                pocket_feature.mouth_indices = mouth_feature_ids_list
                pocket_feature.n_mouths = len(mouth_feature_ids_list)
            elif pocket_feature.mouth_indices is None:
                pocket_feature.mouth_indices = []
                pocket_feature.n_mouths = 0
            pocket_feature.solvent_accessible_area = info.get("solvent_accessible_area")
            pocket_feature.molecular_surface_area = info.get("molecular_surface_area")
            pocket_feature.solvent_accessible_volume = info.get("solvent_accessible_volume")
            pocket_feature.molecular_surface_volume = info.get("molecular_surface_volume")
            pocket_feature.length = info.get("length")
            pocket_feature.corner_points_count = info.get("corner_points_count")
            if "n_mouths" in info and not info.get("mouth_ids"):
                pocket_feature.n_mouths = info["n_mouths"]

        mouth_to_pockets: dict[int, list[str]] = {}
        for mouth_id, feature_id in mouth_feature_ids.items():
            mouth_feature = topography.get_by_id(feature_id)
            info = mouth_info.get(mouth_id, {})
            mouth_feature.solvent_accessible_area = info.get("solvent_accessible_area")
            mouth_feature.molecular_surface_area = info.get("molecular_surface_area")
            mouth_feature.solvent_accessible_length = info.get("solvent_accessible_length")
            mouth_feature.molecular_surface_length = info.get("molecular_surface_length")
            mouth_feature.n_triangles = info.get("n_triangles")
            pocket_ids = info.get("pocket_ids", [])
            if pocket_ids:
                mouth_to_pockets[mouth_id] = [
                    pocket_feature_ids[pocket_id]
                    for pocket_id in pocket_ids
                    if pocket_id in pocket_feature_ids
                ]

        if mouth_to_pockets:
            for poc_id, feature_id in pocket_feature_ids.items():
                pocket_feature = topography.get_by_id(feature_id)
                related_mouths = [
                    mouth_feature_ids[mid]
                    for mid, pocket_ids in mouth_to_pockets.items()
                    if feature_id in pocket_ids
                ]
                if related_mouths:
                    pocket_feature.mouth_indices = related_mouths
                    pocket_feature.n_mouths = len(related_mouths)

        return topography
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()

