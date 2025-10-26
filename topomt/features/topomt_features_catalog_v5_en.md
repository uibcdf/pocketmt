# 🧭 TopoMT — Feature Catalog (v5, by Dimensionality)

This catalog defines the **complete set of topographic features** used in TopoMT, structured by dimensionality:  
- **2D features**: shape patches (concavity, convexity, interface).  
- **1D features**: boundaries associated to 2D features.  
- **0D features**: points associated to 2D and/or 1D features.  

All features are **energy-agnostic** and purely geometric. Future energetic or dynamic annotations should live in separate layers.

---

## 2D — `Feature2D` (shape features)

### 🌀 Concavity — `shape_type = concavity`

| 2D Feature        | Dim | Geometric role                                          | Applicable Boundaries (1D)                     | Applicable Points (0D)                      | Typical Biological / Pharmacological Use |
|-------------------|-----|---------------------------------------------------------|------------------------------------------------|--------------------------------------------|------------------------------------------|
| Cavity            | 2   | General concavity                                       | Mouth, Neck, Furrow, Funnel, EdgeLoop          | Pit, Nadir                                | Ligand or peptide binding sites; active or allosteric pockets. |
| Pocket            | 2   | Closed concavity                                       | Mouth, Neck, Furrow, EdgeLoop                  | Pit, Nadir                                | Classic drug design target. |
| Void              | 2   | Internal concavity (cryptic)                            | Neck, Furrow                                   | Pit, Nadir                                | Cryptic pocket, buried binding site. |
| Channel           | 2   | Continuous channel                                     | Mouth, Neck, BranchLine                        | Pit, Bifurcation                           | Ion/molecule transport, gating. |
| BranchedChannel   | 2   | Channel with multiple branches                         | Mouth, Neck, BranchLine                        | Pit, Bifurcation                           | Multisite or pathway selectivity. |
| Groove            | 2   | Open elongated groove                                  | Mouth, Furrow                                  | Pit                                       | PPI, DNA/RNA interaction. |
| Cleft             | 2   | Broad groove with opening gradient                     | Mouth, Neck, Furrow                             | Pit                                       | Partial anchoring, flexible functionalization. |
| Funnel            | 2   | Conical or narrowing entrance                          | Mouth, Neck, EdgeLoop                           | Pit                                       | Geometric gating, access modulation. |
| Vestibule         | 2   | Pre-chamber near mouth of a pocket/channel             | Mouth, Neck                                    | Pit                                       | Selectivity filter. |
| Ampulla           | 2   | Bulbous widening along a channel                       | Neck, BranchLine                               | Pit, Bifurcation                           | Stepwise occupancy, transport checkpoints. |
| Niche / Alcove    | 2   | Lateral shallow recess                                | Neck, Furrow                                   | Pit                                       | Anchoring sites for fragments or water networks. |

---

### 🌿 Convexity — `shape_type = convexity`

| 2D Feature     | Dim | Geometric role                            | Applicable Boundaries (1D)         | Applicable Points (0D)           | Typical Biological / Pharmacological Use |
|----------------|-----|--------------------------------------------|------------------------------------|-----------------------------------|------------------------------------------|
| Vexity         | 2   | General convex patch                       | BaseRim, Neck, Ridge, Buttress     | Apex                             | Complementarity in PPI. |
| Protrusion     | 2   | Defined bump                               | BaseRim, Neck, Ridge               | Apex                             | Epitopes, surface hotspots. |
| Dome           | 2   | Hemispherical convexity                    | BaseRim, Ridge                     | Apex                             | Protein-protein interfaces. |
| Spine          | 2   | Elongated convex crest                     | BaseRim, Ridge, Neck               | Apex                             | Anchoring or adhesion. |
| Knob / Boss    | 2   | Small rounded bump                         | BaseRim, Ridge                     | Apex                             | Local contact enhancement. |
| Buttress       | 2   | Flared base of a protrusion or dome        | BaseRim, Ridge                     | Apex                             | Structural support, shape modulation. |
| Pinnacle       | 2   | Narrow tall convexity                      | BaseRim, Ridge                     | Apex                             | Salient epitopes, targeted recognition. |

---

### 🪨 Interface — `shape_type = mixed`

| 2D Feature   | Dim | Geometric role / topology                         | Applicable Boundaries (1D) | Applicable Points (0D) | Typical Biological / Pharmacological Use |
|--------------|-----|----------------------------------------------------|----------------------------|-------------------------|------------------------------------------|
| Interface    | 2   | Contact zone between structural domains           | Seam, Isthmus, HingeLine   | —                       | PPI, protein-ligand, protein-membrane interfaces. |
| Patch        | 2   | Flat or irregular patch                           | Seam, HingeLine            | —                       | Transient docking, dynamic surfaces. |
| Joint        | 2   | Structural articulation or transition zone        | Seam                       | —                       | Conformational switches. |
| Saddle       | 2   | Patch with negative Gaussian curvature            | Seam, HingeLine            | SaddlePoint             | Mechanical leverage zone, hinge geometry. |
| Trench       | 2   | Long shallow depression across interface          | Seam                       | SaddlePoint             | Guiding grooves at contact regions. |

---

## 1D — `Feature1D` (boundaries)

| 1D Boundary  | Dim | Applies to shape types | Geometric role / topology                                  | Typical Biological / Pharmacological Use |
|--------------|-----|-------------------------|-----------------------------------------------------------|------------------------------------------|
| Mouth        | 1   | concavity               | Opening of a cavity                                       | Gating, accessibility, selectivity. |
| BaseRim      | 1   | convexity               | Basal rim of convex features                              | Structural support. |
| Neck         | 1   | concavity, convexity    | Narrowing transition                                     | Flow regulation, selectivity. |
| Ridge        | 1   | convexity               | Convex crest boundary                                    | Anchoring line. |
| Furrow       | 1   | concavity               | Internal axis line in grooves/clefts                      | Pharmacophore scaffolding. |
| Lip          | 1   | concavity, convexity, mixed | Flexible/dynamic boundary                             | Cryptic site modeling. |
| Seam         | 1   | mixed                   | Contact boundary between interface patches               | Interface articulation. |
| Isthmus      | 1   | mixed, concavity, convexity | Bridge connecting two patches                        | Bivalent ligand bridging, pathway connection. |
| EdgeLoop     | 1   | concavity               | Closed boundary loop                                    | Loop perimeter analysis. |
| BranchLine   | 1   | concavity, mixed        | Line terminating at bifurcation                          | Channel branching. |
| HingeLine    | 1   | mixed                   | Curve concentrating relative motion                      | Hinge and lever geometry. |

---

## 0D — `Feature0D` (points)

| 0D Point     | Dim | Applies to shape types         | Geometric role                                | Typical Biological / Pharmacological Use |
|--------------|-----|-------------------------------|-----------------------------------------------|------------------------------------------|
| Pit          | 0   | concavity                     | Local minimum of concavity                    | Hotspot candidate, anchor site. |
| Nadir        | 0   | concavity                     | Global minimum of a concavity                 | Key anchoring site. |
| Apex         | 0   | convexity                     | Local maximum of convexity                    | Epitope candidate. |
| Bifurcation  | 0   | concavity, mixed              | Junction point of branching pathways         | Transport path topology. |
| SaddlePoint  | 0   | mixed                         | Point of zero mean curvature in saddle patch | Mechanical leverage point. |
| RidgeTip     | 0   | convexity                     | Tip along a ridge                            | Protrusive epitope geometry. |

---

## 🔐 General Notes

- These features are **purely geometric** — no energy, force, or dynamics is encoded in this catalog.  
- **Interface** remains the canonical name for `shape_type = mixed` features.  
- Some boundaries and points may have **multiple parent 2D features** (e.g., `Seam`, `Isthmus`, `Bifurcation`).  
- Boundaries can be **open or closed** (e.g., `Mouth` vs `EdgeLoop`).  
- 0D features are critical points of the surface or boundary graph.  
- This catalog, combined with the **attributes catalog**, forms the core ontology of the TopoMT topographic model.

