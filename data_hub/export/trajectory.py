###############################################################
#
# Routines to export yaml file for trajectory modelling
# Marc @ RWTH, December 2020
#
################################################################

import os

import pandas as pd
import yaml
from data_hub.library.regimes.Regime import Regime as _Regime


def straight_melting(regime, filename: str, defaults=None):
    """
    :param regime: Ice regime (instance of class Regime)
    :param filename: Output file
    :param defaults: Dictionary with files to take _default properties from
    """

    properties_needed = ['temperature_ice', 'density_ice', 'surface_depth', 'melting_temperature_water',
                         'latent_heat_melting_water', 'density_water', 'thermal_conductivity_water',
                         'dynamic_viscosity_water', 'specific_heat_capacity_ice', 'gravitational_acceleration',
                         'specific_heat_capacity_water', 'thickness_ice']

    if defaults is None:
        defaults = [os.path.join(os.pardir, 'yaml-db', '_default', 'default_expression_ice_props.yaml'),
                    os.path.join(os.pardir, 'yaml-db', '_default', 'default_ice_props.yaml')]

    properties = dict()
    for prop in properties_needed:
        found = False
        if prop in regime.props:
            # if possible, get property from given regime object
            properties[prop] = regime.props[prop]
            found = True
        else:
            # lookup property in given _default databases (_default: first look for expression, then for scalar)
            for default_file in defaults:
                r = _Regime()
                r.load_props(default_file)
                if prop in r.props:
                    properties[prop] = r.props[prop]
                    found = True
                    break
        if not found:
            raise ValueError(f'Property {prop} was not found.')

    # clean HIDDEN_PARAMS
    for prop in properties:
        for hidden_param in r.HIDDEN_PARAMS:
            del properties[prop][hidden_param]

    properties_df = pd.DataFrame(properties)

    with open(filename, 'w') as file:
        yaml.dump(properties_df.to_dict(), file)
