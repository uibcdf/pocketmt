import os
from topomt import pyunitwizard as puw
import molsysmt as msm
from topomt._private.path import ensure_path_exists_and_is_file, ensure_path_exists_and_is_dir

from pathlib import Path
from os import PathLike
from typing import Any

_atom_label_format="{atom_id}-{atom_name}/{group_name}/{chain_id}"

def _discover_castp_files_in_dir(base_path: PathLike[str]) -> dict[str, Path]:
    """Discover CASTp-related files in the given directory (non-recursive)."""
    base_path = Path(base_path)
    discovered: dict[str, Path] = {}

    extension_to_key = {
        ".poc": "poc",
        ".pocInfo": "poc_info",
        ".mouth": "mouth",
        ".mouthInfo": "mouth_info",
        ".pdb": "pdb",
    }

    for file_path in base_path.iterdir():
        if not file_path.is_file():
            continue
        key = extension_to_key.get(file_path.suffix)
        if key and key not in discovered:
            discovered[key] = file_path

    return discovered

def _parse_poc_file(file_path: PathLike[str]):

    poc_id_to_atom_labels = dict()

    with file_path.open('r', encoding='utf-8') as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            fields = line.split()
            if len(fields) < 13:
                raise ValueError(
                    f"Malformed CASTp entry in '{file_path}': expected at least 13 columns, got {len(fields)}."
                )
            atom_id = fields[1]
            atom_name = fields[2]
            group_name = fields[3]
            chain_id = fields[4]
            poc_id = int(fields[11])
            poc_marker = fields[12]
            if poc_marker != 'POC':
                raise ValueError(f"Unexpected marker '{poc_marker}' in .poc file '{file_path}'.")

            poc_id_to_atom_labels.setdefault(poc_id, set()).add(
                _atom_label_format.format(atom_id=atom_id, atom_name=atom_name, group_name=group_name, chain_id=chain_id)
            )

    return poc_id_to_atom_labels

def _parse_mouth_file(file_path: PathLike[str]):

    mouth_id_to_atom_labels = dict()

    with file_path.open('r', encoding='utf-8') as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            fields = line.split()
            if len(fields) < 13:
                raise ValueError(
                    f"Malformed CASTp entry in '{file_path}': expected at least 13 columns, got {len(fields)}."
                )
            atom_id = fields[1]
            atom_name = fields[2]
            group_name = fields[3]
            chain_id = fields[4]
            mouth_id = int(fields[11])
            mouth_marker = fields[12]
            if poc_marker != 'M4P':
                raise ValueError(f"Unexpected marker '{mouth_marker}' in .mouth file '{file_path}'.")

            mouth_id_to_atom_labels.setdefault(mouth_id, set()).add(
                _atom_label_format.format(atom_id=atom_id, atom_name=atom_name, group_name=group_name, chain_id=chain_id)
            )

    return mouth_id_to_atom_labels


def _parse_poc_info_file(file_path: PathLike[str]) -> dict[str, dict[str, Any]]:
    poc_id_to_poc_data: dict[int, dict[str, Any]] = {}
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
            poc_id = int(fields[2])
            entry = {
                "n_mouths": int(fields[3]),
                "solvent_accessible_area": puw.quantity(float(fields[4]), "angstroms**2"),
                "molecular_surface_area": puw.quantity(float(fields[5]), "angstroms**2"),
                "solvent_accessible_volume": puw.quantity(float(fields[6]), "angstroms**3"),
                "molecular_surface_volume": puw.quantity(float(fields[7]), "angstroms**3"),
                "length": puw.quantity(float(fields[8]), "angstroms"),
                "corner_points_count": int(fields[9]),
            }
            if len(fields) > 10:
                mouth_ids: list[int] = []
                for token in fields[10:]:
                    cleaned = token.rstrip(",")
                    if cleaned.isdigit():
                        mouth_ids.append(int(cleaned))
                if mouth_ids:
                    entry["mouth_ids"] = set(mouth_ids)
            poc_id_to_poc_data[poc_id] = entry
    return poc_id_to_poc_data


def _parse_mouth_info(file_path: PathLike) -> dict[int, dict[str, Any]]:
    mouth_id_to_mouth_data: dict[int, dict[str, Any]] = {}
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
            mouth_id = int(fields[2])
            entry = {
                "pocket_ids": set([
                    int(fields[3])
                ]) if fields[3].rstrip(":,").isdigit() else set(),
                "solvent_accessible_area": puw.quantity(float(fields[4]), "angstroms**2"),
                "molecular_surface_area": puw.quantity(float(fields[5]), "angstroms**2"),
                "solvent_accessible_length": puw.quantity(float(fields[6]), "angstroms"),
                "molecular_surface_length": puw.quantity(float(fields[7]), "angstroms"),
                "n_triangles": int(fields[8]),
            }
            if len(fields) > 9:
                for token in fields[9:]:
                    cleaned = token.rstrip(",")
                    if cleaned.isdigit():
                       entry.setdefault("pocket_ids", set()).add(int(cleaned))
            if entry.get("pocket_ids"):
                entry["pocket_ids"] = entry["pocket_ids"]
            mouth_id_to_mouth_data[mouth_id] = entry
    return mouth_id_to_mouth_data


def load_CASTp(poc_file=None, pocInfo_file=None, mouth_file=None, mouthInfo_file=None, pdb_file=None,
               zip_file=None, dir_path=None, molecular_system=None):
    """
    Load CASTp data.

    """

    if zip_file is not None:
        ensure_path_exists_and_is_file(zip_file)
        import zipfile
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall('/tmp/castp_extracted')
        dir_path = '/tmp/castp_extracted'

    if dir_path is not None:
        ensure_path_exists_and_is_dir(dir_path)
        dict_of_files_cast_files = _discover_castp_files_in_dir(dir_path)
        poc_file = dict_of_files_cast_files.get('poc', None)
        pocInfo_file = dict_of_files_cast_files.get('poc_info', None)
        mouth_file = dict_of_files_cast_files.get('mouth', None)
        mouthInfo_file = dict_of_files_cast_files.get('mouth_info', None)
        pdb_file = dict_of_files_cast_files.get('pdb', None)

    poc_id_to_atom_labels = _parse_poc_file(poc_file) if poc_file is not None else None
    poc_id_to_poc_data = _parse_poc_info_file(pocInfo_file) if pocInfo_file is not None else None
    mouth_id_to_atom_labels = _parse_mouth_file(mouth_file) if mouth_file is not None else None
    mouth_id_to_mouth_data = _parse_mouth_info_file(mouthInfo_file) if mouthInfo_file is not None else None

    from topomt.topography.Topography import Topography
    if molecular_system is None and pdb_file is not None:
        molecular_system = pdb_file
    topography = Topography(molecular_system=molecular_system)

    poc_id_to_feature_id = dict()
    mouth_id_to_feature_id = dict()

    for poc_id, atom_labels in poc_id_to_atom_labels.items():
        source_id = 'Pocket ' + str(poc_id)
        args_dict = {}
        if poc_id in poc_id_to_poc_data:
            args_dict['solvent_accessible_area'] = poc_id_to_poc_data[poc_id]['solvent_accessible_area']
            args_dict['molecular_surface_area'] = poc_id_to_poc_data[poc_id]['molecular_surface_area']
            args_dict['solvent_accessible_volume'] = poc_id_to_poc_data[poc_id]['solvent_accessible_volume']
            args_dict['molecular_surface_volume'] = poc_id_to_poc_data[poc_id]['molecular_surface_volume']
            args_dict['length'] = poc_id_to_poc_data[poc_id]['length']
            args_dict['corner_points_count'] = poc_id_to_poc_data[poc_id]['corner_points_count']
        feature_id = topography.add_new_feature(feature_type='pocket', atom_labels=atom_labels,
                                                atom_label_format=_atom_label_format, source='CASTp',
                                                source_id=source_id, **args_dict)
        poc_id_to_feature_id[poc_id] = feature_id

    for mouth_id, atom_labels in mouth_id_to_atom_labels.items():
        source_id = 'Mouth ' + str(mouth_id)
        args_dict = {}
        if mouth_id in mouth_id_to_poc_data:
            args_dict['solvent_accessible_area'] = mouth_id_to_mouth_data[mouth_id]['solvent_accessible_area']
            args_dict['molecular_surface_area'] = mouth_id_to_poc_data[mouth_id]['molecular_surface_area']
            args_dict['solvent_accessible_length'] = mouth_id_to_poc_data[mouth_id]['solvent_accessible_length']
            args_dict['molecular_surface_length'] = mouth_id_to_poc_data[mouth_id]['molecular_surface_length']
            args_dict['n_triangles'] = mouth_id_to_poc_data[mouth_id]['n_triangles']
        feature_id = topography.add_new_feature(feature_type='mouth', atom_labels=atom_labels,
                                                atom_label_format=_atom_label_format, source='CASTp',
                                                source_id=source_id, **args_dict)
        mouth_id_to_feature_id[mouth_id] = feature_id

    if zip_file is not None:
        os.remove(dir_path)

    return topography

