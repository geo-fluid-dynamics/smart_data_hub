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

URSgui = importlib.import_module(module_str + "sim-data-hub.gui.gui")


# General settings:
settings = {
    "gui_title": 'URS-data-Hub',
    # for the image of logo
    "logo_data_hub_png": 'URSLogoV1.png',
    "logo_data_hub_png_title": 'Data Hub Logo',
    "logo_png": None,
    "uni_logo_png": 'rwth_mbd_en_rgb.png',
    "main_dropdown_title": 'Host rock:'
}


lib_path = {
    'map_lib_path': module_str + 'library.map.Map',
    'regime_lib_path': module_str + 'library.regimes.Regime',
    'yaml_loader_path': module_str + 'sim-data-hub.library.regimes.Regime',
    'export_lib_path': module_str + 'sim-data-hub.export',
    'source_path': os.path.join('..', 'yaml-db'),
    'assets_path': 'assets',
    'client_relpath': os.path.join('assets', 'client'),
    'stylesheet_path': 'stylesheet.css'
}

URSgui.load_lib_path(**lib_path)


URSgui.setup_html_gui(**settings)

URSgui.app.run_server(debug=False)
