###############################################################
#
# data hub Map class to plot coordinates on the map
# Qian @ RWTH, July 2020
################################################################
import os
import webbrowser

# Python imports
import cartopy.crs as ccrs
import folium
import matplotlib.pyplot as plt
import numpy as np


class Map:
    """
    Class for visualization of locations on the Map.
    """

    def __init__(self, location_list=None, map_offline: bool = False, zoom_start='auto',
                 zoom_min=0, tiles_path: str = 'Stamen Terrain', projection: str = 'Mercator',
                 show_meta: bool = True, map_name: str = 'Earth'):
        """
        :param location_list: The list of locations
        :param map_offline: If there are custom maps, 'map_offline' should be set to 'True'. Default is 'False'
        :param zoom_start: Initial zoom level for the map (integer) or 'auto' (str). Default is 'auto'
        :param zoom_min: Minimum zoom level for the map (integer). Default is 0.
        :param tiles_path: Earth Tilesets in Folium (For online usage, “OpenStreetMap”, “Mapbox Bright” (Limited levels
         of zoom for free tiles), “Mapbox Control Room” (Limited levels of zoom for free tiles), “Stamen” (Terrain,
         Toner,and Watercolor), “Cloudmade” (Must pass API key), “Mapbox” (Must pass API key), “CartoDB” (positron and
        dark_matter)). Default is "Stamen Terrain"
        :param  projection: Map projection ('Mercator' (refers to displaying map by Folium), 'AzimuthalEquidistant'
        (refers to displaying map by Cartopy, mainly for publication purpose. This projection provides accurate angles
        about and distances through the central position. Other angles, distances, or areas may be distorted.)). Default
        is 'Mercator'
        :param show_meta: If true a tooltip and a popup that appers on clicking on the symbol will appear. Default is
        True
        :param map_name: The name for which map we want to work with (Currently we have maps for 'Earth', 'Europa'
        , 'Mars', 'Enceladus' and 'Ganymede'). Default is 'Earth'
        """
        super().__init__()
        if location_list is None:
            location_list = []
        self.location_insert = folium.map.FeatureGroup()  # a feature group for inserting locations
        self.location_list = location_list
        self.location_map = None
        self.latitude_center = 0.  # location for the folium.Map, for the purpose of displaying locations the best
        self.longitude_center = 0.
        self.zoom_start = zoom_start
        self.zoom_min = zoom_min
        self.tiles_path = tiles_path
        self.map_offline = map_offline
        self.projection = projection
        self.location_latitude_list = []  # list for storing the latitude of locations, for the purpose of using Cartopy
        self.location_longitude_list = []
        self.attribute = 'leaflet'
        self.show_tooltip = show_meta
        self.map_name = map_name  # storing the name for map, for the purpose of choosing different map
        self.sw_corner = None
        self.ne_corner = None

    def load_map(self, data_file_path: str = None):
        """
        Method to store location coordinates in self.location_insert and calculate the map center point.
        """
        if self.map_offline:
            self.set_map_offline(data_file_path=data_file_path)
        if self.projection == 'Mercator' and (not self.map_offline):  # If we want to use Cartopy, then we do not
            self.set_map_online()

        for location in self.location_list:
            location_file = os.path.split(location.propsfile)[-1]
            location_name = location.name if location.name != 'Default' else location_file

            # load location into lists
            if not location.props.__contains__('location'):  # if not, set a random coordinate for the file
                continue

            location_latitude = location.props['location']['value']['N']
            location_longitude = location.props['location']['value']['E']
            location_color = 'yellow'  # assign the color for real loactions
            self.location_latitude_list.append(location_latitude)  # storing the coordinates for Cartopy
            self.location_longitude_list.append(location_longitude)

            # Assembly the popup information
            location_str = f'{location_latitude}° N' if location_latitude >= 0 else f'{-1. * location_latitude}° S'
            location_str += ', '
            location_str += f'{location_longitude}° E' if location_longitude >= 0 else f'{-1. * location_longitude}° W'
            popup = f'''<h4>{location_name}</h4>
                        {location_str}<br><br>
                        <b>Properties:</b> {', '.join(sorted(location.props.columns.values))}<br><br>
                        <i>({location_file})</i>'''

            # insert the locations
            kwargs = {'radium': 7, 'color': location_color, 'fill': True, 'fill_opcity': 0.4, 'fill_color': 'red'}
            if self.show_tooltip:
                kwargs.update({'tooltip': location_name, 'popup': popup})
            self.location_insert.add_child(
                folium.CircleMarker((location_latitude, location_longitude), **kwargs))
            # for calculating the mean, actually they are the sum
            self.latitude_center += location_latitude
            self.longitude_center += location_longitude
            # update bounds
            if self.sw_corner is None:
                self.sw_corner = [location_latitude, location_longitude]
            else:
                self.sw_corner = [min(self.sw_corner[0], location_latitude), min(self.sw_corner[1], location_longitude)]
            if self.ne_corner is None:
                self.ne_corner = [location_latitude, location_longitude]
            else:
                self.ne_corner = [max(self.ne_corner[0], location_latitude), max(self.ne_corner[1], location_longitude)]
            if self.location_list:
                self.latitude_center /= len(self.location_list)
            self.longitude_center /= len(self.location_list)

    def show_map(self, show=False, filename_html: str = 'map.html', filename_png: str = 'map.png'):
        """
        Method to plot locations into the map and create a map.html
        """
        if self.projection == 'AzimuthalEquidistant':  # using Cartopy
            ax = plt.axes(projection=ccrs.AzimuthalEquidistant(central_longitude=self.longitude_center,
                                                               central_latitude=self.latitude_center))
            ax.plot(self.location_longitude_list, self.location_latitude_list, 'r.', label='locations',
                    transform=ccrs.Geodetic())
            ax.legend(loc='best')
            ax.set_global()
            ax.stock_img()
            ax.coastlines()
            ax.gridlines()
            plt.savefig(filename_png)
            if show:
                plt.show()
        else:  # using folium
            # evaluate state of location list:
            one_valid_entry = len(self.location_list) == 1 and self.location_list[0].props.__contains__('location')
            more_than_one_valid_entry = len(self.location_list) > 1
            # determine zoom level if not predefined
            if self.zoom_start == 'auto':
                if one_valid_entry:
                    # if only one location has to be shown, determine zoom level according to the scale factor of the
                    # mercator projection (cos(lat)) but keep the minimum zoom level
                    self.zoom_start = max([int(10. * np.cos(np.deg2rad(self.latitude_center))), self.zoom_min])
                else:
                    # if no location has to be shown, use the minimum zoom level
                    self.zoom_start = self.zoom_min
            kwargs = {'zoom_start': self.zoom_start,
                      'min_zoom': self.zoom_min,
                      'tiles': self.tiles_path,
                      'attr': self.attribute}
            if self.map_offline:
                kwargs['min_zoom'] = 1
                kwargs['max_zoom'] = 6
            if self.sw_corner is None or one_valid_entry:
                # is no or one location are shown, set the center of the map to the correct location (or (0,0))
                kwargs['location'] = [self.latitude_center, self.longitude_center]
            self.location_map = folium.Map(**kwargs)
            if self.sw_corner is not None and more_than_one_valid_entry:
                # if more than one location is shown, determine ideal zoom level and map center using folium's
                # "fit_bounds"-method
                self.location_map.fit_bounds([self.sw_corner, self.ne_corner], max_zoom=4)
            # add the locations to the map
            self.location_map.add_child(self.location_insert)
            # save the html-file of the map
            self.location_map.save(filename_html)
            # show map
            if show:
                webbrowser.open(filename_html)

    def set_map_offline(self, data_file_path: str = None):
        """
        Method to determine which map to use.
        """
        if data_file_path is None:
            # relative path to data directory
            data_file_path = '../../gui/assets/custom_tiles'

        if self.map_name.lower() == 'earth':
            # names of _default tiles dir, zoom level: 1 to 6, format .jpg or .png depends on tiles
            tile_set = os.path.join('USGS_National_Map_Topo', '{z}', '{x}', '{y}.png')
            self.attribute = '@ Mobile Atlas Creator(MOBAC)'
        else:
            raise NotImplementedError(
                'Currently only Earth is available for map plotting')
        # local path for tiles to pass to folium Map
        self.tiles_path = os.path.join(data_file_path, tile_set)

    def set_map_online(self):
        # have to run these steps
        # if it is online, we have to set special online tile for these maps
        if self.map_name.lower() == 'earth':
            self.tiles_path = self.tiles_path
            self.attribute = 'leaflet'

        else:
            raise NotImplementedError(
                'Currently only Earth is available for map online plotting')


