# BodyParts3D Asset Attribution & Licensing

## Data Source
The 3D anatomical models in this directory originate from **BodyParts3D**, developed and maintained by **The Database Center for Life Science (DBCLS)**, Japan.

* **Repository**: [BodyParts3D](https://lifesciencedb.jp/bp3d/)
* **License**: [Creative Commons Attribution-ShareAlike 2.1 Japan (CC BY-SA 2.1 JP)](https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en)
* **Ontology Standard**: Foundational Model of Anatomy (FMA)

## Selected Assets & Attribution Table

| Structure Key | Anatomical Structure | FMA ID | BodyParts3D ID | Source File(s) | Role in CoroVista |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `vessel_lad` | Left anterior descending branch | FMA74912 | BP51969 | MM420, MM424, MM425 | Primary target for LAD stenosis probability visualization |
| `vessel_lcx` | Circumflex branch of LCA | FMA74923 | BP51973 | MM426, MM635 | Primary target for LCX stenosis probability visualization |
| `vessel_rca` | Right coronary artery trunk | FMA3802 | BP51977 | MM556, MM436, MM439 | Primary target for RCA stenosis probability visualization |
| `struct_left_main` | Stem of left coronary artery | FMA4685 | BP58405 | MM557 | Root connecting aortic bulb to LAD/LCX bifurcation |
| `struct_aorta_bulb` | Wall of bulb of aorta | FMA15098 | BP51975 | MM558 | Coronary sinus take-off anchor |
| `struct_aorta_ascending` | Ascending aorta proper | FMA23733 | BP51985 | MM506 | Superior aortic orientation context |
| `struct_lv_wall` | Left ventricle, free wall | FMA84850 | BP51876 | MM631 | Semi-transparent background myocardial silhouette |
| `struct_septum` | Muscular interventricular septum | FMA7134 | BP51936 | MM600 | Septal background myocardial silhouette |
| `struct_pulmonary_trunk` | Pulmonary trunk | FMA15086 | BP58392 | MM607 | Anterior outflow tract context |

## Transformation and Derivation Notice
* All 14 original meshes remain unmodified in `OBJ Files/`.
* The converted GLB assets preserve the exact, unified DICOM/BodyParts3D coordinate space and millimeter scale.
* Sub-segments of vessel trunks (MM420/424/425, MM426/635, MM556/436/439) were combined into continuous vascular meshes for unified shader rendering.
