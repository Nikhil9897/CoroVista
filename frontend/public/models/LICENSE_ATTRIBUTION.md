# BodyParts3D Asset Attribution & Licensing

## Data Source
The 3D anatomical models in this directory originate from **BodyParts3D**, developed and maintained by **The Database Center for Life Science (DBCLS)**, Japan.

* **Repository**: [BodyParts3D](https://lifesciencedb.jp/bp3d/)
* **License**: [Creative Commons Attribution-ShareAlike 2.1 Japan (CC BY-SA 2.1 JP)](https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en)
* **Ontology Standard**: Foundational Model of Anatomy (FMA)
* **Total Licensed Assets**: 24 source OBJ meshes

## Selected Assets & Attribution Table

| Structure Group | Logical Name | Specific Segment Role | FMA ID | BodyParts3D ID | Source File Prefix |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `vessel_lad` | Left Anterior Descending Artery (LAD) | Proximal segment | FMA74912 | BP51969 | MM420 |
| `vessel_lad` | Left Anterior Descending Artery (LAD) | Mid segment | FMA74912 | BP51969 | MM424 |
| `vessel_lad` | Left Anterior Descending Artery (LAD) | Distal segment | FMA74912 | BP51969 | MM425 |
| `vessel_lcx` | Left Circumflex Artery (LCX) | Proximal segment | FMA74923 | BP51973 | MM426 |
| `vessel_rca` | Right Coronary Artery (RCA) | Mid segment | FMA3802 | BP51977 | MM436 |
| `vessel_rca` | Right Coronary Artery (RCA) | Distal segment | FMA3802 | BP51977 | MM439 |
| `struct_la_wall` | Left Atrial Wall & Auricle | Lateral wall of left atrium | FMA84083 | BP51906 | MM456 |
| `struct_la_wall` | Left Atrial Wall & Auricle | Wall of left auricle | FMA84087 | BP51910 | MM459 |
| `struct_la_wall` | Left Atrial Wall & Auricle | Superior wall of left atrium | FMA84084 | BP51907 | MM460 |
| `struct_ra_wall` | Right Atrial Wall & Auricle | Wall of right auricle proper | FMA84093 | BP51915 | MM461 |
| `struct_lv_wall` | Left Ventricular Free Wall | Free wall of left ventricle | FMA84850 | BP51876 | MM474 |
| `struct_aorta_ascending` | Ascending Aorta Proper | Ascending aorta proper | FMA23733 | BP51985 | MM506 |
| `struct_rv_wall` | Right Ventricular Wall | Wall of outflow part of right ventricle | FMA84853 | BP51893 | MM538 |
| `vessel_rca` | Right Coronary Artery (RCA) | Proximal segment | FMA3802 | BP51977 | MM556 |
| `struct_left_main` | Left Main Coronary Artery | Left main trunk | FMA4685 | BP58405 | MM557 |
| `struct_aorta_bulb` | Aortic Bulb (Root) | Wall of bulb of aorta | FMA15098 | BP51975 | MM558 |
| `struct_ra_wall` | Right Atrial Wall & Auricle | Anterior wall proper of right atrium | FMA84090 | BP51912 | MM559 |
| `struct_ra_wall` | Right Atrial Wall & Auricle | Lateral wall proper of right atrium | FMA84091 | BP51913 | MM560 |
| `struct_rv_wall` | Right Ventricular Wall | Wall of inflow part of right ventricle | FMA84851 | BP51897 | MM598 |
| `struct_septum` | Muscular Interventricular Septum | Muscular part of interventricular septum | FMA7134 | BP51936 | MM600 |
| `struct_pulmonary_trunk` | Pulmonary Trunk | Pulmonary trunk proper | FMA15086 | BP58392 | MM607 |
| `struct_la_wall` | Left Atrial Wall & Auricle | Anterior wall proper of left atrium | FMA84081 | BP51904 | MM632 |
| `struct_la_wall` | Left Atrial Wall & Auricle | Posterior wall of left atrium | FMA84085 | BP51908 | MM633 |
| `vessel_lcx` | Left Circumflex Artery (LCX) | Distal segment | FMA74923 | BP51973 | MM635 |

## Transformation and Derivation Notice
* All 24 original meshes remain unmodified in `OBJ Files/`.
* The converted GLB assets strictly preserve the unified BodyParts3D millimeter coordinate space ($X, Y, Z$).
* Multi-segment vessel trunks (LAD: MM420/424/425, LCX: MM426/635, RCA: MM556/436/439) and chamber walls (RV: MM598/538, RA: MM559/560/461, LA: MM632/633/456/459/460) were assembled into unified anatomical structures for high-performance WebGL rendering.
* Full Left Ventricular Free Wall (`MM474`) is selected to provide an anatomically complete myocardial envelope from base to apex.
