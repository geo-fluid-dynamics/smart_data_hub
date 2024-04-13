## Design of site YAML files  
This folder collects geological information on reference sites, with one YAML file dedicated to each reference site.
An example of the YAML file entries is provided below:

```
# name of the site
name: synthetic site A

# Location
location:
  type: coordinate
  value: {'N': 47.3643,
          'E': 7.1543}

# lithstratigraphy and its properties

Middle_Jurassic-Aalenian-OpalinusClay-sandy_facies1:
  properties: ../../../yaml-db/lithostratigraphy/synthetic_site_A/sandy_facies.yml
Middle_Jurassic-Aalenian-OpalinusClay-shaly_facies2:
  properties: ../../../yaml-db/lithostratigraphy/synthetic_site_A/shaly_facies.yml
Middle_Jurassic-Aalenian-OpalinusClay-sandy_facies2:
  properties: ../../../yaml-db/lithostratigraphy/synthetic_site_A/sandy_facies.yml
Middle_Jurassic-Aalenian-PasswangFormation:
  properties: default
Middle_Jurassic-Bajocian-PasswangFormation:
  properties: default

# geometry data for creating 3D geological structural model
geometry:
  geological_model_points: ../../../yaml-db/geometry/default/points.csv
  geological_model_orientations: ../../../yaml-db/geometry/default/orientations.csv
```
The entries in this YAML file consist of three sections: the site's name, lithostratigraphy, and geometry. In the 
lithostratigraphy section, each lithostratigraphic layer is named based on the [Stratigraphic Table from Germany Compact 
2022](https://www.stratigraphie.de/ergebnisse/), following the rules of Period-Epoch-Stage-Lithostratigraphy-Regional_level_group.
Each lithostratigraphy is linked to a YAML file, with the path specified inside the 'properties' field. A "default" can 
be written as a fallback option if no information is available for a specific lithostratigraphy. 

### Hierarchical Search Approach for Default Values
The filenames of the YAML files are structured to facilitate searching for defaults based on a hierarchical approach.  

For instance, in the provided example, the lithostratigraphy 'Middle_Jurassic-Aalenian-PasswangFormation' is referred to 
as 'default'. In this case, the search process begins by checking if a default folder with the same locality name, 
'synthetic site A' in 'lithostratigraphy/default' exists. If not found, the search extends to look for a YAML file named "PasswangFormation", and 
if that is not found either, the search progresses to find a file named "Aalenian", and so forth. Similarly, if there is 
a default folder named "synthetic site A", we search for it in the same hierarchical way.

This naming convention makes it easier to search for defaults and systematically organize the files, ensuring comprehensive 
coverage even without specific data for each lithostratigraphy.

