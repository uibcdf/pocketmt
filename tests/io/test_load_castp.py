from __future__ import annotations

import importlib
import shutil
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Iterable
from zipfile import ZipFile

import pytest

import topomt


@dataclass(frozen=True)
class _DummyAtom:
    index: int
    atom_id: int
    atom_name: str
    group_name: str
    chain_id: str


class _DummyTopology:
    def __init__(self, atoms: Iterable[_DummyAtom]) -> None:
        self._atoms = tuple(atoms)

    def get_atom_indices(
        self,
        *,
        atom_id: int | None = None,
        atom_name: str | None = None,
        group_name: str | None = None,
        chain_id: str | None = None,
    ) -> list[int]:
        matches: list[int] = []
        for atom in self._atoms:
            if atom_id is not None and atom.atom_id != atom_id:
                continue
            if atom_name is not None and atom.atom_name != atom_name:
                continue
            if group_name is not None and atom.group_name != group_name:
                continue
            if chain_id is not None and atom.chain_id != chain_id:
                continue
            matches.append(atom.index)
        return matches


class _DummyMolSys:
    def __init__(self, atoms: Iterable[_DummyAtom]) -> None:
        self.topology = _DummyTopology(atoms)


_DummyMolSys.__name__ = "MolSys"  # type: ignore[attr-defined]
_DummyMolSys.__module__ = "molsysmt.native"  # type: ignore[attr-defined]


class _FeatureStubBase:
    feature_type: str
    shape_type: str
    dimensionality: int

    def __init__(self) -> None:
        self._topography: topomt.Topography | None = None

    @property
    def topography(self) -> topomt.Topography | None:
        return self._topography

    @topography.setter
    def topography(self, value: topomt.Topography | None) -> None:
        self._topography = value

    @property
    def molecular_system(self):
        if self._topography is None:
            return None
        return self._topography.molecular_system

    @molecular_system.setter
    def molecular_system(self, value) -> None:
        if self._topography is None:
            raise AttributeError("Feature is not associated with any topography")
        self._topography.molecular_system = value

    @property
    def molsys(self):
        if self._topography is None:
            return None
        return self._topography.molsys

    @molsys.setter
    def molsys(self, value) -> None:
        if self._topography is None:
            raise AttributeError("Feature is not associated with any topography")
        self._topography.molsys = value


class _PocketStub(_FeatureStubBase):
    feature_type = "pocket"
    shape_type = "concavity"
    dimensionality = 2

    def __init__(
        self,
        *,
        atom_indices: Iterable[int] | None = None,
        mouth_index: str | None = None,
        index: int | None = None,
        id: int | None = None,
        shape_index: int | None = None,
        shape_id: int | None = None,
        feature_index: int | None = None,
        feature_id: str | None = None,
    ) -> None:
        super().__init__()
        self.atom_indices = list(atom_indices or [])
        self.feature_id = feature_id
        self.feature_index = feature_index
        self.type_index = index
        self.type_id = id
        self.shape_index = shape_index
        self.shape_id = shape_id
        self.boundary_ids: list[str] = []
        self.point_ids: list[str] = []
        if mouth_index is None:
            self.mouth_indices: list[str] = []
            self.n_mouths = 0
        else:
            self.mouth_indices = [mouth_index]
            self.n_mouths = 1
        self.solvent_accessible_area = None
        self.solvent_accessible_volume = None
        self.molecular_surface_area = None
        self.molecular_surface_volume = None
        self.length = None
        self.corner_points_count = None
        self.index = index
        self.id = id


class _MouthStub(_FeatureStubBase):
    feature_type = "mouth"
    shape_type = "boundary"
    dimensionality = 1

    def __init__(
        self,
        *,
        atom_indices: Iterable[int] | None = None,
        index: int | None = None,
        id: int | None = None,
        shape_index: int | None = None,
        shape_id: int | None = None,
        feature_index: int | None = None,
        feature_id: str | None = None,
    ) -> None:
        super().__init__()
        self.atom_indices = list(atom_indices or [])
        self.feature_id = feature_id
        self.feature_index = feature_index
        self.type_index = index
        self.type_id = id
        self.shape_index = shape_index
        self.shape_id = shape_id
        self.boundary_ids: list[str] = []
        self.point_ids: list[str] = []
        self.solvent_accessible_area = None
        self.molecular_surface_area = None
        self.solvent_accessible_length = None
        self.molecular_surface_length = None
        self.n_triangles = None
        self.index = index
        self.id = id


def _build_molecular_system_from_pdb(pdb_path: Path) -> _DummyMolSys:
    atoms: list[_DummyAtom] = []
    with pdb_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.startswith(("ATOM", "HETATM")):
                continue
            atoms.append(
                _DummyAtom(
                    index=len(atoms),
                    atom_id=int(line[6:11]),
                    atom_name=line[12:16].strip(),
                    group_name=line[17:20].strip(),
                    chain_id=line[21].strip(),
                )
            )
    return _DummyMolSys(atoms)


@pytest.fixture
def castp_dataset(tmp_path: Path) -> dict[str, Path]:
    source_dir = Path(__file__).resolve().parents[2] / "sandbox" / "castp" / "1tcd"
    dataset_dir = tmp_path / "castp_1tcd"
    dataset_dir.mkdir()
    files = {}
    for name in ("1tcd.pdb", "1tcd.poc", "1tcd.pocInfo", "1tcd.mouth", "1tcd.mouthInfo"):
        src = source_dir / name
        dst = dataset_dir / name
        shutil.copy(src, dst)
        files[name] = dst
    files["dir"] = dataset_dir
    return files


@pytest.fixture
def patched_load_castp(monkeypatch: pytest.MonkeyPatch):
    module = importlib.import_module("topomt.io.load_CASTp")
    monkeypatch.setattr(module, "Topography", topomt.Topography)
    monkeypatch.setattr(module, "Pocket", _PocketStub)
    monkeypatch.setattr(module, "Mouth", _MouthStub)

    def _fake_convert(path: str | Path, *, to_form: str | None = None):
        assert to_form == "molsysmt.MolSys"
        return _build_molecular_system_from_pdb(Path(path))

    fake_module = SimpleNamespace(convert=_fake_convert)
    def _fake_molsys_converter(system):
        if system is None:
            return None
        if isinstance(system, _DummyMolSys):
            return system
        return _build_molecular_system_from_pdb(Path(system))

    monkeypatch.setattr(topomt.Topography, "default_molsys_converter", _fake_molsys_converter, raising=False)
    monkeypatch.setattr(module.Topography, "default_molsys_converter", _fake_molsys_converter, raising=False)
    monkeypatch.setattr(module, "_import_molsysmt", lambda: fake_module)
    monkeypatch.setattr(module, "msm", fake_module, raising=False)
    return module


def _quantity_value(quantity, unit: str) -> float | None:
    if quantity is None:
        return None
    return float(quantity.to(unit).m)


def _read_pocket_info(info_path: Path) -> dict[int, dict[str, float]]:
    data: dict[int, dict[str, float]] = {}
    with info_path.open(encoding="utf-8") as handle:
        next(handle)
        for line in handle:
            fields = line.split()
            if not fields:
                continue
            pocket_id = int(fields[2])
            data[pocket_id] = {
                "n_mouths": int(fields[3]),
                "area_sa": float(fields[4]),
                "area_ms": float(fields[5]),
                "vol_sa": float(fields[6]),
                "vol_ms": float(fields[7]),
            }
    return data


def _read_mouth_info(info_path: Path) -> dict[int, dict[str, float | list[int]]]:
    data: dict[int, dict[str, float | list[int]]] = {}
    with info_path.open(encoding="utf-8") as handle:
        next(handle)
        for line in handle:
            fields = line.split()
            if not fields:
                continue
            mouth_id = int(fields[2])
            pocket_ids: list[int] = []
            token = fields[3].rstrip(":,")
            if token.isdigit():
                pocket_ids.append(int(token))
            for extra in fields[9:]:
                cleaned = extra.rstrip(",")
                if cleaned.isdigit():
                    pocket_ids.append(int(cleaned))
            data[mouth_id] = {
                "pocket_ids": sorted(set(pocket_ids)),
                "area_sa": float(fields[4]),
                "area_ms": float(fields[5]),
                "len_sa": float(fields[6]),
                "len_ms": float(fields[7]),
                "n_triangles": int(fields[8]),
            }
    return data


def _invert_pocket_mapping(mouth_data: dict[int, dict[str, float | list[int]]]) -> dict[int, list[int]]:
    pocket_to_mouths: dict[int, list[int]] = {}
    for mouth_id, payload in mouth_data.items():
        for pocket_id in payload["pocket_ids"]:  # type: ignore[index]
            pocket_to_mouths.setdefault(pocket_id, []).append(mouth_id)
    for mouths in pocket_to_mouths.values():
        mouths.sort()
    return pocket_to_mouths


def _registered_mouth_ids(topography: topomt.Topography) -> list[int]:
    return sorted(
        int(feature.feature_id.rsplit("-", 1)[-1])
        for feature in topography.of_type("mouth")
    )


def test_load_castp_directory_and_zip(castp_dataset: dict[str, Path], patched_load_castp):
    module = patched_load_castp
    dataset_dir = castp_dataset["dir"]

    zip_path = dataset_dir.parent / "1tcd.zip"
    with ZipFile(zip_path, "w") as archive:
        for name in ("1tcd.pdb", "1tcd.poc", "1tcd.pocInfo", "1tcd.mouth", "1tcd.mouthInfo"):
            archive.write(castp_dataset[name], arcname=castp_dataset[name].name)

    topo_from_dir = module.load_CASTp(dir_path=dataset_dir)
    topo_from_zip = module.load_CASTp(zip_file=zip_path)

    assert len(topo_from_dir.pockets) == 78
    assert len(topo_from_dir.mouths) == 42
    assert len(topo_from_zip.pockets) == 78
    assert len(topo_from_zip.mouths) == 42

    assert topo_from_dir.molecular_system == str(castp_dataset["1tcd.pdb"])
    assert isinstance(topo_from_dir.molsys, _DummyMolSys)
    assert Path(topo_from_zip.molecular_system).name == "1tcd.pdb"
    assert isinstance(topo_from_zip.molsys, _DummyMolSys)

    expected_pockets = _read_pocket_info(castp_dataset["1tcd.pocInfo"])
    expected_mouths = _read_mouth_info(castp_dataset["1tcd.mouthInfo"])
    expected_pocket_to_mouths = _invert_pocket_mapping(expected_mouths)

    for pocket_id in (1, 2, 7, 23, 54, 68):
        feature_id = f"castp-pocket-{pocket_id}"
        pocket_dir = topo_from_dir.get_by_id(feature_id)
        pocket_zip = topo_from_zip.get_by_id(feature_id)
        info = expected_pockets[pocket_id]

        assert pocket_dir.molecular_system == topo_from_dir.molecular_system
        assert pocket_dir.molsys is topo_from_dir.molsys
        assert pocket_zip.molecular_system == topo_from_zip.molecular_system
        assert pocket_zip.molsys is topo_from_zip.molsys

        assert _quantity_value(pocket_dir.solvent_accessible_area, "angstroms**2") == pytest.approx(info["area_sa"])
        assert _quantity_value(pocket_dir.molecular_surface_area, "angstroms**2") == pytest.approx(info["area_ms"])
        assert _quantity_value(pocket_dir.solvent_accessible_volume, "angstroms**3") == pytest.approx(info["vol_sa"])
        assert _quantity_value(pocket_dir.molecular_surface_volume, "angstroms**3") == pytest.approx(info["vol_ms"])

        mouth_ids = expected_pocket_to_mouths.get(pocket_id, [])
        actual_dir = sorted(int(value.rsplit("-", 1)[-1]) for value in pocket_dir.mouth_indices)
        actual_zip = sorted(int(value.rsplit("-", 1)[-1]) for value in pocket_zip.mouth_indices)
        if mouth_ids:
            assert actual_dir == mouth_ids
            assert actual_zip == mouth_ids
            assert pocket_dir.n_mouths == len(mouth_ids)
            assert pocket_zip.n_mouths == len(mouth_ids)
        else:
            assert actual_dir == []
            assert actual_zip == []
            assert pocket_dir.n_mouths == info["n_mouths"]
            assert pocket_zip.n_mouths == info["n_mouths"]
        assert pocket_dir.atom_indices == pocket_zip.atom_indices

    existing_mouth_ids = _registered_mouth_ids(topo_from_dir)
    selection = existing_mouth_ids[:6] + existing_mouth_ids[-4:]
    for mouth_id in selection:
        feature_id = f"castp-mouth-{mouth_id}"
        mouth_dir = topo_from_dir.get_by_id(feature_id)
        mouth_zip = topo_from_zip.get_by_id(feature_id)
        info = expected_mouths[mouth_id]

        assert mouth_dir.molecular_system == topo_from_dir.molecular_system
        assert mouth_dir.molsys is topo_from_dir.molsys
        assert mouth_zip.molecular_system == topo_from_zip.molecular_system
        assert mouth_zip.molsys is topo_from_zip.molsys

        assert _quantity_value(mouth_dir.solvent_accessible_area, "angstroms**2") == pytest.approx(info["area_sa"])
        assert _quantity_value(mouth_dir.molecular_surface_area, "angstroms**2") == pytest.approx(info["area_ms"])
        assert _quantity_value(mouth_dir.solvent_accessible_length, "angstroms") == pytest.approx(info["len_sa"])
        assert _quantity_value(mouth_dir.molecular_surface_length, "angstroms") == pytest.approx(info["len_ms"])
        assert mouth_dir.n_triangles == info["n_triangles"]
        assert mouth_dir.atom_indices == mouth_zip.atom_indices


@pytest.mark.parametrize(
    "argument, description, file_key",
    [
        ("poc_file", "CASTp .poc file", "1tcd.poc"),
        ("mouth_file", "CASTp .mouth file", "1tcd.mouth"),
        ("pocInfo_file", "CASTp .pocInfo file", "1tcd.pocInfo"),
        ("mouthInfo_file", "CASTp .mouthInfo file", "1tcd.mouthInfo"),
        ("pdb_file", "PDB file", "1tcd.pdb"),
    ],
)
def test_load_castp_missing_required_files(
    argument: str,
    description: str,
    file_key: str,
    castp_dataset: dict[str, Path],
    patched_load_castp,
):
    module = patched_load_castp
    missing_path = castp_dataset[file_key]
    missing_path.unlink()

    kwargs = {argument: missing_path}
    if argument != "pdb_file":
        kwargs["molecular_system"] = _build_molecular_system_from_pdb(castp_dataset["1tcd.pdb"])

    with pytest.raises(FileNotFoundError) as excinfo:
        module.load_CASTp(**kwargs)
    assert description in str(excinfo.value)


def test_load_castp_detects_corrupted_marker(castp_dataset: dict[str, Path], patched_load_castp):
    module = patched_load_castp
    poc_path = castp_dataset["1tcd.poc"]
    contents = poc_path.read_text(encoding="utf-8")
    poc_path.write_text(contents.replace(" POC", " BAD", 1), encoding="utf-8")

    with pytest.raises(ValueError) as excinfo:
        module.load_CASTp(dir_path=castp_dataset["dir"])

    assert "Unexpected marker" in str(excinfo.value)
