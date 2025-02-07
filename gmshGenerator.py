import gmsh
import sys

gmsh.initialize()

# Set global mesh size (optional)
lc = 1e-2
gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc)
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc)

# Create geometry (your original code)
point1 = gmsh.model.geo.add_point(0.0, 0.0, 0.0, lc)
point2 = gmsh.model.geo.add_point(1.0, 0.0, 0.0, lc)
point3 = gmsh.model.geo.add_point(1.0, 0.1, 0.0, lc)
point4 = gmsh.model.geo.add_point(0.0, 0.1, 0, lc)

line1 = gmsh.model.geo.add_line(point1, point2)
line2 = gmsh.model.geo.add_line(point2, point3)
line3 = gmsh.model.geo.add_line(point3, point4)
line4 = gmsh.model.geo.add_line(point4, point1)

face1 = gmsh.model.geo.add_curve_loop([line1, line2, line3, line4])
gmsh.model.geo.add_plane_surface([face1])

gmsh.model.geo.synchronize()

# Set meshing algorithm to Frontal-Delaunay (better for triangles)
gmsh.option.setNumber("Mesh.Algorithm", 6)  # 6 = Frontal-Delaunay

# Generate initial mesh
gmsh.model.mesh.generate(2)

# Optimize the mesh for equilateral triangles
gmsh.option.setNumber("Mesh.Smoothing", 100)  # Increase smoothing steps
gmsh.option.setNumber("Mesh.OptimizeNetgen", 1)  # Enable Netgen optimization

# Run optimization steps (combine multiple methods)
gmsh.model.mesh.optimize("Netgen")  # Use Netgen optimization
gmsh.model.mesh.optimize("HighOrder")  # Additional smoothing
gmsh.model.mesh.optimize("Laplace2D")  # Laplace smoothing

# Save and view the mesh
gmsh.write("optimized_mesh.msh")
gmsh.fltk.run()
gmsh.finalize()