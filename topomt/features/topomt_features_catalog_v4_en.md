# TopoMT — Feature Catalog

## 2D — `Feature2D` (shape features)

### Concavity — `shape_type = concavity`
| 2D Feature         | Dim | Geometric role                       | Applicable Boundaries (1D)   | Applicable Points (0D) | Biological / Pharmacological Interpretation |
|--------------------|-----|--------------------------------------|------------------------------|-------------------------|--------------------------------------------|
| Cavity             | 2   | General concavity                    | Mouth, Neck, Furrow          | Pit                     | Ligand or peptide binding regions, active/allosteric sites. |
| Pocket             | 2   | Closed concavity                     | Mouth, Neck, Furrow          | Pit                     | Classic drug design target. |
| Void               | 2   | Internal cavity not exposed          | Neck, Furrow                 | Pit                     | Cryptic pockets. |
| Channel            | 2   | Continuous channel                   | Mouth, Neck                  | Pit                     | Ion/molecule transport; gating. |
| BranchedChannel    | 2   | Branched channel                     | Mouth, Neck                  | Pit                     | Multisite selectivity. |
| Groove             | 2   | Open elongated groove                | Mouth, Furrow                | Pit                     | PPI and nucleic acid binding. |
| Cleft              | 2   | Broad groove with opening gradient   | Mouth, Neck, Furrow          | Pit                     | Partial anchoring and functionalization. |

### Convexity — `shape_type = convexity`
| 2D Feature            | Dim | Geometric role                       | Applicable Boundaries (1D) | Applicable Points (0D) | Biological / Pharmacological Interpretation |
|-----------------------|-----|--------------------------------------|----------------------------|-------------------------|--------------------------------------------|
| Vexity                | 2   | General convex surface               | BaseRim, Neck, Ridge       | Apex                    | Shape complementarity in PPI. |
| Protrusion            | 2   | Defined bump                         | BaseRim, Neck, Ridge       | Apex                    | Epitopes / protruding recognition sites. |
| Dome                  | 2   | Hemispherical surface                | BaseRim, Ridge             | Apex                    | Protein–protein interfaces. |
| Spine                 | 2   | Elongated convex crest               | BaseRim, Ridge, Neck       | Apex                    | Anchoring or adhesion. |

### Mixed — `shape_type = mixed`
| 2D Feature        | Dim | Geometric role / topography                | Applicable Boundaries (1D) | Applicable Points (0D) | Biological / Pharmacological Interpretation |
|-------------------|-----|--------------------------------------------|----------------------------|-------------------------|--------------------------------------------|
| Interface         | 2   | Contact zone between structural domains    | Seam                       | —                       | PPI, protein–ligand, protein–membrane interfaces. |
| Patch             | 2   | Flat or irregular patch                    | Seam                       | —                       | Transient docking site. |
| Joint             | 2   | Structural articulation or transition      | Seam                       | —                       | Conformational switches. |

---

## 1D — `Feature1D` (boundaries)

> `shape_type = boundary`. Boundaries are associated to compatible Feature2Ds.

| 1D Boundary | Dim | Applies to 2D shape types     | Geometric role / use |
|-------------|-----|-------------------------------|----------------------|
| Mouth       | 1   | concavity                     | Opening; controls accessibility and selectivity. |
| BaseRim     | 1   | convexity                     | Basal rim of convex features; structural delimitation. |
| Neck        | 1   | concavity, convexity          | Local narrowing; regulates connectivity/flow. |
| Ridge       | 1   | convexity                     | Prominent convex crest or edge. |
| Furrow      | 1   | concavity                     | Bottom line of grooves/clefts; internal axis. |
| Lip         | 1   | concavity, convexity, mixed   | Flexible/dynamic rim (cryptic sites). |
| Seam        | 1   | mixed                         | Line of contact at mixed interfaces. |

---

## 0D — `Feature0D` (points)

> `shape_type = point`. Points are anchored to compatible Feature2Ds.

| 0D Point | Dim | Applies to 2D shape types | Geometric role / use |
|----------|-----|----------------------------|----------------------|
| Pit      | 0   | concavity                  | Deepest point (local minimum) of concavity. |
| Apex     | 0   | convexity                  | Tip (local maximum) of convexity. |

---
