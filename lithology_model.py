from dash import Dash, html, dcc, callback, Output, Input, dash_table, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import gempy as gp
import gempy_viewer as gpv
import pyvista as pv
import webbrowser
from matplotlib.pyplot import cm
import numpy as np
from matplotlib.colors import to_hex
import os
from os import listdir, walk
from os.path import isfile, join
import yaml

geomodel_colors = px.colors.qualitative.Dark24


def yml_files_in_dir(dir_name: str):
    dir_path = os.path.join(
        os.path.realpath(os.path.dirname(__file__)),
        os.path.join("data_hub", "yaml-db", dir_name),
    )
    file_list = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    yml_files = [file[:-4] for file in file_list if file.endswith(".yml")]
    return yml_files


def folders_in_dir(dir_name: str):
    dir_path = os.path.join(
        os.path.realpath(os.path.dirname(__file__)),
        os.path.join("data_hub", "yaml-db", dir_name),
    )
    dir_list = []
    for dirpath, dirnames, filenames in walk(dir_path):
        dir_list.extend(dirnames)
        break
    return dir_list


def load_geomodel(site_name: str):
    site_geo_path = os.path.join(
        os.path.realpath(os.path.dirname(__file__)),
        os.path.join("data_hub", "yaml-db", "geometry", site_name),
    )

    site_orientation_path = os.path.join(site_geo_path, "orientations.csv")
    site_points_path = os.path.join(site_geo_path, "points.csv")
    points_csv = pd.read_csv(site_points_path)

    formation_list = list(dict.fromkeys(list(points_csv["formation"])))
    extent_geometry = [
        min(0, min(list(points_csv["X"]))),
        max(0, max(list(points_csv["X"]))),
        min(0, min(list(points_csv["Y"]))),
        max(0, max(list(points_csv["Y"]))),
        min(0, min(list(points_csv["Z"]))),
        max(0, max(list(points_csv["Z"]))),
    ]
    formation_dict = dict(zip(formation_list, formation_list))

    geo_data = gp.create_geomodel(
        project_name=site_name,
        extent=extent_geometry,
        refinement=4,
        importer_helper=gp.data.ImporterHelper(
            path_to_orientations=site_orientation_path,
            path_to_surface_points=site_points_path,
        ),
    )

    surface_data = gp.map_stack_to_surfaces(geo_data, formation_dict)

    data_model = gp.compute_model(geo_data)

    model_img = gpv.plot_3d(model=geo_data, show=False)

    len_formation = len(formation_list)

    # layer_colors = [to_hex(c) for c in cm.tab20.colors]
    layer_colors = geomodel_colors
    plotter_model = pv.Plotter()
    plotter_model.add_mesh(mesh=model_img.surface_points_mesh, show_scalar_bar=False)
    plotter_model.add_mesh(
        mesh=model_img.regular_grid_actor.GetMapper().GetInput(),
        cmap=layer_colors[0:len_formation],
        opacity=0.7,
        show_scalar_bar=False,
    )

    for i in range(len_formation):
        plotter_model.add_mesh(
            mesh=model_img.surface_poly[formation_list[i]],
            color=layer_colors[i],
            show_scalar_bar=False,
        )

    plotter_model.show_grid(color="gray", grid="front")
    filename_html = site_name + ".html"
    plotter_model.export_html(filename_html)
    return filename_html


def load_yaml(file_name: str):
    lithology = " "
    age = " "
    name = " "
    description = " "
    geometry = " "
    with open(file_name) as file:
        yaml_data = yaml.load(file, Loader=yaml.loader.SafeLoader)
        if "lithology" in yaml_data.keys():
            lithology = yaml_data.pop("lithology")
        if "age" in yaml_data.keys():
            age = yaml_data.pop("age")
        if "name" in yaml_data.keys():
            name = yaml_data.pop("name")
        if "description" in yaml_data.keys():
            description = yaml_data.pop("description")
        if "geometry" in yaml_data.keys():
            geometry = yaml_data.pop("geometry")

        props = pd.DataFrame.from_dict(yaml_data, orient="index").T

    props_dict = {"lithology": lithology, "age": age,
                  "name": name, "description": description,
                  "geometry": geometry, "properties": props}

    return props_dict


def load_site_yaml(site_name: str):
    site_path = os.path.join(
        os.path.realpath(os.path.dirname(__file__)),
        os.path.join("data_hub", "yaml-db", "site"),
    )
    site_yaml_path = os.path.join(site_path, site_name + ".yml")
    props_dict = load_yaml(site_yaml_path)
    return props_dict


def create_stratigraphic_table(site_strata: list):
    ids = ["Stratigraphy"]
    labels = ["Stratigraphy"]
    parents = [""]
    geomodel_strata = []

    c_k = 0
    strata_colors = ["lightgrey"]

    for strata in site_strata:
        strata_names = strata.split('-')
        root = "Stratigraphy"
        geomodel_strata.append(strata_names[-1])

        for i in range(len(strata_names)):
            id_name = "-".join(strata_names[:i + 1])  # combining the name again using '-'
            if id_name not in ids:
                ids.append(id_name)

                if id_name in site_strata:
                    strata_colors.append(geomodel_colors[c_k])
                    c_k = c_k + 1
                else:
                    strata_colors.append("lightgrey")

                # add the splitted name
                labels.append(strata_names[i])

                parents.append(root)
            root = id_name  # hierarchy is divided by '-' and a root is always the id_name before '-'

    fig = go.Figure(
        go.Icicle(
            ids=ids,
            labels=labels,
            parents=parents,
            marker_colors=strata_colors,
            hovertext=[""],
            textinfo="label+text",
            sort=False,
        )
    )
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    return fig


site_dropdown_list = yml_files_in_dir("site")
site_dropdown_list = ["DE_North_Claystone", "test"]
geometry_folder_list = folders_in_dir("geometry")

app = Dash(external_stylesheets=["assets/dashboard.css"])
app.title = "Smart Data Hub"
df = px.data.tips()

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    className="header",
                    children="Site selection with 3D structural geological modeling and properties",
                    style={"textAlign": "center", "color": "black"},
                ),
                html.P(children="Select site:"),
                dcc.Dropdown(
                    id="site_dropdown",
                    options=site_dropdown_list,
                    placeholder="Select a site name...",
                    clearable=False,
                ),
            ]
        ),
        html.Div(
            className="model_and_properties",
            children=[
                dcc.Store(id="model_html_list"),
                html.Div(
                    className="geomodel",
                    children=[
                        html.H1(
                            className="geomodel_header",
                            children="3D Structural Geomodel",
                            style={"textAlign": "center", "color": "black"},
                        ),
                        html.Iframe(id="3d_model", className="iframe_geomodel"),
                    ],
                ),
                html.Div(
                    className="properties",
                    children=[
                        html.H1(
                            className="stratigraphy_header",
                            children="lithostratigraphy",
                            style={"textAlign": "center", "color": "black"},
                        ),
                        dcc.Store(id="site_strata_list"),
                        dcc.Store(id="site_props_dict"),
                        dcc.Store(id="site_name_value"),
                        dcc.Graph(id="icicle_props", className="icicle_stratigraphy"),
                        dcc.Store(id="yaml_files_dict"),
                        html.Div(id="properties_table"),
                    ],
                ),
            ],
        ),
    ]
)


@app.callback(
    Output("3d_model", "srcDoc"),
    Output("model_html_list", "data"),
    Input("site_dropdown", "value"),
    State("model_html_list", "data"),
)
def display_3d_model(site_name, model_html_list):
    if site_name is None:
        return None, []
    elif site_name not in geometry_folder_list:
        return "No geomodel available!", model_html_list
    else:
        site_name_html = site_name + ".html"
        # if the load_geomodel function has been called before, then one can directly load the html
        if site_name_html in model_html_list:
            return open(site_name_html, "rt").read(), model_html_list
        else:
            model_html = load_geomodel(site_name)
            model_html_list.append(model_html)
            return open(model_html, "rt").read(), model_html_list


@app.callback(
    Output("icicle_props", "figure"),
    Output("site_strata_list", "data"),
    # Output("site_props_dict", "data"),
    Input("site_dropdown", "value"),
)
def display_stratigraphic_table(site_name):
    if site_name is None:
        fig = go.Figure()
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        return fig, []
    else:
        site_props_dict = load_site_yaml(site_name)
        site_strata = (site_props_dict["properties"]).columns.values.tolist()

        fig = create_stratigraphic_table(site_strata)
        fig.update_traces(hovertext=[site_props_dict["description"]], selector=dict(type='icicle'))

        return fig, site_strata


@app.callback(
    Output("properties_table", "children"),
    Output("yaml_files_dict", "data"),
    Output("site_name_value", "data"),
    Input("icicle_props", "clickData"),
    Input("site_strata_list", "data"),
    Input("site_dropdown", "value"),
    # Input("site_props_dict", "data"),
    State("site_name_value", "data"),
    State("yaml_files_dict", "data"),
)
def update_layer_tables(clickData, site_strata, site_name,
                        site_name_value, yaml_files_dict):
    layer_name = clickData

    if layer_name is None:
        return [], {}, site_name
    else:
        id_name = layer_name["points"][0]["id"]
        if id_name in site_strata and site_name == site_name_value:
            site_props_dict = load_site_yaml(site_name)
            properties_table = (load_yaml(site_props_dict["properties"][id_name]["properties"])["properties"]).T
            properties_table = properties_table.reset_index()
            properties_table = properties_table.rename(columns={"index": "property"})

            childrens = [
                html.Div(
                    className="table_props",
                    children=[dash_table.DataTable(data=(properties_table).to_dict("records"))],
                )
            ]
            return childrens, [], site_name
        else:
            return [], [], site_name


if __name__ == "__main__":
    app.run_server(debug=True)
