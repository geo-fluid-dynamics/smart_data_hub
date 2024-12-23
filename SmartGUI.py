from dash import Dash, html, dcc, Output, Input, dash_table, State
import pandas as pd
import plotly.graph_objects as go
import pyvista as pv
import os
from os import listdir, walk
from os.path import isfile, join
import yaml
import dash_vtk


def RGBtxt_to_dict(file_path: str, color_type: str):
    """
    Convert text to Dict.
    @param file_path: path to the txt file.
    @param color_type: str, color type {'to_hex', 'to_rgb'}.
    to_hex: return hex color codes.
    to_rgb: return RGB colors.
    @return: dictionary with all hexadecimal color codes or rgb colors and corresponding lithologies.
    """
    result_dict = {}
    with open(file_path, "r") as file:
        for line in file:
            parts = line.split(maxsplit=1)
            if len(parts) == 2:  # Ensure there are at least 2 parts (key and value)
                key = parts[0].strip()
                rgb_value = parts[1].strip()
                # Convert RGB to hex
                rgb = tuple(map(int, rgb_value.split("/")))
                if color_type == 'to_hex':
                    hex_value = "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
                    result_dict[key] = hex_value
                elif color_type == 'to_rgb':
                    result_dict[key] = f"rgb{rgb}"
                else:
                    raise ValueError("Valid value for color_type: ['to_hex', 'to_rgb']")
            elif len(parts) != 2:
                raise ValueError(
                    "No tuple, please make sure the dictionary has the right structure!"
                )

    return result_dict


def load_yaml_to_dict(file_name: str, props_yaml_to_dataframe=True):
    """
    Covert YAML file to a Python Dictionary
    @param file_name: path to a YAML file.
    @param props_yaml_to_dataframe: bool, covert dictionary to pandas dataframe. Default 'True'.
    @return: a Pyhon Dictionary contains: {"lithology", "age", "name", "description", "geometry"}
    """
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

    if props_yaml_to_dataframe:
        yaml_data = pd.DataFrame.from_dict(yaml_data, orient="index").T

    props_dict = {
        "lithology": lithology,
        "age": age,
        "name": name,
        "description": description,
        "geometry": geometry,
        "properties": yaml_data,
    }

    return props_dict


def load_items_in_dir(
        dir_name: str,
        items: str,
):
    """
    Load items (list of YAML files or list of folders or material properties) from dir_name
    @param dir_name: str, path to a folder.
    @param items: str, {'yml_files', 'folders', 'site_props_dict', 'default_props_dict'}.
    'yml_files': Load list of YAML files from dir_name.
    'folders': Loading list of folders from dir_name,
    'site_props_dict' or 'default_props_dict': Load site or default material properties to a Python Dictionary.
    @return: A List of YAML files or List of folders or .
    """
    real_path = os.path.realpath(os.path.dirname(__file__))
    dir_path = os.path.join(
        real_path,
        os.path.join("data_hub", "yaml-db", dir_name),
    )
    if items == "site_props_dict" or items == "default_props_dict":
        props_dict = load_yaml_to_dict(dir_path, props_yaml_to_dataframe=True)
        return props_dict
    elif items == "yml_files":
        file_list = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
        yml_files = [file[:-4] for file in file_list if file.endswith(".yml")]
        return yml_files
    elif items == "folders":
        dir_list = []
        for dirpath, dirnames, filenames in walk(dir_path):
            dir_list.extend(dirnames)
            break
        return dir_list
    else:
        raise ValueError(
            "Valid value for items: ['site_props_dict', 'default_props_dict', 'yml_files', 'folders']"
        )


def load_default_props():
    """
    Load default properties.
    @return: A Python Dictionary that stores all the default properties.
    """
    default_yml_files_names_list = load_items_in_dir(os.path.join("rock_props", "default"), items="yml_files")
    default_props_dict_df = {}
    for default_file_name in default_yml_files_names_list:
        default_dict = load_items_in_dir(
            dir_name=os.path.join("rock_props", "default", default_file_name + ".yml"), items="default_props_dict")
        default_props_dict_df[default_file_name] = default_dict['properties']

    return default_props_dict_df


def fill_in_default_props(stratum_props: pd.DataFrame or str, default_props: pd.DataFrame):
    """
    Load stratum property and its corresponding default properties.
    @param stratum_props: DataFrame or "default". Set to "default" when no stratum property is provided.
    @param default_props: DataFrame. Default property with corresponding lithology and age.
    @return: stratum properties fill in the default values and styles for DataTable.
    """
    if isinstance(stratum_props, str):  # default
        stratum_props_table = (
            (default_props.T.reset_index())
            .rename(columns={"index": "property"})
            .astype(str)
        )
        style_data_conditional = [{"backgroundColor": "rgb(145, 121, 121)", "color": "white"}]

    else:
        stratum_field_names_list = stratum_props.index.tolist()
        full_field_names_list = [
            "type",
            "value",
            "dev_pdf",
            "dev_value",
            "unit_str",
            "unit",
            "variable",
            "variable_unit",
            "variable_unit_str",
            "source",
            "meta_sys",
            "meta_free",
        ]

        # check for missing fields and append those fields to stratum props
        missing_field_names_list = [
            field_names
            for field_names in full_field_names_list
            if field_names not in stratum_field_names_list
        ]
        stratum_props = pd.concat(
            [stratum_props, pd.DataFrame(index=missing_field_names_list)]
        )

        # find missing props and add default props to stratum props
        stratum_props_names_list = stratum_props.columns.values.tolist()
        default_props_names_list = default_props.columns.values.tolist()
        len_default_props = len(default_props_names_list)
        missing_props_names_list = [
            props_name
            for props_name in default_props_names_list
            if props_name not in stratum_props_names_list
        ]
        stratum_props = stratum_props.join(default_props[missing_props_names_list])

        # drop rows that contains only NA
        stratum_props = stratum_props.dropna(how="all")

        # get the current names of all properties
        stratum_props_names_list_updated = stratum_props.columns.values.tolist()

        # find the idex of properties in stratum_props that are also in default_props
        missing_props_table_row_index = [
            stratum_props_names_list_updated.index(props_name)
            for props_name in missing_props_names_list
        ]
        stratum_props_table_row_index = [
            stratum_props_names_list_updated.index(props_name)
            for props_name in default_props_names_list
        ]

        # fill in missing values that exist in default_props with default values
        stratum_props_table = stratum_props.copy()
        stratum_props_table[stratum_props_table.isnull()] = default_props

        # convert stratum_props to dash table
        stratum_props_table = (
            (stratum_props_table.T.reset_index())
            .rename(columns={"index": "property"})
            .astype(str)
        )
        # Highlight cells that are filled with default values
        style_data_conditional = [
                                     {
                                         "if": {
                                             "row_index": [stratum_props_table_row_index[i]],
                                             "column_id": list(
                                                 set(
                                                     stratum_props[
                                                         stratum_props.iloc[
                                                         :, stratum_props_table_row_index[i]
                                                         ].isnull()
                                                     ].index.tolist()
                                                 )
                                                 - set(
                                                     default_props[default_props.iloc[:, i].isnull()].index.tolist()
                                                 )
                                             ),
                                         },
                                         "backgroundColor": "rgb(145, 121, 121)",
                                         "color": "white",
                                     }
                                     for i in range(len_default_props)  # loop over all the default props and find
                                     # fields that contain default values
                                 ] + [
                                     {
                                         "if": {"row_index": missing_props_table_row_index},
                                         "backgroundColor": "rgb(145, 121, 121)",
                                         "color": "white",
                                     }
                                 ]

    return stratum_props_table, style_data_conditional


def load_plydata(site_name: str, sites_material_props_dict: dict, stratum_colors_dict: dict):
    site_strata_names_list = list(sites_material_props_dict[site_name]['strata'].keys())
    plotter_strata = pv.Plotter()

    for stratum in site_strata_names_list:
        stratum_props_file_path = sites_material_props_dict[site_name]['strata'][stratum]["geometry_file_path"]

        if isinstance(stratum_props_file_path, str):  # not None or nan
            stratum_ply = pv.read(stratum_props_file_path)

            plotter_strata.add_mesh(
                stratum_ply,
                color=stratum_colors_dict[stratum],
                name=stratum)

    plotter_strata.show_grid()
    return plotter_strata


def create_stratigraphic_table(site_strata: list, strata_props_descriptions: list):
    """
    Create a stratigrahic table for the site similar to the international chronostratigraphic chart.
    @param site_strata: list of string that contains the name for each lithostratigraphic layer.
    @param strata_props_descriptions: list of string that
    @return: A stratigraphic table figure (icicle chart).
    """
    ids = ["Phanerozoic"]
    labels = ["Phanerozoic"]
    parents = [""]
    stratigraphy_colors = [hex_colors["Phanerozoic"]]

    d_k = 0
    ids_descriptions = ['']

    for strata in site_strata:
        strata_names = strata.split("-")
        root = "Phanerozoic"

        for i in range(len(strata_names)):
            id_name = "-".join(
                strata_names[: i + 1]
            )  # combining the name again using '-'
            if id_name not in ids:
                ids.append(id_name)
                try:
                    stratigraphy_colors.append(hex_colors[id_name])
                except KeyError:  # if the id_name is not within the international chronostratigraphic chart, then use
                    # its parents color.
                    stratigraphy_colors.append(stratigraphy_colors[-1])

                if id_name in site_strata:
                    ids_descriptions.append(strata_props_descriptions[d_k])
                    d_k += 1
                else:
                    ids_descriptions.append("")

                # add the splitted name
                labels.append(strata_names[i])

                parents.append(root)
            root = id_name  # hierarchy is divided by '-' and a root is always the id_name before '-'

    fig = go.Figure(
        go.Icicle(
            ids=ids,
            labels=labels,
            parents=parents,
            marker_colors=stratigraphy_colors,
            hovertext=ids_descriptions,
            textinfo="label+text",
            sort=False,
        )
    )

    stratigraphy_colors_dict = dict(zip(ids, stratigraphy_colors))
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    return fig, stratigraphy_colors_dict


def add_site_props_to_sites_dict(site_name: str, sites_material_props_dict: dict):
    """
    Add site material properties to the existing Python Dictionary sites_material_props_dict.
    @param site_name: str, name of the site
    @param sites_material_props_dict: dict, dictionary that contains all the sites material properties.
    @return: the updated sites_material_props_dict.
    """
    # convert YAML file to Python dictionary
    site_props_dict = load_items_in_dir(
        dir_name=os.path.join("site", site_name + ".yml"), items="site_props_dict"
    )
    # get a list of layer names
    site_strata_names_list = list(site_props_dict['properties'].keys())
    # store the site name and its layers names
    sites_material_props_dict.update(
        {site_name: {'strata': dict(zip(site_strata_names_list, site_strata_names_list))}}
    )
    # load property path, lithology, age and description
    for id_name in site_strata_names_list:
        site_props_dict_props_id = site_props_dict["properties"][id_name]
        # load default file name
        stratum_props_lithology = site_props_dict_props_id["lithology"]
        stratum_props_age = site_props_dict_props_id["age"]
        # load stratum file path and description
        stratum_props_file_path = site_props_dict_props_id["properties"]
        stratum_props_description = site_props_dict_props_id["description"]
        stratum_props_geometry_path = site_props_dict_props_id["geometry"]
        # store property path, default file name, and description into dictionary
        sites_material_props_dict[site_name]['strata'][id_name] = {
            "properties_file_path": stratum_props_file_path,
            "default_properties_file_name": stratum_props_age + "_" + stratum_props_lithology,
            "description": stratum_props_description,
            "geometry_file_path": stratum_props_geometry_path
        }
    return sites_material_props_dict


def add_stratum_table_to_sites_dict(site_name: str, id_name: str, sites_material_props_dict: dict):
    """
    Add stratum table to the existing Python Dictionary sites_material_props_dict.
    @param site_name: str, name of the site
    @param id_name: str, name of the lithostratigraphic layer.
    @param sites_material_props_dict: dict, dictionary that contains all the sites material properties.
    @return: the updated sites_material_props_dict.
    """
    # Load default file
    default_file_name = sites_material_props_dict[site_name]['strata'][id_name]["default_properties_file_name"]
    default_props = default_props_dict[default_file_name]

    # Load stratum props
    stratum_props_file_path = sites_material_props_dict[site_name]['strata'][id_name]["properties_file_path"]
    if stratum_props_file_path == "default":
        stratum_props = "default"
    else:
        # load stratum properties
        id_name_props_yaml = load_yaml_to_dict(stratum_props_file_path, props_yaml_to_dataframe=True)
        stratum_props = id_name_props_yaml["properties"]

    # fill in missing fields and properties with default
    stratum_props_table, style_default_data = fill_in_default_props(
        stratum_props, default_props
    )

    # convert dataframe to dash table
    stratum_props_table_to_records = stratum_props_table.to_dict("records")
    stratum_props_table_index = stratum_props_table.columns

    # store stratum properties into dictionary
    sites_material_props_dict[site_name]['strata'][id_name].update({"stratum_props": {
        "stratum_props_table": stratum_props_table_to_records,
        "stratum_props_table_index": stratum_props_table_index,
        "style_default_data": style_default_data}})

    return sites_material_props_dict


def load_dash_vtk_children(points_all, polys_all, stratum_colors, stratum_opacity):
    children_lists = [
        dash_vtk.GeometryRepresentation(
            children=[dash_vtk.PolyData(points=points_all[0], polys=polys_all[0])],
            property={"edgeVisibility": False, "color": stratum_colors[0], "opacity": stratum_opacity[0]},
            showCubeAxes=True,
        )
    ]
    for i in range(1, len(stratum_colors)):
        children_lists.append(
            dash_vtk.GeometryRepresentation(
                children=[dash_vtk.PolyData(points=points_all[i], polys=polys_all[i])],
                property={"edgeVisibility": False, "color": stratum_colors[i], "opacity": stratum_opacity[i]},
            ),
        )

    return children_lists


def load_dash_stratum_table(site_name: str, id_name: str, sites_material_props_dict: dict):
    stratum_props_table_to_records = sites_material_props_dict[site_name]['strata'][id_name]["stratum_props"][
        "stratum_props_table"]
    stratum_props_table_index = sites_material_props_dict[site_name]['strata'][id_name]["stratum_props"][
        "stratum_props_table_index"]
    style_default_data = sites_material_props_dict[site_name]['strata'][id_name]["stratum_props"][
        "style_default_data"]

    children = [
        html.Div(
            className="table_props",
            children=[
                dash_table.DataTable(
                    data=stratum_props_table_to_records,
                    columns=[{"name": i, "id": i} for i in stratum_props_table_index],
                    style_data_conditional=style_default_data,
                    filter_action="native",
                )
            ],
        )
    ]
    return children


hex_colors = RGBtxt_to_dict("RGB_stratigraphy.txt", color_type='to_hex')
rgb_colors = RGBtxt_to_dict("RGB_stratigraphy.txt", color_type='to_rgb')

site_dropdown_list = load_items_in_dir(dir_name="site", items="yml_files")
geometry_folder_list = load_items_in_dir(dir_name="geometry", items="folders")
default_props_dict = load_default_props()
app = Dash(external_stylesheets=["assets/dashboard.css"])
app.title = "Smart Data Hub"

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
                html.Div(
                    className="geomodel",
                    children=[
                        html.H1(
                            id="reset_camera",
                            className="geomodel_header",
                            children="3D Structural Geomodel",
                            style={"textAlign": "center", "color": "black"},
                        ),
                        html.Iframe(id="3d_model", className="iframe_geomodel")
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
                        dcc.Graph(id="icicle_props", className="icicle_stratigraphy"),
                        html.Div(id="properties_table"),
                    ],
                ),
            ],
        ),

        dcc.Store(id="sites_material_props_dict"),
        dcc.Store(id="site_name_previous"),
        dcc.Store(id="clicked_layer_name"),
        dcc.Store(id="plotter_plydata")
    ]
)


# change the value in state will not return output,  unless any input has changed
@app.callback(
    Output("icicle_props", "figure"),
    Output("sites_material_props_dict", "data"),
    Input("site_dropdown", "value"),
    State("sites_material_props_dict", "data"),
)
def display_stratigraphic_table(site_name, sites_material_props_dict):
    if site_name is None:  # assign initial value
        fig = go.Figure()
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        return fig, {}
    else:
        if site_name not in sites_material_props_dict:
            sites_material_props_dict = add_site_props_to_sites_dict(site_name, sites_material_props_dict)

        site_strata_names_list = list(sites_material_props_dict[site_name]['strata'].keys())
        strata_props_descriptions = [
            id_name.get("description")
            for id_name in sites_material_props_dict[site_name]['strata'].values()
        ]

        fig, stratigraphy_colors_dict = create_stratigraphic_table(
            site_strata_names_list, strata_props_descriptions
        )

        # store rgb colors for each stratum
        if 'stratum_colors_dict' not in sites_material_props_dict[site_name].keys():
            stratum_colors = [stratigraphy_colors_dict[id_name] for id_name in site_strata_names_list]
            stratum_colors_dict = dict(zip(site_strata_names_list, stratum_colors))
            sites_material_props_dict[site_name]['stratum_colors_dict'] = stratum_colors_dict

        return fig, sites_material_props_dict


@app.callback(
    Output("properties_table", "children"),
    Output("site_name_previous", "data"),
    Output("icicle_props", "clickData"),
    Output("clicked_layer_name", "data"),
    # Output("sites_material_props_dict", "data", allow_duplicate=True),
    Input("icicle_props", "clickData"),
    Input("sites_material_props_dict", "data"),
    Input("site_dropdown", "value"),
    State("site_name_previous", "data"),
    # prevent_initial_call=True
)
def load_stratum_table(
        click_data,
        sites_material_props_dict,
        site_name,
        site_name_previous,
):
    if click_data is None:
        dash_stratum_table = []  # hide the table
        clicked_layer_name = None

    else:  # display the properties table
        dash_stratum_table = []
        clicked_layer_name = click_data["points"][0]["id"]
        site_strata_names_list = list(sites_material_props_dict[site_name]['strata'].keys())
        # set the condition of site_name == site_name_previous to make sure the properties table
        # is hidden when site_name is updated.
        if clicked_layer_name in site_strata_names_list and site_name == site_name_previous:  # if properties for the layer exist
            # display the properties table
            # if "stratum_props" not in sites_material_props_dict[site_name]['strata'][id_name].keys():
            sites_material_props_dict = add_stratum_table_to_sites_dict(site_name, clicked_layer_name,
                                                                        sites_material_props_dict)
            dash_stratum_table = load_dash_stratum_table(site_name, clicked_layer_name, sites_material_props_dict)

    return dash_stratum_table, site_name, None, clicked_layer_name


@app.callback(
    Output("3d_model", "srcDoc"),
    Input("site_dropdown", "value"),
    Input("sites_material_props_dict", "data"),
    Input("clicked_layer_name", "data")
)
def display_3d_model(site_name, sites_material_props_dict, clicked_layer_name):
    if site_name is None:  # initial interface
        return None
    elif site_name not in geometry_folder_list:  # when no geomodel is available.
        return "No geomodel is available!"
    else:
        stratum_colors_dict = sites_material_props_dict[site_name][
            "stratum_colors_dict"
        ]
        plotter_plydata = load_plydata(
            site_name, sites_material_props_dict, stratum_colors_dict
        )
        plotter_plydata_names = list(plotter_plydata.renderer.actors.keys())

        # highlight the clicked layer
        if clicked_layer_name in plotter_plydata_names:
            for name, actor in plotter_plydata.renderer.actors.items():
                if name != clicked_layer_name:
                    actor.GetProperty().SetColor(211 / 255.0, 211 / 255.0, 211 / 255.0)
                    actor.GetProperty().SetOpacity(0.4)
        site_name_html = site_name + ".html"
        plotter_plydata.export_html(site_name_html)

        return open(site_name_html, "rt").read()


if __name__ == "__main__":
    app.run_server(debug=True)
