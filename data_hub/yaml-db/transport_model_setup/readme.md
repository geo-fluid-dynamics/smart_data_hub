##  Compute Scenario for Nuclide Transport Modelling
This folder is intended to assemble all the input data required for running nuclide transport simulations. To simplify 
this process, the user needs to provide information about the site, including its name and modelling area, the type of 
fluid present in the modelling area, the nuclides that need to be considered in the simulation, and the chosen forward 
solver. Presently, an example of OpenGeoSys is available. The entries of the YAML file for this purpose are illustrated below:
```
site:
  site_name: # path_to_site
  modelling_areas: # list of string 

fluid:
  type: # list of string
  fluid_properties: # path_to_fluid

nuclide:
  nuclides_properties: # path_to_nuclide
  first_nuclide: # string
  include_nuclides: # list of string
  
solver:
  ogs_solver:
    simulation_setup: # path to solver
  analytical_solution:
    simulation_setup:  # path to solver
```
