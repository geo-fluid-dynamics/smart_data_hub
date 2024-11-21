import os
import pandas as pd
import gempy as gp
import pyvista as pv
import numpy as np


def create_geomodel_for_site(site_orientation_path: str, site_points_path: str, save_ply_folder_path: str = ''):
    """
    Create GemPy 3D structural model and save each surface mesh to PolyData
    @param site_orientation_path: path to CSV file that stores orientation data for each surface.
    @param site_points_path: path to CSV file that stores point data for each surface.
    @param save_ply_folder_path: path to a folder that saves the PolyData.
    @return: PolyData for each surface.
    """

    points_csv = pd.read_csv(site_points_path)
    # get strata name list
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
        project_name="site",
        extent=extent_geometry,
        refinement=4,
        importer_helper=gp.data.ImporterHelper(
            path_to_orientations=site_orientation_path,
            path_to_surface_points=site_points_path,
        ),
    )
    surface_data = gp.map_stack_to_surfaces(geo_data, formation_dict)

    # Compute the geological model
    data_model = gp.compute_model(geo_data)
    geo_model = geo_data

    print("created the 3D structural model!")
    # Get vertices and edges for each surface
    surface_meshes_vertices = [
        geo_model.input_transform.apply_inverse(mesh.vertices)
        for mesh in geo_model.solutions.dc_meshes
    ]
    surface_meshes_edges = [mesh.edges for mesh in geo_model.solutions.dc_meshes]

    #
    for i in range(len(surface_meshes_vertices)):
        surface_mesh = pv.PolyData(
            surface_meshes_vertices[i],
            np.insert(surface_meshes_edges[i], 0, 3, axis=1).ravel(),
        )
        surface_mesh.save(os.path.join(save_ply_folder_path, f"{formation_list[i]}.ply"))
        print(f"Saved {formation_list[i]}.ply !")
