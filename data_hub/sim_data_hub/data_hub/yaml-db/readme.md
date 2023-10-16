# yaml-db
This document explains the structure of folders and files in the yaml-db

## Directories / Folders
Each folder represents one map body, for example, Earth, Europa, and Mars or claystone, salt and crystalline. There is 
only one exception, which is the folder "_default". This folder contains the default material properties that can be 
used when there is no value for a certain parameter at a specific location.

No subfolders are supported.

## Files
For each planetary body, i.e. each folder, there can be any number of different yaml-files that are associated with a 
certain location. There can be several files with the same location (e.g., repeated measurements in different years), 
but there cannot be several locations within one file.
The names of the files should contain the location of the dataset.

The files should contain a field "name", that gives the name similar to the filename, a field "description", that gives 
details on the dataset, a location and other fields that depend on the dataset itself.

A field other than name and description has the following structure (it must contain type, value, unit and unit_str; it 
should contain source; other subfields can be omitted):

```
field:
  type: STR                         # String out of [ scalar, array, tabulated, expression, coordinate, string ].
  value: VAL                        # A value of type float, integer, string, array or dictionary.
  dev_pdf: STR                      # Gauss or other parametrized or tabulated PDF.
  dev_value: VAL                    # Hyperparameters of PDF or array with same type as value.
  unit_str: STR                     # Standard string to inidate unit.
  unit: [ 0 0 0 0 0 0 0 ]           # An array of the form [ kg m s K A mol cd ] that gives the unit as the exponent of  
                                    # The SI basis units, e.g., m/s^2 is [ 0 1 -2 0 0 0 0 ].
  variable: STR                     # Function argument (e.g., temperature) (must be used if type is tabulated or 
                                    # expression).
  variable_unit: [ 0 0 0 0 0 0 0 ]  # See above (must be used if type is tabulated or expression).
  variable_unit_str: STR            # Standard string to indicate variable_unit.
  source: STR                       # String with BibTeX key of data source. Free format should not be used here.
  meta_sys: STR                     # Meta data from systematic databases, e.g. NASA database.
  meta_free: STR                    # Free text meta data.
```

## Fields

The different fields should have the the structure (PROPERTY)_(OBJECT), or only (PROPERTY) if the property is 
independent of any object (e.g., material or interface). Examples are density_ice or gravitational_acceleration.
Special fields are _name_, _description_, and _figures_, which are used to provide additional information for the 
dataset. 
The following list an example of all properties and objects known to the Ice, yet.

| Property                   | Object   |
|----------------------------|----------|
| accumulation               | air      |
| attenuation_length         | base     |
| bulk_modulus               | brine    |
| bulk_modulus_drained       | firn     |
| density                    | ice      |
| depth                      | seawater |
| dynamic_viscosity          | snow     |
| elevation                  | surface  |
| geothermal_heat_flux       | water    |
| gravitational_acceleration |          |
| latent_heat_melting        |          |
| latent_heat_sublimation    |          |
| location                   |          |
| mass                       |          |
| melt_rate                  |          |
| melting_temperature        |          |
| porosity                   |          |
| permeability               |          |
| Q_P                        |          |
| Q_S                        |          |
| salt_concentration         |          |
| saturation                 |          |
| shear_modulus              |          |
| specific_heat_capacity     |          |
| surface_depth              |          |
| temperature                |          |
| thermal_conductivity       |          |
| thermal_diffusivity        |          |
| thermal_expansivity        |          |
| thickness                  |          |
| velocity_P                 |          |
| velocity_S                 |          |
| youngs_modulus             |          |

## sources.bib
The file sources.bib contains BibTeX entries for all sources that are mentioned in the yaml-db.