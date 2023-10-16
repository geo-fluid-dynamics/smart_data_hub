###############################################################
# 
# Generic Regime class 
# Julia @ RWTH, March 2020
# Qian @ RWTH, July 2020
#
################################################################

# imports from system libraries if necessary
import os

# Python imports
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yaml as yaml
from scipy import interpolate


# import parent class if needed
# from . import ????
# PrettySafeLoader for loading tuple type from .yaml files
class PrettySafeLoader(yaml.CSafeLoader):
    def construct_python_tuple(self, node):
        return tuple(self.construct_sequence(node))


PrettySafeLoader.add_constructor(
    u'tag:yaml.org,2002:python/tuple',
    PrettySafeLoader.construct_python_tuple)


class Regime:
    PLOT_POINTS = 100
    DESCRIPTION_DEFAULT = "(No description)"
    NAME_DEFAULT = "Default"
    HIDDEN_PARAMS = ['_interpolated']

    def __init__(self, name=None, file_name=None):
        # defaulted instance arguments
        self.separator = ": "
        self.populated = False
        self.props = pd.DataFrame()
        self.propsfile = None
        self.site = pd.DataFrame()
        self.site_file = None
        # instance arguments that get optionally passed over by __init__
        self.name = str(name) if name else self.NAME_DEFAULT
        self.description = self.DESCRIPTION_DEFAULT
        self.figures = {}
        self.interpl_dict = {}  # interploation dictionary for storing interpolation functions
        self.profile_data = None  # storing 2D profile data
        if file_name:
            self.load_props(file_name=file_name)

    def __str__(self):
        out = 'REGIME name' + self.separator + self.name + '\n'
        if not self.populated:
            out += 'Regime incomplete!'
        else:
            out += 'Regime' + self.separator + self.name + '\n'
            out += self.props.__repr__()
        out += '\n'
        return out

    def regime_summary(self):
        print('REGIME SUMMARY:')
        print(self.__str__())

    def load_props(self, file_name=None):
        # read *.yaml file and save as pandas dataframe
        if file_name:
            with open(file_name) as file:
                yaml_data = yaml.load(file, Loader=PrettySafeLoader)
                if 'name' in yaml_data.keys():
                    self.name = yaml_data.pop('name')
                if 'description' in yaml_data.keys():
                    self.description = yaml_data.pop('description')
                if 'figures' in yaml_data.keys():
                    self.figures = yaml_data.pop('figures')
                self.props = pd.DataFrame.from_dict(yaml_data, orient='index').T
                if not self.props.empty:
                    self.props.loc['_interpolated'] = [dict() for i in range(self.props.shape[1])]
                self.propsfile = file_name
                self.populated = True

        else:
            print('Please specify YAML file to load properties')
            print('\n')

        # load properties like temperature, density, salt concentration
        if hasattr(self.props, "properties_distribution"):
            # preparing the data from 2D files
            props_distribution_name = self.props['properties_distribution']['value']
            # Load data
            data = np.genfromtxt(props_distribution_name, skip_header=15, unpack=True)
            # Calculate Radius and Angle and append them
            # Convert Cartesian coordinate system to polar coordinate system
            data = np.append(data, [np.sqrt((data[0, :] * 1000) ** 2 + (data[1, :] * 1000) ** 2)], axis=0)
            data = np.append(data, [np.arctan2(data[0, :] * 1000, data[1, :] * 1000)], axis=0)

            # calculate the number of profiles
            with open(props_distribution_name, 'r') as openfile:
                nprofiles = int(float(openfile.readlines()[7].split()[-1]))  # number of profiles

            # Separate data into different profiles according to .txt file
            profile_data = []
            for i in range(nprofiles):
                profile_data.append(data[:, i::nprofiles])
            profile_data = np.array(profile_data)
            self.profile_data = profile_data
            print('2D data loaded from txt file:', props_distribution_name, sep=self.separator)

    def load_site(self, file_name=None):
        # read *.yaml file and save as pandas dataframe
        if file_name is not None:
            with open(file_name) as file:
                self.site = pd.DataFrame.from_dict(yaml.safe_load(file), 'index').T
                self.site_file = file_name
                # print('Site specifics loaded from:', file_name, sep = self.separator)
                # print('\n')
        else:
            print('Please specify YAML file to load site specifics')
            print('\n')

    def plot_property(self, name_props=None, props_min=None, props_max=None, multivariable=None, use_plotly=False,
                      gui=False,
                      ):
        """
        Method to plot properties of the Regime class
        :param name_props: specify the property name.
        :param props_min: specify a minimum value.
        :param props_max: specify a maximum value.
        :param multivariable: if the equation contains more than one variable, then the user needs to specify constant
        variable and changing variables in a dictionary form( e.g {'cst':{'x3': 45}, 'noncst':{'x':[3, 78],
         'x2': [23,90]}}). Default is None.
        :param use_plotly: use plotly for plotting the figure. If it is False, then use matplotlib. Default is False.
        :param gui: if it is True, then return a figure. Default is False.
        :return: if gui is True, return a figure; if gui is False, directly display the figure.
        """
        # Get information on the property
        props = self.props[name_props]
        props_type = props['type']  # to define if it is constant or not
        props_value = props['value']  # expression:a string,should call eval

        if props.__contains__('dev_value'):  # in some props have no dev_value
            props_dev = props['dev_value']
        else:
            props_dev = None

        # if dev_value in yaml-file is just a dummy entry
        if props_dev is not None:
            if type(props_dev) is dict:
                if np.any(np.isnan(list(props_dev.values()))):
                    props_dev = None
            elif np.any(np.isnan(props_dev)):
                props_dev = None

        if props_type == 'scalar':
            raise ValueError(
                '{0} is constant: {1}+-{2} {3}'.format(name_props, props_value, props_dev, props['unit_str']))

        # Create axis labels
        try:
            props_xlabel = props['variable'].replace('_', ' ') if 'variable' in props else 'x'
        except AttributeError:
            props_xlabel = props['variable']
        if 'variable_unit_str' in props and props['variable_unit_str'] is not None and \
                not pd.isnull(props['variable_unit_str']):  # The value could also be nan
            try:
                props_xlabel += f" in {props['variable_unit_str']}"
            except TypeError:
                props_xlabel = {}
                for var_name, var, unit in zip(props['variable'].keys(), props['variable'].values(),
                                               props['variable_unit_str'].values()):
                    props_xlabel.update({var_name: var + ' in ' + unit})

        props_ylabel = name_props.replace('_', ' ')
        if 'unit_str' in props and props['unit_str'] is not None:
            props_ylabel += f" in {props['unit_str']}"

        if props_type == 'expression':
            mappings = {'exp': np.exp, 'sqrt': np.sqrt, 'sin': np.sin, 'cos': np.cos, 'tan': np.tan}
            if multivariable is not None:  # if we have more than one variable.
                cst_list = multivariable['cst']
                noncst_list = multivariable['noncst']
                selected_noncst = list(noncst_list)
                mappings.update(cst_list)
                if len(selected_noncst) == 1:  # if we have only changing variable, then 2D plot
                    props_min = noncst_list[selected_noncst[0]][0]
                    props_max = noncst_list[selected_noncst[0]][1]
                else:  # if we have two variable, then 3D plot
                    props_min = [noncst_list[selected_noncst[0]][0], noncst_list[selected_noncst[1]][0]]
                    props_max = [noncst_list[selected_noncst[0]][1], noncst_list[selected_noncst[1]][1]]
            else:
                selected_noncst = ['x']

            if props_min is None or props_max is None:
                raise ValueError("Provide property's name as well as min and max for plotting.")

            x = np.linspace(props_min, props_max, self.PLOT_POINTS)
            if type(props_min) == list:  # 3D plot
                x, x2 = np.meshgrid(x[:, 0], x[:, 1])
                noncst_list.update({selected_noncst[0]: x})
                noncst_list.update({selected_noncst[1]: x2})
                mappings.update(noncst_list)
                props_y = eval(props_value, mappings)
            else:  # 2D plot
                props_y = list()
                for value in x:
                    mappings.update({selected_noncst[0]: value})
                    props_y.append(eval(props_value, mappings))  # eval(expression)
                props_y = np.array(props_y)
                if type(props_xlabel) == dict:  # if we have variable with a dict input
                    props_xlabel = props_xlabel[selected_noncst[0]]
            symbol = 'b-'
        elif props_type == 'tabulated':
            x = list(props_value.keys())
            props_y = list(props_value.values())
            symbol = 'b.'
        else:
            raise NotImplementedError('Currently only expressions and tabulated values can be plotted.')

        y_err = None
        if props_type == 'expression' or props_type == 'tabulated':
            if type(props_dev) == dict:
                y_err = list(props_dev.values())
            elif (type(props_dev) == float or type(props_dev) == int) and not np.isnan(props_dev):
                y_err = props_dev

            if use_plotly:
                labels = {'x': props_xlabel, 'y': props_ylabel}
                if props_type == 'expression':
                    try:  # 2D plot
                        fig = px.line(x=x, y=props_y, title=name_props, labels=labels)
                        fig.update_traces(name='Data', showlegend=True)
                    except ValueError:  # 3D plot
                        fig = go.Figure(data=[go.Surface(x=x, y=x2, z=props_y)])
                        fig.update_traces(contours_z=dict(show=True, usecolormap=True, highlightcolor="limegreen",
                                                          project_z=True))
                elif props_type == 'tabulated':
                    fig = px.scatter(x=x, y=props_y, error_y=y_err, title=name_props, labels=labels)
                    fig.update_traces(name='Data', showlegend=True)
                if self.props[name_props]['_interpolated']:
                    fig.add_trace(go.Scatter(x=list(self.props[name_props]['_interpolated'].keys()),
                                             y=list(self.props[name_props]['_interpolated'].values()),
                                             name='_interpolated',
                                             mode='markers'))
            else:  # matplotlib
                fig, ax = plt.subplots()
                try:  # 2D plot
                    ax.errorbar(x, props_y, fmt=symbol, yerr=y_err, xerr=None, label='Data')
                except ValueError:  # plot contour map
                    levels = np.linspace(np.min(props_y), np.max(props_y), 50)
                    cset = ax.contourf(x, x2, props_y, levels, cmap=cm.get_cmap('terrain', len(levels) - 1))
                    cbar = fig.colorbar(cset, ax=ax, orientation="vertical")
                    cbar.ax.set_title(props_ylabel)

                    props_ylabel = props_xlabel[selected_noncst[1]]
                    props_xlabel = props_xlabel[selected_noncst[0]]

                    ax.set_ylim((props_min[1], props_max[1]))

                    props_min = props_min[0]
                    props_max = props_max[0]

                if self.props[name_props]['_interpolated']:
                    ax.plot(list(self.props[name_props]['_interpolated'].keys()),
                            list(self.props[name_props]['_interpolated'].values()), 'r.', label='_interpolated')
                if props_min and props_max:
                    ax.set_xlim((props_min, props_max))
                ax.set_xlabel(props_xlabel)
                ax.set_ylabel(props_ylabel)
                ax.set_title(name_props)
                ax.legend(loc='best')
            if gui:
                return fig
            else:
                if use_plotly:
                    fig.show()
                else:
                    plt.show()

    def get_scalar_prop_value(self, name_props=None, variable=None, interpolation_type='cubic', **variables):
        """
        Method to get a scalar value from tables or expressions. This can be used as a black box for accessing data.
        :param name_props: Name of the field
        :param variable: Parameter to determine value of name_props, i.e., name_props(variable).
        :param interpolation_type: Specifies the kind of interpolation as a string (‘linear’, ‘nearest’, ‘zero’,
         ‘slinear’, ‘quadratic’, ‘cubic’, ‘previous’, ‘next’, where ‘zero’, ‘slinear’, ‘quadratic’ and ‘cubic’ refer to
         a spline interpolation of zeroth, first, second or third order; ‘previous’ and ‘next’ simply return the
         previous or next value of the point) or as an integer specifying the order of the spline interpolator to use
         (see scipy.interpolate.interp1d). Default is ‘cubic’.
        :param variables: Additional variables with its value needs to be specified here.
        :return:
        """
        # Get information on the property
        prop = self.props[name_props]
        prop_type = prop['type']  # to define if it is constant or not
        prop_value = prop['value']  # expression: a string,should call eval

        mapping = {'x': variable, 'exp': np.exp, 'sqrt': np.sqrt, 'sin': np.sin, 'cos': np.cos, 'tan': np.tan}
        mapping.update(variables)

        if prop_type == 'expression':
            prop_y = eval(prop_value, mapping)  # eval(expression)
        elif prop_type == 'tabulated':
            self.interpolation(name_props=name_props, interpl_list=[variable], kind=interpolation_type)
            prop_y = self.props[name_props]['_interpolated'][variable]
        elif prop_type == 'scalar':
            prop_y = prop_value
        else:
            raise NotImplementedError('This method only works for expressions, tabulated and scalar values.')
        return prop_y

    def interpolation(self, name_props: str = None, interpl_list=None, overwrite: bool = True, kind='quadratic'):
        """
        Method to interpolate between known values of a tabulated property.
        :param name_props: Name of the property
        :param interpl_list: List of values at which the interpolation should be done
        :param overwrite: If there are already interpolated values available, should they be overwritten (True) or kept
        / updated (False)? Default is True.
        :param kind: Specifies the kind of interpolation as a string (‘linear’, ‘nearest’, ‘zero’, ‘slinear’,
        ‘quadratic’, ‘cubic’, ‘previous’, ‘next’, where ‘zero’, ‘slinear’, ‘quadratic’ and ‘cubic’ refer to a spline
        interpolation of zeroth, first, second or third order; ‘previous’ and ‘next’ simply return the previous or next
        value of the point) or as an integer specifying the order of the spline interpolator to use
        (see scipy.interpolate.interp1d). Default is ‘quadratic’.
        """
        # Get information on the property
        props = self.props[name_props]
        props_type = props['type']  # to define if its tabulated or not
        props_value = props['value']

        if not (props_type == 'tabulated'):
            raise NotImplementedError('It is currently only possible to interpolate tabulated values.')

        # if the given property and kind have been computed or not
        if self.interpl_dict.__contains__(name_props) and self.interpl_dict[name_props].__contains__(kind):
            # returns a function to find the interpolated values
            interpl_f = self.interpl_dict[name_props][kind]
        else:
            x = list(props_value.keys())
            y = list(props_value.values())
            # returns a function to find the interpolated values
            interpl_f = interpolate.interp1d(x, y,  # default quadratic refers to spline interpolation of second order
                                             kind=kind)
            if self.interpl_dict.__contains__(name_props):
                self.interpl_dict[name_props].update({kind: interpl_f})
            else:
                self.interpl_dict.update({name_props: {kind: interpl_f}})

        # if overwrite is True
        if overwrite:
            self.props[name_props]['_interpolated'] = dict(
                zip(interpl_list, interpl_f(interpl_list)))  # to store the interpolation values in interpolated
        else:  # if not overwritten, then add the new interpolated values
            self.props[name_props]['_interpolated'].update(dict(zip(interpl_list, interpl_f(interpl_list))))

    def save_regime(self, filename: str):
        """
        Method to save the properties to a yaml file.
        :param filename: location to store the data
        """
        output = self.props
        for prop in output:
            for hidden_param in self.HIDDEN_PARAMS:
                try:
                    del output[prop][hidden_param]
                except KeyError:
                    pass
        if self.name != self.NAME_DEFAULT:
            output['name'] = self.name
        if self.description != self.DESCRIPTION_DEFAULT:
            output['description'] = self.description
        output['figures'] = self.figures
        with open(filename, 'w') as file:
            yaml.dump(output, file)

    def load_regime(self):
        # Re-load regime that had been saved previously 
        pass


# unit test and demo
# run by executing module directly: python Regime.py

if __name__ == "__main__":
    # create Regime objects for different argument options
    r1 = Regime()
    r2 = Regime("Sea Ice Lab")


    r32 = Regime('Sea Ice Lab')


    # specify databases
    dirname = os.path.dirname(__file__)
    r2.load_props(os.path.join(dirname, "../../yaml-db/_default/props.yaml"))

    r32.load_props(os.path.join(dirname, "../../yaml-db/earth/multivaribales_equations.yaml"))


    r1.regime_summary()
    r2.regime_summary()

    # this is the syntax needed to access entries/types of the scalar_props and site dataframe
    print('Print first shear_modulus_ice entry in pandas dataframe ice_props')
    print(r2.props.at['value', 'shear_modulus_ice'])
    print('\n')
    print('Print data type of shear_modulus_ice entry in dataframe ice_props')
    print(type(r2.props.at['value', 'shear_modulus_ice']))
    print('\n')
    # this is the unit test for plotting
    print('___plotting test___:')
    print('\n')
    print('Plotting expression')
    r2.plot_property('latent_heat_sublimation_ice', 10, 273.15)

    print("___test one variable but a dict as input___")
    r32.plot_property('test_case2', multivariable={'cst': {}, 'noncst': {'x': [3, 78], 'x2': [4, 89]}}, use_plotly=True)
    r32.plot_property('test_case3', multivariable={'cst': {'x2': 45}, 'noncst': {'x3': [3, 78], 'x': [13, 78]}})
    r32.plot_property('test_case3', multivariable={'cst': {'x2': 45}, 'noncst': {'x3': [3, 78], 'x': [13, 78]}},
                      use_plotly=True)
    r32.plot_property('test_case3', multivariable={'cst': {'x2': 45, 'x': 10}, 'noncst': {'x3': [3, 78]}},
                      use_plotly=True)
    r32.plot_property('test_case3', multivariable={'cst': {'x2': 45, 'x': 10}, 'noncst': {'x3': [3, 78]}})
    print('\n')
    print('Plotting tabulated')
    r2.plot_property('density_firn', 0, 80)
    print('\n')
    # this is the unit test for interpolation
    r2.interpolation('density_firn', [50, 60], overwrite=False)
    r2.plot_property('density_firn', 0, 80)
    r2.interpolation('poisson_firn', [20, 30], kind='linear')
    r2.plot_property('poisson_firn', 0, 80)
    r2.interpolation('density_firn', [20, 30], overwrite=False)
    r2.interpolation('density_firn', [22, 33], kind='linear', overwrite=False)
    r2.plot_property('density_firn', 0, 80)
    print('The interpolated list of density_firn')
    print(r2.props.density_firn['_interpolated'])
