# Smart Data Hub
Welcome to the smart data hub repository, developed by the [Methods for Model-based Development in Computational Engineering](https://www.mbd.rwth-aachen.de/) (MBD) and 
[Geophysical Imaging and Monitoring](https://www.gim.rwth-aachen.de/) (GIM) groups at RWTH Aachen University. The smart 
data hub is a product of the '[Smart-Monitoring](https://www.mbd.rwth-aachen.de/go/id/sxklc?lidx=1#aaaaaaaaaasxkoh)' project,
which aims to provide innovative solutions in data-integrated simulation studies: scenario-based, uncertainty-integrated database.

The smart data hub offers a direct interface to the analysis and simulation of specific repository sites. Our approach 
ensures the reproducibility and transparency of our results, while it is also feasible to apply the method to other 
research areas, such as the [ice data hub](https://doi.org/10.23689/fidgeo-5735).

## Installation
This repository contains a submodule [sim_data_hub](https://github.com/geo-fluid-dynamics/sim_data_hub.git).  If you 
want to clone the project with a submodule, follow the steps below:
1. Clone the current repository:
   ```
    git clone https://github.com/geo-fluid-dynamics/smart_data_hub.git
   ```
2. Navigate to the `data_hub` directory by running `cd data_hub`.
3. clone the submodule:
   ```
    git clone --recurse-submodules https://github.com/geo-fluid-dynamics/sim_data_hub.git
   ```
If you are only interested in the [scenario-base database](./README.md#data-hub-architecture), you don't need to use the `sim_data_hub`.

## Data Hub Architecture
The data hub is designed to serve two different use cases:
1. **Scenario-based Database**: The data is stored in YAML format, managed and constructed using the [yaml-db](data_hub/yaml-db/readme.md) module.
All relevant files for this use case can be found in the `data_hub/yaml-db` directory.
2. **Data Visualization**: Data is visualized through a Graphical User Interface (GUI), which supports data import, export, 
and visualization. The basic features can be found in the [GUI_for_data_hubs]() repository (which will be made public soon). 
Files associated with this use case are located in the following directories:
   * `assets`
   * `data_hub/export`
   * `data_hub/library`
   * `data_hub/sim_data_hub`
   * `config_gui.yml`

Please refer to the [documentation](https://github.com/geo-fluid-dynamics/sim_data_hub/tree/main#usage) in the 
sim_data_hub repository for a detailed explanation of these files and their usage.

## Credits
The authors of this project are [@CQVera](https://github.com/CQVera), [@ninomenzel1](https://github.com/ninomenzel1) and 
[@mboxberg](https://github.com/mboxberg).

## License
`smart_data_hub` is released under the MIT License. See [LICENSE](LICENSE) file for details.