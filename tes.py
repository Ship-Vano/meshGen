import gmsh
import numpy as np

gmsh.initialize()

# Define the spline points (example: a simple closed curve)
spline_points = [
    [0.0, 0.0, 0.0],  # Point 1
    [1.0, 0.5, 0.0],   # Point 2
    [1.5, 1.5, 0.0],   # Point 3
    [1.0, 2.5, 0.0],   # Point 4
    [0.0, 3.0, 0.0],   # Point 5
    [-1.0, 2.5, 0.0],  # Point 6
    [-1.5, 1.5, 0.0],  # Point 7
    [-1.0, 0.5, 0.0],  # Point 8
    [0.0, 0.0, 0.0]    # Close the loop
]

# Add points to the geometry
point_tags = [gmsh.model.geo.add_point(x, y, z) for x, y, z in spline_points]

# Add splines connecting the points
spline_tags = []
for i in range(len(point_tags) - 1):
    spline_tags.append(gmsh.model.geo.add_spline([point_tags[i], point_tags[i + 1]]))

# Close the loop
curve_loop = gmsh.model.geo.add_curve_loop(spline_tags)

# Create a surface from the curve loop
surface = gmsh.model.geo.add_plane_surface([curve_loop])

# Synchronize the geometry
gmsh.model.geo.synchronize()

# Set mesh size (smaller size for equilateral triangles)
lc = 0.1
gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc)
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc)

# Set meshing algorithm to Frontal-Delaunay
gmsh.option.setNumber("Mesh.Algorithm", 6)  # 6 = Frontal-Delaunay

# Generate 2D mesh
gmsh.model.mesh.generate(2)

# Optimize the mesh
gmsh.model.mesh.optimize("Netgen")
gmsh.model.mesh.optimize("HighOrder")
gmsh.model.mesh.optimize("Laplace2D")

# View the mesh in the GMSH GUI
gmsh.fltk.run()

# Finalize GMSH
gmsh.finalize()