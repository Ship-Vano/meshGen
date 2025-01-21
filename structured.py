from netgen.geom2d import unit_square, MakeCircle, SplineGeometry
from netgen.meshing import Element0D, Element1D, Element2D, MeshPoint, FaceDescriptor, Mesh
from netgen.csg import Pnt

quads = False
N=250

mesh = Mesh()
mesh.SetGeometry(unit_square)
mesh.dim = 2

pnums = []
for i in range(N + 1):
    for j in range(N + 1):
        pnums.append(mesh.Add(MeshPoint(Pnt(i / N, j / N, 0))))

mesh.Add (FaceDescriptor(surfnr=1,domin=1,bc=1))
mesh.SetMaterial(1, "mat")
for j in range(N):
    for i in range(N):
        if quads:
            mesh.Add(Element2D(1, [pnums[i + j * (N + 1)], pnums[i + (j + 1) * (N + 1)], pnums[i + 1 + (j + 1) * (N + 1)], pnums[i + 1 + j * (N + 1)]]))
        else:
            mesh.Add(Element2D(1, [pnums[i + j * (N + 1)], pnums[i + (j + 1) * (N + 1)], pnums[i + 1 + j * (N + 1)]]))
            mesh.Add(Element2D(1, [pnums[i + (j + 1) * (N + 1)], pnums[i + 1 + (j + 1) * (N + 1)], pnums[i + 1 + j * (N + 1)]]))




# экспорт
filename = "mesh.txt"
with open(filename, 'w') as f:
    f.write(f"$Nodes\n")
    f.write(f"{len(mesh.Points())}\n") #number of vertices
    i = 1
    for p in mesh.Points():
        x,y,z = p.p
        f.write(f"{i} {x} {y} 0.0\n")
        i += 1
    f.write(f"$EndNodes\n")
    f.write(f"$Elements\n")
    f.write(f"{len(mesh.Elements2D())}\n")
    elements = str(mesh.Elements2D()).split("\n")
    j = 0
    separator = " "
    for el in mesh.Elements2D():
        f.write(f"{j} {len(el.vertices)} {separator.join(map(str, el.vertices))}\n")
        j += 1
    f.write(f"$EndElements\n")
print(f"Mesh exported to {filename}")

print("all right!")
