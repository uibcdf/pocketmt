
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class Pocket:
    pocket_id: int
    atom_serials: list[int] = field(default_factory=list)
    center: Optional[tuple[float, float, float]] = None
    score: Optional[float] = None
    druggability_score: Optional[float] = None
    volume_mc: Optional[float] = None
    volume_hull: Optional[float] = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class FpocketResult:
    source_pdb: Path
    output_dir: Path
    pockets: list[Pocket] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_pdb": str(self.source_pdb),
            "output_dir": str(self.output_dir),
            "pockets": [
                {
                    "pocket_id": p.pocket_id,
                    "atom_serials": p.atom_serials,
                    "center": p.center,
                    "score": p.score,
                    "druggability_score": p.druggability_score,
                    "volume_mc": p.volume_mc,
                    "volume_hull": p.volume_hull,
                    "raw": p.raw,
                }
                for p in self.pockets
            ],
            "metadata": self.metadata,
        }

