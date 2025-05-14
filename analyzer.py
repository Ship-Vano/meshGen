import numpy as np
import pyvista as pv
from scipy.interpolate import griddata
import math


def load_vtu(filename, data_field='elemUs'):
    """
    Loads a VTU file using PyVista and returns the cell-center coordinates
    along with the cell data for the given field.

    Parameters:
        filename (str): Path to the VTU file.
        data_field (str): Name of the cell data array (here, "elemUs").

    Returns:
        points (np.ndarray): An array of shape (n_cells, 3) with the cell centers.
        values (np.ndarray): An array of shape (n_cells, n_vars) with the state data.
    """
    mesh = pv.read(filename)
    # Compute cell centers (centroids) of the elements
    cell_centers = mesh.cell_centers()
    points = cell_centers.points  # shape: (n_cells, 3)

    # Try to get the cell data from the cell centers; if not available, try the mesh
    if data_field in cell_centers.cell_data:
        values = cell_centers.cell_data[data_field]
    elif data_field in mesh.cell_data:
        values = mesh.cell_data[data_field]
    else:
        raise ValueError(f"Data field '{data_field}' not found in {filename}.")

    return points, values


def remove_constant_dims(points, tol=1e-14):
    """
    Removes dimensions in which the variation is negligible.

    Parameters:
        points (np.ndarray): Array of point coordinates.
        tol (float): Tolerance for variation.

    Returns:
        points_reduced (np.ndarray): Reduced point array (only dimensions with variation).
        keep (np.ndarray): Indices of the kept dimensions.
    """
    ranges = np.ptp(points, axis=0)  # peak-to-peak (max-min) along each coordinate
    keep = np.where(ranges > tol)[0]
    return points[:, keep], keep


def compute_relative_error(coarse_points, coarse_values, fine_points, fine_values, var_index):
    """
    Computes the relative error for a single component (specified by var_index)
    using the formula:

        δ(ψ) = sum(|ψ_coarse - ψ_fine_interp|) / sum(|ψ_fine_interp|)

    where ψ_fine_interp is the fine solution interpolated at the coarse cell centers.

    Parameters:
        coarse_points (np.ndarray): Coordinates of coarse mesh cell centers.
        coarse_values (np.ndarray): Coarse mesh state data.
        fine_points (np.ndarray): Coordinates of fine mesh cell centers.
        fine_values (np.ndarray): Fine mesh state data.
        var_index (int): Index of the component (e.g., 2 for v).

    Returns:
        rel_error (float): The computed relative error.
    """
    # Combine points to find dimensions to keep based on both meshes
    combined_points = np.vstack((coarse_points, fine_points))
    combined_pts_red, keep_idx = remove_constant_dims(combined_points, tol=1e-12)

    # Reduce dimensions for both meshes using the same keep indices
    coarse_pts_red = coarse_points[:, keep_idx]
    fine_pts_red = fine_points[:, keep_idx]

    psi_coarse = coarse_values[:, var_index]
    psi_fine = fine_values[:, var_index]

    # Interpolate the fine solution onto the coarse points.
    psi_fine_interp = griddata(fine_pts_red, psi_fine, coarse_pts_red, method='linear')

    # Fill remaining NaNs with nearest neighbor interpolation
    nan_idx = np.isnan(psi_fine_interp)
    if np.any(nan_idx):
        psi_fine_interp[nan_idx] = griddata(fine_pts_red, psi_fine, coarse_pts_red[nan_idx], method='nearest')

    # Calculate sums
    error_sum = np.sum(np.abs(psi_coarse - psi_fine_interp))
    abs_sum = np.sum(np.abs(psi_fine_interp))

    # Handle division by zero
    return error_sum / abs_sum if abs_sum != 0 else np.nan

def analyze_errors(mesh_files, fine_file):
    """
    For each coarse mesh VTU file, computes the average relative error
    for the variables v (index 2), w (index 3), and B_y (index 6) with
    respect to the fine solution.

    Also computes convergence rates between successive coarse resolutions.

    Parameters:
        mesh_files (dict): Mapping of a mesh identifier (e.g., 50, 100, 200)
                           to the filename of the coarse VTU file.
        fine_file (str): Filename of the fine solution VTU file.
    """
    # Load the fine (exact) solution.
    fine_points, fine_values = load_vtu(fine_file, data_field='elemUs')

    errors = {}
    print("Relative Errors:")
    # For each coarse mesh, compute errors for the three variables and average them.
    for res, fname in sorted(mesh_files.items()):
        coarse_points, coarse_values = load_vtu(fname, data_field='elemUs')

        # Compute errors for v (index 2), w (index 3), and B_y (index 6)
        err_v = compute_relative_error(coarse_points, coarse_values, fine_points, fine_values, 2)
        err_w = compute_relative_error(coarse_points, coarse_values, fine_points, fine_values, 3)
        err_By = compute_relative_error(coarse_points, coarse_values, fine_points, fine_values, 6)

        avg_err = (err_v + err_w + err_By) / 3.0
        errors[res] = avg_err
        print(f"  Mesh {res:3d}: δ_{res} = {avg_err:.4e}")

    # Compute convergence rates R_N = log2(δ_{N_previous}/δ_N)
    print("\nConvergence Rates:")
    sorted_res = sorted(errors.keys())
    for i in range(1, len(sorted_res)):
        res_prev = sorted_res[i - 1]
        res_curr = sorted_res[i]
        if errors[res_curr] == 0:
            rate = float('nan')
        else:
            rate = math.log2(errors[res_prev] / errors[res_curr])
        print(f"  From Mesh {res_prev:3d} to Mesh {res_curr:3d}: R = {rate:.4f}")



# Define your coarse mesh files.
mesh_files = {
        50: "mesh5_50.vtu",
        100: "mesh5_100.vtu",
        200: "mesh5_200.vtu"
}
# Fine solution file (assumed to be the "exact" solution)
fine_file = "mesh5_400.vtu"

analyze_errors(mesh_files, fine_file)