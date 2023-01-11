import importlib

simRegime = importlib.import_module("sim-data-hub.library.regimes.Regime")


class Regime(simRegime.Regime):
    def load_regime(self):
        pass
