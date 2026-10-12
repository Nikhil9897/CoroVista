# BodyParts3D Asset Attribution & Licensing

## Data Source
The 3D anatomical models in this directory originate from **BodyParts3D**, developed and maintained by **The Database Center for Life Science (DBCLS)**, Japan.

* **Repository**: [BodyParts3D](https://lifesciencedb.jp/bp3d/)
* **License**: [Creative Commons Attribution-ShareAlike 2.1 Japan (CC BY-SA 2.1 JP)](https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en)
* **Ontology Standard**: Foundational Model of Anatomy (FMA)
* **Total Licensed Assets**: 18 source OBJ meshes (Reconstruction version 2.1-cohesive-heart)

## Selected Assets & Attribution Table

| Structure Group | Logical Name | Specific Segment Role | FMA ID | BodyParts3D ID | Source File Prefix |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `vessel_lad` | Left Anterior Descending Artery (LAD) | Proximal segment | FMA74912 | BP51969 | MM420 |
| `vessel_lad` | Left Anterior Descending Artery (LAD) | Mid segment | FMA74912 | BP51969 | MM424 |
| `vessel_lad` | Left Anterior Descending Artery (LAD) | Distal segment | FMA74912 | BP51969 | MM425 |
| `vessel_lcx` | Left Circumflex Artery (LCX) | Proximal segment | FMA74923 | BP51973 | MM426 |
| `vessel_rca` | Right Coronary Artery (RCA) | Mid segment | FMA3802 | BP51977 | MM436 |
| `vessel_rca` | Right Coronary Artery (RCA) | Distal segment | FMA3802 | BP51977 | MM439 |
| `struct_auricles` | Atrial Auricular Appendages | Wall of left auricle | FMA84087 | BP51910 | MM459 |
| `struct_auricles` | Atrial Auricular Appendages | Wall of right auricle proper | FMA84093 | BP51915 | MM461 |
| `struct_myocardium` | Ventricular Myocardium | Free wall of left ventricle | FMA84850 | BP51876 | MM474 |
| `struct_aorta_ascending` | Ascending Aorta Proper | Ascending aorta proper | FMA23733 | BP51985 | MM506 |
| `struct_myocardium` | Ventricular Myocardium | Wall of outflow part of right ventricle | FMA84853 | BP51893 | MM538 |
| `vessel_rca` | Right Coronary Artery (RCA) | Proximal segment | FMA3802 | BP51977 | MM556 |
| `struct_left_main` | Left Main Coronary Artery | Left main trunk | FMA4685 | BP58405 | MM557 |
| `struct_aorta_bulb` | Aortic Bulb (Root) | Wall of bulb of aorta | FMA15098 | BP51975 | MM558 |
| `struct_myocardium` | Ventricular Myocardium | Wall of inflow part of right ventricle | FMA84851 | BP51897 | MM598 |
| `struct_septum` | Muscular Interventricular Septum | Muscular part of interventricular septum | FMA7134 | BP51936 | MM600 |
| `struct_pulmonary_trunk` | Pulmonary Trunk | Pulmonary trunk proper | FMA15086 | BP58392 | MM607 |
| `vessel_lcx` | Left Circumflex Artery (LCX) | Distal segment | FMA74923 | BP51973 | MM635 |

## Transformation and Derivation Notice
* All 18 original meshes remain unmodified in `OBJ Files/`.
* The converted GLB assets strictly preserve the unified BodyParts3D millimeter coordinate space ($X, Y, Z$).
* Fragment cleaning removes disconnected orphan shards (<15 faces) while preserving all authentic anatomical openings and ostia.
* Unified ventricular myocardium (`struct_myocardium`) welds LV free wall (MM474), RV inflow (MM598), and RV outflow (MM538) into a cohesive, rounded organ silhouette with continuous surface normals.
* The published `corovista_heart.glb` master scene combines these 10 semantic groups for unified, efficient WebGL rendering while maintaining discrete sub-mesh nodes for vessel raycasting, hover inspection, and continuous risk color shading.
