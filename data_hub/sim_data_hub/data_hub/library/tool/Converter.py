###############################################################
#
# Class for converting .txt to .yaml
# Qian @ RWTH, October 2020
#
################################################################

# Python import
import yaml as yaml
import numpy as np


class Converter:
    """
    class for converting .txtx to .yaml
    """

    def __init__(self):
        self.res = None
        self.res_str = None
        self.value_dict = None

    def load_file(self, file_name: str = None):
        """
        Method for loading the .txt file, save the data into a numpy.array
        :param file_name: Name of the .txt file
        :return: a numpy.array and a str which stores the names of variables
        """

        data_file = []
        with open(file_name, 'r') as f:
            data = f.readlines()
        for i, line in enumerate(data):
            # only take the numbers
            if i > 0:  # suppose the first line only contains string
                tmp = list(map(float, line.split()))  # convert str to float
                data_file.append(tmp)
            else:
                self.res_str = line.split()
        self.res = np.array(data_file)
        return self.res, self.res_str

    def create_value_dict_1d(self, key_list=None, value_list=None):
        """
        Method for creating a dictionary (for 1D file)
        :param key_list: dictionary key_list
        :param value_list: dictionary value_list
        :return: a dict
        """

        if value_list is None:
            value_list = []
        if key_list is None:
            key_list = []
        self.value_dict = dict(zip(key_list.tolist(), value_list.tolist()))
        return self.value_dict

    def create_value_dict_2d(self, key_tuple: tuple = None, value_list=None):
        """
        Method for creating a dictionary (for 2D file)
        :param key_tuple: dictionary key_tuple
        :param value_list: dictionary value_list
        :return: a dict
        """

        if value_list is None:
            value_list = []

        key_numpy = np.vstack(key_tuple).T  # concatenate arrays
        key_tuple = tuple(map(tuple, key_numpy.tolist()))  # convert numpy to tuple

        self.value_dict = dict(zip(key_tuple, value_list.tolist()))
        return self.value_dict

    @staticmethod
    def create_yaml(save_file_name='test.yaml', ice_props_name: str = None,
                    value: dict = None,
                    dev_pdf: str = None,
                    dev_value=None,
                    source: str = None,
                    meta_free: str = None,
                    meta_sys: str = None,
                    unit_str: str = None,
                    variable: str = None,
                    unit: list = None, variable_unit_str: str = None, variable_unit: list = None):
        """
        :param save_file_name : The new yaml files name
        :param ice_props_name: name of ice property
        :param value: the value of ice property, which is in the form of dictionary
        :param dev_pdf: Gauss or other parametrized or tabulated PDF
        :param dev_value: hyperparameters of PDF or array
        :param source: data source
        :param meta_free: free text metadata
        :param meta_sys: metadata from systematic databases, e.g. NASA database
        :param unit_str: standard string to inidate unit
        :param variable: function argument
        :param unit: unit in systematically documented SI units [ kg m s K A mol cd ]
        :param variable_unit_str: standard string to indicate variable_unit
        :param variable_unit: unit in systematically documented SI units [ kg m s K A mol cd ]
        """

        ice_props_dict = {
            ice_props_name: {'type': 'tabulated', 'value': value, 'dev_pdf': dev_pdf, 'dev_value': dev_value,
                             'unit': unit, 'unit_str': unit_str,
                             'variable': variable, 'variable_unit_str': variable_unit_str,
                             'variable_unit': variable_unit, 'source': source, 'meta_free': meta_free,
                             'meta_sys': meta_sys}}

        with open(save_file_name, mode='w', encoding='utf-8') as file:
            yaml.dump(ice_props_dict, file)

    @staticmethod
    def merge(file1: str = None, file2: str = None):
        """
        Method for merging two files
        :param file1: name of file1, the content of file2 will be merged into file1
        :param file2: name of file2

        """
        f1 = open(file1, 'a+', encoding='utf-8')
        with open(file2, 'r', encoding='utf-8') as f2:
            f1.write('\n')
            for i in f2:
                f1.write(i)


if __name__ == "__main__":
    Converter_rho = Converter()
    Converter_t = Converter()

    res_rho, res_str_rho = Converter_t.load_file(file_name='2D_data_split.txt')
    res_t, res_str_t = Converter_t.load_file(file_name='2D_data_split.txt')

    value_dict_density = Converter_rho.create_value_dict_2d(key_tuple=(1000.0 * res_rho[:, 0], 1000.0 * res_rho[:, 1],
                                                                       1000.0 * res_rho[:, 2]),
                                                            value_list=res_rho[:, 4])
    value_dict_temperature = Converter_t.create_value_dict_2d(key_tuple=(1000.0 * res_t[:, 0], 1000.0 * res_t[:, 1],
                                                                         1000.0 * res_t[:, 2]), value_list=res_t[:, 3])

    Converter_rho.create_yaml(save_file_name='file1_2D.yaml', ice_props_name='density_ice', value=value_dict_density,
                              unit_str='kg m^-3',
                              unit=['1 -3 0 0 0 0 0'], variable='radius', variable_unit_str='m',
                              variable_unit=['0 1 0 0 0 0 0'])
    Converter_t.create_yaml(save_file_name='file2_2D.yaml', ice_props_name='temperature_ice',
                            value=value_dict_temperature,
                            unit_str='K',
                            unit=['0 0 0 1 0 0 0'], variable='radius', variable_unit_str='m',
                            variable_unit=['0 1 0 0 0 0 0'])

    Converter.merge(file1='file1_2D.yaml', file2='file2_2D.yaml')
    Converter.merge(file1='europa_ice_2D.yaml', file2='file1_2D.yaml')
