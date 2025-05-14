import gmsh
import numpy as np
from math import sqrt

gmsh.initialize()

taskType = 1

if taskType == 1:
    N = 100
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

gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc*0.01)
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc)



gmsh.model.geo.synchronize()

# Set meshing algorithm to Frontal-Delaunay
gmsh.option.setNumber("Mesh.Algorithm", 6)  # 6 = Frontal-Delaunay, 1=MeshAdapt, 5=Delaunay

# Generate and optimize mesh
gmsh.model.mesh.generate(2)
# for _ in range(100):
#     # gmsh.model.mesh.optimize("Netgen")
#     gmsh.model.mesh.optimize("Relocate2D", force=True)
#     gmsh.model.mesh.optimize("Laplace2D")


# Get all nodes and their coordinates
node_tags, coords, _ = gmsh.model.mesh.getNodes()
coords = np.array(coords).reshape(-1, 3)  # Reshape properly

# Map Gmsh node tags to 1-based indices
node_indices = {tag: idx + 1 for idx, tag in enumerate(node_tags)}

# Get all triangular elements (type 2 in Gmsh)
elem_tags, elem_node_tags = gmsh.model.mesh.getElementsByType(2)
elem_node_tags = list(zip(*[iter(elem_node_tags)] * 3))  # Safe grouping

# Export to .txt
filename = f"fem_mesh{taskType}.txt"
with open(filename, "w") as f:
    # Write nodes
    f.write("$Nodes\n")
    f.write(f"{len(node_tags)}\n")
    for tag, (x, y, z) in zip(node_tags, coords):
        f.write(f"{node_indices[tag]} {x:.6f} {y:.6f} 0.0\n")  # Force z=0.0 for 2D
    f.write("$EndNodes\n")

    # Write elements
    f.write("$Elements\n")
    f.write(f"{len(elem_tags)}\n")
    for elem_idx, nodes in enumerate(elem_node_tags, 1):
        mapped_nodes = [node_indices[tag] for tag in nodes]
        f.write(f"{elem_idx} 3 {' '.join(map(str, mapped_nodes))}\n")
    f.write("$EndElements\n")

print(f"Info    : Mesh exported to {filename}")

# Show mesh in GUI
gmsh.fltk.run()
gmsh.finalize()
