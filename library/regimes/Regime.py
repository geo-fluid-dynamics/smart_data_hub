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

simRegime = importlib.import_module(module_str + "sim-data-hub.library.regimes.Regime")


class Regime(simRegime.Regime):
    def load_regime(self):
        pass
