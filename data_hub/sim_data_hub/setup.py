###############################################################
#
# Setup for the Sim Data Hub
# Marc @ RWTH, February 2021
#
################################################################

from setuptools import find_packages, setup


def get_long_description():
    try:
        with open('README.md', 'r') as file:
            return file.read()
    except IOError:
        return ''


setup(
    name='sim_data_hub',
    version='0.dev',
    author='mboxberg',
    url='https://github.com/geo-fluid-dynamics/sim-data-hub',
    description='Accessing and managing of data made simple.',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    license='Licence :: MIT License',
    packages=find_packages()
)
