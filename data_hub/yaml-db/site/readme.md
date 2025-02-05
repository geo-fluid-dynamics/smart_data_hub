## Design of site YAML files  
This folder summaries geological information on siting regions, with one YAML file dedicated to each region.
An example of the YAML file entries is provided below:

```
# name of the site
name: DE_South_Claystone

description: Synthetic data from Southern Germany.

# lithstratigraphy
Cenozoic-Tertiary:
  properties: default
  lithology: Claystone
  age: Cenozoic
  description: Marlstone, varying calcareous and clayey components.
  geometry: data_hub/yaml-db/geometry/DE_South_Claystone/Tertiary.ply

Mesozoic-Jurassic-Upper-Tithonian:
  properties: data_hub/yaml-db/rock_props/DE_South_Claystone/Tithonian.yml
  lithology: Limestone
  age: Mesozoic
  description: Limestone, marlstone.
  geometry: data_hub/yaml-db/geometry/DE_South_Claystone/Tithonian.ply
```
The entries in this YAML file consist of three main sections: 
1. name: site's name or region's name. 
2. description: additional description of the site or region. 
3. stratigraphy: each stratigraphic layer is named based on [International Commission on Stratigraphy](https://stratigraphy.org/chart),
following the rules of Erathem-System-Series-Stage (or -Regional_level_group).
    * properties: path to the YAML file that contains rock properties of the stratigraphical layer.
      - "default" can be written as a fallback option if no information is available for a specific stratigraphical layer. 
    * lithology: rock type {'Claystone', 'Limestone', 'Sandstone', 'Crystalline', 'Rocksalt'}.
    * age: Erathem.
    * description: additional information on the stratigraphical layer.
    * geometry: path to the PLY files. For more details on generating a PLY file, please refer to the readme.md file in the [`../geometry/readme.md`](../geometry/readme.md).

## Search Approach for Default Values
The missing values are filled based on the `lithology` and `age` entries in each stratigraphical layer. For instance, in the provided example, 
the properties of 'Cenozoic-Tertiary' are referenced as 'default'. In this case, the missing values are retrieved from the file `../rock_props/default/Cenozoic_Claystone.yml`.


