###############################################################
#
# Routines to export porousmaterials
# Marc @ RWTH, March 2020
#
################################################################


def matprop(regime, poroelastic=True, saturated=True, translation=None, **kwargs):
    """
    :param regime: Ice regime (instance of class Regime)
    :param poroelastic: Export poroelastic (True) or elastic/anelastic (False) material.
    :param saturated: Export saturated (one fluid; True) or unsaturated (two fluids; False) material.
    :param translation: Dictionary translating keywords of the regime to the porous material keywords.

    Parameters related to porodisp.material classes:
    :param **rho_s: Density of the solid
    :param **mu: Shear modulus / 2nd Lamé parameter of the skeleton
    :param **phi: Porosity
    :param **kappa: Permeability of the skeleton
    :param **rho_w: Density of the fluid
    :param **k_w: Bulk modulus of the fluid
    :param **nu_w: Viscosity of the fluid
    :param **k: (drained) bulk modulus of the skeleton
    :param **k_s: bulk modulus of the matrix material that builds up the skeleton
    Optional parameters related to the tortuosity:
    :param **t: Tortuosity (specify t or t_inv otherwise it will be estimated from the porosity)
    :param **t_inv: Inverse tortuosity (specify t or t_inv otherwise it will be estimated from the porosity)
    :param **r: Geometry factor for the shape of the pores (Default: 0.5; spherical pores)
    """
    # local import to avoid having porodisp as a required package for ice-data-hub
    from porodisp import material

    if not translation:
        if poroelastic:
            translation = {
                'rho_s': 'density_ice',
                'mu': 'shear_modulus_ice',
                'phi': 'porosity_ice',
                'kappa': 'permeability_ice',
                'rho_w': 'density_water',
                'k_w': 'bulk_modulus_water',
                'nu_w': 'dynamic_viscosity_water',
                'k': 'bulk_modulus_drained_ice',
                'k_s': 'bulk_modulus_ice'
            }
            if not saturated:
                translation.update({
                    'rho_nw': 'density_air',
                    'k_nw': 'bulk_modulus_air',
                    'nu_nw': 'dynamic_viscosity_air',
                    's_w': 'saturation_water'
                })
        else:
            translation = {
                'rho': 'density_ice',
                'mu': 'shear_modulus_ice',
                'k': 'bulk_modulus_drained_ice',
                'v_p': 'velocity_P',
                'v_s': 'velocity_S',
                'q_p': 'Q_P',
                'q_s': 'Q_S',
            }

    missing_properties = []
    for name_prop_poro, name_prop_icedb in translation.items():
        if name_prop_poro not in kwargs.keys():
            try:
                kwargs[name_prop_poro] = regime.ice_props[name_prop_icedb]['value']
            except KeyError:
                missing_properties.append(name_prop_icedb)
    if poroelastic:
        if missing_properties:
            raise AttributeError(f'Cannot export regime due to missing attribute(s): {", ".join(missing_properties)}')
        if saturated:
            return material.PoroelasticSaturated(**kwargs)
        else:
            return material.PoroelasticUnsaturated(**kwargs)
    else:
        try:
            rho = kwargs.pop('rho')
            if 'Q_P' in missing_properties or 'Q_S' in missing_properties:
                return material.Elastic(rho, **kwargs)
            else:
                return material.Viscoelastic(rho, **kwargs)
        except KeyError:
            raise AttributeError(f'Cannot export regime due to missing attribute(s): {", ".join(missing_properties)}')
        except ValueError as error:
            raise AttributeError(
                f'Cannot export regime due to missing attribute(s): {", ".join(missing_properties)}. {error}')
