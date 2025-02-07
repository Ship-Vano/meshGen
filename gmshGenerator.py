import gmsh
import sys

gmsh.initialize()

# Set global mesh size (optional)
lc = 1e-2
gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc)
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc)

Brio = True

# Create geometry (your original code)

if Brio:
    point1 = gmsh.model.geo.add_point(0.0, 0.0, 0.0, lc)
    point2 = gmsh.model.geo.add_point(1.0, 0.0, 0.0, lc)
    point3 = gmsh.model.geo.add_point(1.0, 0.1, 0.0, lc)
    point4 = gmsh.model.geo.add_point(0.0, 0.1, 0, lc)
else:
    point1 = gmsh.model.geo.add_point(0.0, 0.0, 0.0, lc)
    point2 = gmsh.model.geo.add_point(3.0, 0.0, 0.0, lc)
    point3 = gmsh.model.geo.add_point(3.0, 3.0, 0.0, lc)
    point4 = gmsh.model.geo.add_point(0.0, 3.0, 0, lc)

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



# Get all nodes and their coordinates
node_tags, coords, _ = gmsh.model.mesh.getNodes()
coords = coords.reshape(-1, 3)  # Reshape to (N, 3) array

# Create a mapping from Gmsh node tags to 1-based indices
node_indices = {tag: idx + 1 for idx, tag in enumerate(node_tags)}

# Get all triangular elements (type 2 in Gmsh)
elem_tags, elem_node_tags = gmsh.model.mesh.getElementsByType(2)
elem_node_tags = elem_node_tags.reshape(-1, 3)  # Reshape to (M, 3) array

# Export to your custom format
filename = "mesh.txt"
with open(filename, "w") as f:
    # Write nodes
    f.write("$Nodes\n")
    f.write(f"{len(node_tags)}\n")
    for tag, (x, y, z) in zip(node_tags, coords):
        f.write(f"{node_indices[tag]} {x} {y} 0.0\n")  # Force z=0.0 for 2D
    f.write("$EndNodes\n")

    # Write elements
    f.write("$Elements\n")
    f.write(f"{len(elem_tags)}\n")
    for elem_idx, nodes in enumerate(elem_node_tags, 1):
        # Map Gmsh node tags to your custom indices
        mapped_nodes = [node_indices[tag] for tag in nodes]
        f.write(f"{elem_idx} {' '.join(map(str, mapped_nodes))}\n")
    f.write("$EndElements\n")

print(f"Info    : Mesh exported to {filename}")


#gmsh.write("optimized_mesh.msh")
gmsh.fltk.run()
gmsh.finalize()
