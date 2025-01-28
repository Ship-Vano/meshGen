import netgen.geom2d as geom2d
from netgen.meshing import Mesh, FaceDescriptor

# Define the geometry of a square domain [-3, 3] x [-3, 3]
geo = geom2d.SplineGeometry()

# Define points for the square boundary
# p1 = geo.AppendPoint(-3.0, -3.0)  # Bottom-left
# p2 = geo.AppendPoint(3.0, -3.0)   # Bottom-right
# p3 = geo.AppendPoint(3.0, 3.0)    # Top-right
# p4 = geo.AppendPoint(-3.0, 3.0)   # Top-left

p1 = geo.AppendPoint(0.0, 0.0)  # Bottom-left
p2 = geo.AppendPoint(1.0, 0.0)   # Bottom-right
p3 = geo.AppendPoint(1.0, 0.01)    # Top-right
p4 = geo.AppendPoint(0.0, 0.01)   # Top-left

# Add boundary edges
geo.Append(["line", p1, p2])  # Bottom edge
geo.Append(["line", p2, p3])  # Right edge
geo.Append(["line", p3, p4])  # Top edge
geo.Append(["line", p4, p1])  # Left edge

# Generate the mesh
print("Starting to generate mesh...")
maxh = 0.009  # Maximum element size
mesh = geo.GenerateMesh(maxh=maxh)
mesh.dim = 2

# Add material descriptor
mesh.Add(FaceDescriptor(surfnr=1, domin=1, bc=1))
mesh.SetMaterial(1, "mat")

# Assign boundary conditions manually
for boundary_edge in mesh.Elements1D():
    vertices = boundary_edge.vertices
    boundary_edge.index = 1  # Assign boundary condition index for these edges

# Apply mesh refinement for better quality
refinement_steps = 3  # Number of refinement steps
for _ in range(refinement_steps):
    mesh.Refine()

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