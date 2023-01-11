import importlib
import os

URSgui = importlib.import_module("sim-data-hub.gui.gui")


# General settings:
settings = {
    "gui_title": 'URS-data-Hub',
    # for the image of logo
    "logo_data_hub_png": 'logo.png',
    "logo_data_hub_png_title": 'Data Hub Logo',
    "logo_png": 'logo.png',
    "uni_logo_png": 'logo.png',
    "main_dropdown_title": 'Host rock:',
    "client_path_name": os.path.join('../sim-data-hub/gui/assets', 'client')
}


lib_path = {
    'map_lib_path': 'library.map.Map',
    'regime_lib_path': 'library.regimes.Regime',
    'yaml_loader_path': 'sim-data-hub.library.regimes.Regime',
    'export_lib_path': 'sim-data-hub.export',
    'source_path': '../yaml-db',
    'assets_path': '/assets',
    'stylesheet_path': 'stylesheet.css'
}

URSgui.load_lib_path(**lib_path)


URSgui.setup_html_gui(**settings)

URSgui.app.run_server(debug=False)
