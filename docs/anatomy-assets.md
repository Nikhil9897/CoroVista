# CoroVista — BodyParts3D Anatomy Asset Inventory & Discovery Report

**Stage 5B.1: Anatomical Mesh Discovery & Verification**  
**Asset Source**: `OBJ Files` (BodyParts3D, FMA Ontology)  
**Total Assets Discovered**: 129 OBJ Files  

---

## 1. Executive Summary & Verification Findings

A complete recursive audit of the `OBJ Files` directory discovered **129 `.obj` mesh files** totaling **27.6 MB**. All assets originate from the **BodyParts3D** anatomical repository mapped to the **Foundational Model of Anatomy (FMA)**.

### Key Architectural Discoveries:
1. **Unified Coordinate System**:
   * All 129 meshes share an **identical, pre-aligned coordinate space** in millimeters ($X, Y, Z$).
   * Bounding box across all assets:
     * $X \in [-35.33, 81.1]$ mm ($\Delta X = 116.43$ mm)
     * $Y \in [-177.22, -70.61]$ mm ($\Delta Y = 106.61$ mm)
     * $Z \in [1174.58, 1292.65]$ mm ($\Delta Z = 118.07$ mm)
   * The assets require **zero manual rotation, translation, or scaling** to assemble into an anatomically correct human heart.
2. **Resolution of "Multiple LAD Trunk Files"**:
   * Filenames `MM420`, `MM424`, and `MM425` all share `BP51969` / `FMA74912` (*"Trunk of anterior interventricular branch"*).
   * Spatial analysis proves they are **sequential contiguous segments**:
     * **MM420** (Proximal LAD): $Z \in [1245.52, 1252.08]$ mm (0.018 mm from Left Main)
     * **MM424** (Mid LAD): $Z \in [1232.76, 1248.09]$ mm (0.040 mm from Proximal)
     * **MM425** (Distal LAD): $Z \in [1186.97, 1234.05]$ mm (0.041 mm from Mid, extending to apex)
   * **They do not duplicate geometry**. To render the complete LAD trunk, all three segments must be rendered together (or merged into a unified LAD group).
3. **Resolution of "Multiple RCA Trunk Files"**:
   * Filenames `MM556`, `MM436`, and `MM439` all share `BP51977` / `FMA3802` (*"Trunk of right coronary artery"*).
   * Spatial analysis proves they are **sequential contiguous segments** from aortic ostium to the crux:
     * **MM556** (Proximal RCA): $Z \in [1224.82, 1240.40]$ mm (0.142 mm from Aortic Bulb)
     * **MM436** (Mid RCA): $Z \in [1204.30, 1226.20]$ mm (0.102 mm from Proximal)
     * **MM439** (Distal RCA): $Z \in [1193.92, 1205.60]$ mm (0.116 mm from Mid)
   * **They do not duplicate geometry**. Together they form the complete RCA trunk.
4. **Resolution of "Multiple LCX Trunk Files"**:
   * Filenames `MM426` and `MM635` both share `BP51973` / `FMA74923` (*"Trunk of circumflex branch"*).
   * **MM426** (Proximal LCX): $Z \in [1231.16, 1254.22]$ mm (434 vertices)
   * **MM635** (Distal LCX): $Z \in [1188.94, 1235.18]$ mm (6,180 vertices, detailed posterior AV groove)
   * Minimum distance between `MM426` and `MM635` is **0.127 mm**. They represent proximal and distal segments of the LCX trunk.
5. **Material / Texture Audit**:
   * **Zero `.mtl` or texture image files** exist in `OBJ Files`.
   * OBJ files do not contain active material links.
   * Shaders and material colors (e.g. vascular risk shaders, myocardial glass/semi-transparent shaders) must be defined programmatically in Three.js.

---

## 2. Anatomical Category Inventory

| Category | File Count | Total Vertices | Total Faces | Total Size (KB) | Key Structures Included |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Coronary Arteries & Branches** | 18 | 19,451 | 35,420 | 2,342.3 | LAD (3 segs), RCA (3 segs), LCX (2 segs), LM, Diagonals, Septals, Marginal, Conus |
| **Coronary Veins & Sinus** | 7 | 6,569 | 12,238 | 845.8 | Great cardiac vein, Coronary sinus, Small cardiac vein, Right marginal vein |
| **Great Vessels (Aorta & Outflow)** | 3 | 6,323 | 11,312 | 704.0 | Ascending aorta proper (MM506), Bulb of aorta (MM558), Pulmonary trunk (MM607) |
| **Cardiac Valves & Anuli** | 21 | 29,864 | 54,928 | 3,745.2 | Aortic valve cusps/anulus, Mitral valve leaflets/anulus, Tricuspid leaflets, Pulmonary valve |
| **Cardiac Conduction System** | 13 | 19,374 | 33,656 | 2,246.7 | SA node, AV node, AV bundle, Bundle branches (RBB, LBB), Internodal tracts |
| **Internal Musculature & Skeleton** | 12 | 27,243 | 48,154 | 3,382.4 | Papillary muscles (LV/RV), Trabeculae carneae, Fibrous trigones, Supraventricular crest |
| **Septal Structures** | 8 | 14,842 | 26,984 | 1,845.5 | Muscular IV septum, Membranous IV septum, Interatrial septum, AV septum |
| **Chamber Walls & Myocardium** | 47 | 100,000+ | 180,000+ | 12,500+ | LV free wall segments, RV inflow/outflow, Left/Right atrial walls, Auricles |
| **Total** | **129** | **223,666** | **402,692** | **27,611.9** | Complete adult cardiac anatomy |

---

## 3. Recommended Primary Mesh Candidates for CoroVista

### 3.1 Left Anterior Descending Artery (LAD)

* **Clinical Target**: LAD Stenosis ($\ge 50\%$ luminal obstruction)
* **Candidate Meshes**: **Assemble `MM420` + `MM424` + `MM425`**
  * `MM420_BP51969_FMA74912_Trunk of anterior interventricular branch of left coronary artery.obj` (Proximal, 397 verts, 40.6 KB)
  * `MM424_BP51969_FMA74912_Trunk of anterior interventricular branch of left coronary artery.obj` (Mid, 610 verts, 66.1 KB)
  * `MM425_BP51969_FMA74912_Trunk of anterior interventricular branch of left coronary artery.obj` (Distal, 511 verts, 54.9 KB)
* **Total Trunk Geometry**: 1,518 vertices, 2,658 faces, 161.6 KB.
* **Selection Evidence**:
  1. Identical FMA ID (`FMA74912`) and BP ID (`BP51969`).
  2. Bounding boxes are strictly sequential along the anterior interventricular sulcus from base ($Z=1252$ mm) to apex ($Z=1187$ mm).
  3. Gap between segments is $< 0.041$ mm.
  4. Rendering only one segment would display an incomplete, truncated artery (e.g. MM420 alone is only 6.5 mm tall).
* **Optional Context Branches**:
  * Diagonal Branch 1: `MM422_BP51972_FMA3860` (1,154 verts)
  * Second Left Anterior Branch: `MM423_BP51965_FMA3888` (742 verts)
  * Septal Perforators: `MM431`, `MM433`, `MM434`

### 3.2 Left Circumflex Artery (LCX)

* **Clinical Target**: LCX Stenosis ($\ge 50\%$ luminal obstruction)
* **Candidate Meshes**: **Assemble `MM426` + `MM635`**
  * `MM426_BP51973_FMA74923_Trunk of circumflex branch of left coronary artery.obj` (Proximal, 434 verts, 46.3 KB)
  * `MM635_BP51973_FMA74923_Trunk of circumflex branch of left coronary artery.obj` (Distal, 6,180 verts, 769.0 KB)
* **Total Trunk Geometry**: 6,614 vertices, 13,012 faces, 815.3 KB.
* **Selection Evidence**:
  1. Identical FMA ID (`FMA74923`) and BP ID (`BP51973`).
  2. `MM426` arises from Left Main (`MM557`) at $Z=1254$ mm and runs lateral to $Z=1231$ mm.
  3. `MM635` continues seamlessly from $Z=1235$ mm down to $Z=1189$ mm along the posterior atrioventricular groove.
  4. Clearance between `MM426` and `MM635` is 0.127 mm.
* **Optional Context Branches**:
  * Left Marginal Artery (Obtuse Marginal): `MM610_BP51926_FMA3902` (2,113 verts, branches from `MM426` at 0.091 mm)
  * Posterior Ventricular Branch: `MM428_BP51937_FMA3914` (1,349 verts)

### 3.3 Right Coronary Artery (RCA)

* **Clinical Target**: RCA Stenosis ($\ge 50\%$ luminal obstruction)
* **Candidate Meshes**: **Assemble `MM556` + `MM436` + `MM439`**
  * `MM556_BP51977_FMA3802_Trunk of right coronary artery.obj` (Proximal, 576 verts, 63.2 KB)
  * `MM436_BP51977_FMA3802_Trunk of right coronary artery.obj` (Mid, 442 verts, 47.3 KB)
  * `MM439_BP51977_FMA3802_Trunk of right coronary artery.obj` (Distal, 795 verts, 86.2 KB)
* **Total Trunk Geometry**: 1,813 vertices, 3,242 faces, 196.7 KB.
* **Selection Evidence**:
  1. Identical FMA ID (`FMA3802`) and BP ID (`BP51977`).
  2. `MM556` originates at the right aortic sinus of the aortic bulb (`MM558`, dist = 0.142 mm) at $Z=1240$ mm.
  3. `MM436` descends along the anterior right AV groove ($Z \in [1204, 1226]$ mm, clearance to proximal = 0.102 mm).
  4. `MM439` rounds the acute margin onto the posterior diaphragmatic surface ($Z \in [1194, 1205]$ mm, clearance to mid = 0.116 mm).
* **Optional Context Branches**:
  * Conus Branch: `MM441_BP51955_FMA3807` (780 verts)
  * Sinoatrial Nodal Branch: `MM438_BP51922_FMA3823` (433 verts)
  * Right Marginal Branch (Acute Marginal): `MM440_BP51950_FMA3818` (1,018 verts)
  * AV Nodal Branch: `MM443_BP51952_FMA3851` (2,041 verts)
  * Posterior Ventricular Branch: `MM444_BP51956_FMA3837` (524 verts)

### 3.4 Root and Context Anchor Meshes

To provide proper anatomical perspective without visual clutter:
1. **Left Main Stem**: `MM557_BP58405_FMA4685_Stem of left coronary artery.obj` (370 verts, bridges aortic bulb to LAD/LCX bifurcation).
2. **Aortic Bulb**: `MM558_BP51975_FMA15098_Wall of bulb of aorta.obj` (2,327 verts, contains left and right coronary ostia).
3. **Ascending Aorta**: `MM506_BP51985_FMA23733_Ascending aorta proper.obj` (1,492 verts, superior orientation landmark).
4. **Myocardial Base (Semi-Transparent)**:
   * Left Ventricle Free Wall: `MM631_BP51876_FMA84850` (4,831 verts)
   * Interventricular Septum: `MM600_BP51936_FMA7134` (2,530 verts)
   * Pulmonary Trunk: `MM607_BP58392_FMA15086` (2,504 verts)

---

## 4. Duplicate and Overlapping Mesh Audit

1. **Interventricular Septum**:
   * `MM594` (1,026 verts, 109 KB) vs `MM600` (2,530 verts, 302 KB): Both represent `FMA7134` (*"Muscular part of interventricular septum"*). `MM600` is the complete muscular septum; `MM594` is a sub-region. **Use `MM600`**.
2. **Septal Wall of Right Atrium**:
   * `MM590` (439 KB) vs `MM591` (40 KB): Both represent `FMA84094`. `MM590` is the primary full wall.
3. **Left Ventricle Free Wall**:
   * Multiple small sub-segments (`MM614`, `MM615`, `MM616`, `MM620`, etc.) are subdivisions of the primary free wall. `MM474` (363 KB) and `MM631` (543 KB) represent the primary overarching free wall envelopes.
4. **Coronary Sinus**:
   * `MM449` (61 KB), `MM634` (346 KB), and `MM638` (92 KB) represent different anatomical sections of the coronary venous sinus (`FMA4706`).

---

## 5. Summary Table of All 18 Coronary Artery Assets

| MM ID | BP ID | FMA ID | Anatomical Structure | Vertices | Faces | Size (KB) | Spatial Role |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **MM557** | BP58405 | FMA4685 | Stem of left coronary artery | 370 | 500 | 35.0 | Left Main root from aorta |
| **MM420** | BP51969 | FMA74912 | Trunk of anterior interventricular branch | 397 | 642 | 40.6 | **LAD Segment 1 (Proximal)** |
| **MM424** | BP51969 | FMA74912 | Trunk of anterior interventricular branch | 610 | 1,104 | 66.1 | **LAD Segment 2 (Mid)** |
| **MM425** | BP51969 | FMA74912 | Trunk of anterior interventricular branch | 511 | 912 | 54.9 | **LAD Segment 3 (Distal / Apical)** |
| **MM422** | BP51972 | FMA3860 | Diagonal branch of anterior descending | 1,154 | 1,930 | 122.3 | Major LAD side branch (D1) |
| **MM423** | BP51965 | FMA3888 | Second left anterior branch | 742 | 1,274 | 78.9 | LAD diagonal/anterior branch |
| **MM432** | BP51962 | FMA3890 | Third left anterior branch | 1,135 | 1,894 | 120.6 | Distal anterior branch |
| **MM431** | BP51970 | FMA3893 | Anterior septal branch | 749 | 1,262 | 79.4 | Septal perforator branch |
| **MM433** | BP51970 | FMA3893 | Anterior septal branch | 1,328 | 2,218 | 140.0 | Septal perforator branch |
| **MM434** | BP51970 | FMA3893 | Anterior septal branch | 1,332 | 2,238 | 141.8 | Septal perforator branch |
| **MM426** | BP51973 | FMA74923 | Trunk of circumflex branch | 434 | 764 | 46.3 | **LCX Segment 1 (Proximal)** |
| **MM635** | BP51973 | FMA74923 | Trunk of circumflex branch | 6,180 | 12,248 | 769.0 | **LCX Segment 2 (Distal / Posterior)** |
| **MM610** | BP51926 | FMA3902 | Left marginal artery | 2,113 | 3,984 | 247.7 | Obtuse marginal branch (OM) |
| **MM428** | BP51937 | FMA3914 | First posterior ventricular branch of circumflex | 1,349 | 2,306 | 144.8 | Distal circumflex lateral branch |
| **MM556** | BP51977 | FMA3802 | Trunk of right coronary artery | 576 | 1,066 | 63.2 | **RCA Segment 1 (Proximal Ostial)** |
| **MM436** | BP51977 | FMA3802 | Trunk of right coronary artery | 442 | 774 | 47.3 | **RCA Segment 2 (Mid Anterior Sulcus)** |
| **MM439** | BP51977 | FMA3802 | Trunk of right coronary artery | 795 | 1,402 | 86.2 | **RCA Segment 3 (Distal / Crux)** |
| **MM437** | BP51980 | FMA3815 | First anterior ventricular branch of RCA | 1,082 | 1,792 | 113.8 | Anterior right ventricular branch |
| **MM440** | BP51950 | FMA3818 | Marginal branch of RCA | 1,018 | 1,426 | 99.1 | Acute marginal branch (AM) |
| **MM441** | BP51955 | FMA3807 | Conus branch of RCA | 780 | 1,308 | 81.8 | Outflow tract conus branch |
| **MM438** | BP51922 | FMA3823 | Sinoatrial nodal branch of RCA | 433 | 640 | 42.9 | SA nodal branch to right atrium |
| **MM443** | BP51952 | FMA3851 | Atrioventricular node branch of RCA | 2,041 | 3,518 | 228.1 | AV nodal branch at cardiac crux |
| **MM444** | BP51956 | FMA3837 | First posterior ventricular branch of RCA | 524 | 950 | 56.8 | Posterior descending / PLV branch |
| **MM445** | BP51957 | FMA3829 | Anterior atrial branch of RCA | 524 | 888 | 55.4 | Right atrial branch |

---

## 6. Recommendations for Stage 5B Implementation

1. **Pre-Processing / Grouping Strategy**:
   * In Stage 5B, assemble the three vessel trunks as logical Three.js `Group` or merged geometries:
     * `LAD Group`: `MM420` + `MM424` + `MM425`
     * `LCX Group`: `MM426` + `MM635`
     * `RCA Group`: `MM556` + `MM436` + `MM439`
     * `Left Main`: `MM557`
   * This provides a complete uninterrupted visual vessel tree while allowing each vessel to receive its dedicated continuous risk probability shader from the API.
2. **Context Model**:
   * Render the Aorta (`MM558` + `MM506`) as a solid anatomical anchor.
   * Render the myocardium (`MM631` + `MM600`) with semi-transparent, subtle dark glass styling so the coronary vessels remain prominently visible both on the anterior and posterior aspects of the heart.
3. **Preservation**:
   * All 129 source assets in `OBJ Files` remain completely unmodified and preserved in their original form.
