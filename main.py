import netgen.geom2d as geom2d
from netgen.meshing import Mesh, FaceDescriptor, MeshingParameters

# Define the geometry of a square domain [-3, 3] x [-3, 3]
geo = geom2d.SplineGeometry()

Brio = True
# Define points for the square boundary
p1 = geo.AppendPoint(-3.0, -3.0)  # Bottom-left
p2 = geo.AppendPoint(3.0, -3.0)   # Bottom-right
p3 = geo.AppendPoint(3.0, 3.0)    # Top-right
p4 = geo.AppendPoint(-3.0, 3.0)   # Top-left
refinement_steps = 5  # Number of refinement steps
maxh = 0.2
if Brio:
    p1 = geo.AppendPoint(0.0, 0.0)  # Bottom-left
    p2 = geo.AppendPoint(1.0, 0.0)   # Bottom-right
    p3 = geo.AppendPoint(1.0, 0.1)    # Top-right
    p4 = geo.AppendPoint(0.0, 0.1)   # Top-left
    maxh = 0.009  # Maximum element size
    refinement_steps = 10  # Number of refinement steps

# Add boundary edges
geo.Append(["line", p1, p2], bc="bottom")  # Bottom edge
geo.Append(["line", p2, p3], bc="right")  # Right edge
geo.Append(["line", p3, p4], bc="top")  # Top edge
geo.Append(["line", p4, p1], bc="left")  # Left edge

# Generate the mesh
print("Starting to generate mesh...")

ng_params = MeshingParameters(maxh=maxh, closeedges = True, optimize=True, delaunay2d = False, optsteps2d = 1000,elsizeweight = 0.3, segmentsperedge=10)

mesh = geo.GenerateMesh(ng_params)
mesh.dim = 2

# Add material descriptor
# mesh.Add(FaceDescriptor(surfnr=1, domin=1, bc=1))
# mesh.SetMaterial(1, "mat")
#
# # Assign boundary conditions manually
# for boundary_edge in mesh.Elements1D():
#     vertices = boundary_edge.vertices
#     boundary_edge.index = 1  # Assign boundary condition index for these edges

# Apply mesh refinement for better quality

for el in mesh.Elements2D():
    if len([edge for edge in mesh.GetEdges(el) if mesh.GetBC(edge) != 0]) >= 2:
        mesh.DeleteElement(el)
mesh.Compress()
mesh.Refine()
# mesh.OptimizeMesh2d()
# for _ in range(refinement_steps):
mesh.OptimizeMesh2d(ng_params)


# Export the mesh to a file
filename = "mesh.txt"
with open(filename, 'w') as f:
    # Export nodes
    f.write("$Nodes\n")
    f.write(f"{len(mesh.Points())}\n")  # Number of vertices
    for i, point in enumerate(mesh.Points(), start=1):
        x, y, z = point.p
        f.write(f"{i} {x} {y} 0.0\n")
    f.write("$EndNodes\n")

    # Export elements
    f.write("$Elements\n")
    f.write(f"{len(mesh.Elements2D())}\n")  # Number of 2D elements
    for j, element in enumerate(mesh.Elements2D(), start=1):
        vertices = " ".join(map(str, element.vertices))
        f.write(f"{j} {len(element.vertices)} {vertices}\n")
    f.write("$EndElements\n")

print(f"Mesh exported to {filename}")
print("All done!")