import importlib
import os
module_str = ''
module = None
modules = (os.path.normpath(os.path.split(os.getcwd())[0])).split(os.sep)

for i in range(1, len(modules) + 1):
    try:
        importlib.import_module(modules[-i])
        module_str = modules[-i] + '.' + module_str
        module = modules[-i]
        break
    except (ModuleNotFoundError, ValueError) as error:
        module_str = modules[-i] + '.' + module_str

if module is None:  # only contains submodule sim-data-hub
    module_str = ''
    module = 'sim-data-hub'

simMap = importlib.import_module(module_str + "sim-data-hub.library.map.Map")

class Map(simMap.Map):

    def set_map_offline(self, data_file_path: str = None):
        """
        Method to determine which map to use.
        """
        if data_file_path is None:
            # relative path to data directory
            data_file_path = '../../gui/assets/custom_tiles'

        if self.map_name.lower() == 'claystone':
            # names of _default tiles dir, zoom level: 1 to 6, format .jpg or .png depends on tiles
            tile_set = os.path.join('USGS_National_Map_Topo', '{z}', '{x}', '{y}.png')
            self.attribute = '@ Mobile Atlas Creator(MOBAC)'

        elif self.map_name.lower() == 'salt':
            # names of _default tiles dir, zoom level: 1 to 6, format .jpg or .png depends on tiles
            tile_set = os.path.join('USGS_National_Map_Topo', '{z}', '{x}', '{y}.png')
            self.attribute = '@ Mobile Atlas Creator(MOBAC)'
        elif self.map_name.lower() == 'crystalline':
            # names of _default tiles dir, zoom level: 1 to 6, format .jpg or .png depends on tiles
            tile_set = os.path.join('USGS_National_Map_Topo', '{z}', '{x}', '{y}.png')
            self.attribute = '@ Mobile Atlas Creator(MOBAC)'
        else:
            raise NotImplementedError(
                'Currently only claystone, salt and crystalline are available for map online plotting')
        # local path for tiles to pass to folium Map
        self.tiles_path = os.path.join(data_file_path, tile_set)

    def set_map_online(self):
        # have to run these steps
        # if it is online, we have to set special online tile for these maps
        if self.map_name.lower() == 'claystone':
            self.tiles_path = self.tiles_path
            self.attribute = 'leaflet'
        elif self.map_name.lower() == 'salt':
            self.tiles_path = self.tiles_path
            self.attribute = 'leaflet'

        elif self.map_name.lower() == 'crystalline':
            self.tiles_path = self.tiles_path
            self.attribute = 'leaflet'

        else:
            raise NotImplementedError(
                'Currently only claystone, salt and crystalline are available for map online plotting')
