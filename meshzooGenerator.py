import gmsh
import numpy as np
from math import sqrt
gmsh.initialize()

# Set global mesh size (optional)



taskType = 1
lc = 1e-3
# Create geometry
if taskType == 1:
    N = 500
    lc = 2 / (N * sqrt(3))
    point1 = gmsh.model.geo.add_point(0.0, 0.0, 0.0, lc)
    point2 = gmsh.model.geo.add_point(1.0, 0.0, 0.0, lc)
    point3 = gmsh.model.geo.add_point(1.0, 1.0, 0.0, lc)
    point4 = gmsh.model.geo.add_point(0.0, 1.0, 0.0, lc)
    line1 = gmsh.model.geo.add_line(point1, point2)
    line2 = gmsh.model.geo.add_line(point2, point3)
    line3 = gmsh.model.geo.add_line(point3, point4)
    line4 = gmsh.model.geo.add_line(point4, point1)
    gmsh.model.geo.add_curve_loop([line1, line2, line3, line4])
    face1 = gmsh.model.geo.add_curve_loop([line1, line2, line3, line4])
    gmsh.model.geo.add_plane_surface([face1])

elif taskType == 2:
    lc = 1e-1
    point1 = gmsh.model.geo.add_point(-3.0, -3.0, 0.0, lc)
    point2 = gmsh.model.geo.add_point(3.0, -3.0, 0.0, lc)
    point3 = gmsh.model.geo.add_point(3.0, 3.0, 0.0, lc)
    point4 = gmsh.model.geo.add_point(-3.0, 3.0, 0.0, lc)
    line1 = gmsh.model.geo.add_line(point1, point2)
    line2 = gmsh.model.geo.add_line(point2, point3)
    line3 = gmsh.model.geo.add_line(point3, point4)
    line4 = gmsh.model.geo.add_line(point4, point1)
    gmsh.model.geo.add_curve_loop([line1, line2, line3, line4])
    face1 = gmsh.model.geo.add_curve_loop([line1, line2, line3, line4])
    gmsh.model.geo.add_plane_surface([face1])

elif taskType == 4:
    lc = 6e-3
    point1 = gmsh.model.geo.add_point(0.0, 0.0, 0.0, lc)
    point2 = gmsh.model.geo.add_point(1.0, 0.0, 0.0, lc)
    point3 = gmsh.model.geo.add_point(1.0, 1.0, 0.0, lc)
    point4 = gmsh.model.geo.add_point(0.0, 1.0, 0.0, lc)
    line1 = gmsh.model.geo.add_line(point1, point2)
    line2 = gmsh.model.geo.add_line(point2, point3)
    line3 = gmsh.model.geo.add_line(point3, point4)
    line4 = gmsh.model.geo.add_line(point4, point1)
    gmsh.model.geo.add_curve_loop([line1, line2, line3, line4])
    face1 = gmsh.model.geo.add_curve_loop([line1, line2, line3, line4])
    gmsh.model.geo.add_plane_surface([face1])

gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc*0.01)
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc+0.0001)



gmsh.model.geo.synchronize()

# Set meshing algorithm to Frontal-Delaunay
gmsh.option.setNumber("Mesh.Algorithm", 6)  # 6 = Frontal-Delaunay, 1=MeshAdapt, 5=Delaunay

# Generate and optimize mesh
gmsh.model.mesh.generate(2)

# ===== CROP MESH BETWEEN x_min/x_max AND y_min/y_max =====
x_min = 0.4  # Lower x bound (adjust as needed)
x_max = 0.6  # Upper x bound (adjust as needed)
y_min = -1.0  # Lower y bound (adjust as needed)
y_max = 2.0  # Upper y bound (adjust as needed)

# Get nodes and filter
node_tags, coords, _ = gmsh.model.mesh.getNodes()
node_tags = np.array(node_tags)
coords = np.array(coords).reshape(-1, 3)

# Keep nodes within x and y bounds
keep_mask = (
        (coords[:, 0] >= x_min) &
        (coords[:, 0] <= x_max) &
        (coords[:, 1] >= y_min) &
        (coords[:, 1] <= y_max)
)
kept_node_tags = node_tags[keep_mask]
kept_coords = coords[keep_mask]

# Create new node index mapping
new_node_indices = {tag: idx + 1 for idx, tag in enumerate(kept_node_tags)}

# Get elements and filter
_, elem_node_tags = gmsh.model.mesh.getElementsByType(2)
elem_node_tags = np.array(elem_node_tags).reshape(-1, 3)

# Keep elements where all nodes are within bounds
kept_nodes_set = set(kept_node_tags)
valid_elements = [elem for elem in elem_node_tags if all(node in kept_nodes_set for node in elem)]

# Map element nodes to new indices
valid_elements_mapped = [[new_node_indices[node] for node in elem] for elem in valid_elements]

# Export cropped mesh
filename = f"meshBrio.txt"
with open(filename, "w") as f:
    # Nodes
    f.write("$Nodes\n")
    f.write(f"{len(kept_node_tags)}\n")
    for tag, (x, y, z) in zip(kept_node_tags, kept_coords):
        f.write(f"{new_node_indices[tag]} {x:.6f} {y:.6f} 0.0\n")
    f.write("$EndNodes\n")

    # Elements
    f.write("$Elements\n")
    f.write(f"{len(valid_elements)}\n")
    for idx, nodes in enumerate(valid_elements_mapped, 1):
        f.write(f"{idx} 3 {' '.join(map(str, nodes))}\n")
    f.write("$EndElements\n")

print(f"Info    : Cropped mesh saved to {filename}")

# Show mesh in GUI
gmsh.fltk.run()
gmsh.finalize()