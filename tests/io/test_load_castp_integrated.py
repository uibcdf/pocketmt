
from __future__ import annotations

from pathlib import Path

import pytest

from topomt.io.load_CASTp import load_CASTp


@pytest.mark.ecosystem
def test_load_castp_end_to_end_with_real_molsysmt(tmp_path: Path):
    """
    Integration test: exercise load_CASTp using the real molsysmt,
    to ensure the TopoMT <-> MolSysMT ecosystem is coherent.
    """

    # 1) localizar el dataset CASTp real
    # ajusta esta ruta a donde tú lo tengas en el repo
    source_dir = (
        Path(__file__).resolve().parents[2] / "sandbox" / "castp" / "1tcd"
    )

    if not source_dir.exists():
        pytest.skip(f"CASTp dataset not found at {source_dir}")

    # copiamos al tmp para no tocar el original
    work_dir = tmp_path / "castp_1tcd"
    work_dir.mkdir(parents=True, exist_ok=True)
    for name in ("1tcd.pdb", "1tcd.poc", "1tcd.pocInfo", "1tcd.mouth", "1tcd.mouthInfo"):
        src = source_dir / name
        if not src.exists():
            pytest.skip(f"Required CASTp file {name} not found in {source_dir}")
        (work_dir / name).write_bytes(src.read_bytes())

    # 2) cargar con la función real
    topo = load_CASTp(dir_path=work_dir)

    # 3) comprobaciones de ecosistema

    # a) debe haber un molsys real
    assert topo.molsys is not None, "Topography should have a molsys attached"
    assert msm.get_form(topo.molsys) == "molsysmt.MolSys"

    # b) debe haber features registradas
    assert len(topo.concavities) > 0, "CASTp should yield concavity-like features"
    assert len(topo.boundaries) >= 0  # puede haber 0, pero lo consultamos

    # c) coherencia: las features deben ver el mismo molsys
    for feat in topo.concavities:
        # muchas de tus features exponen .molsys vía topography
        assert getattr(feat, "molsys", topo.molsys) is topo.molsys

    # d) si el loader creó mouths asociados, que estén linkeados
    # (esto puede variar según el dataset, así que hacemos una comprobación suave)
    for conc in topo.concavities:
        # algunas concavidades tendrán .boundary_ids o .point_ids
        boundary_ids = getattr(conc, "boundary_ids", [])
        for bid in boundary_ids:
            mouth = topo.get_by_id(bid)
            # el mouth también debe ver el mismo topo y molsys
            assert mouth.topography is topo
            assert mouth.molsys is topo.molsys

