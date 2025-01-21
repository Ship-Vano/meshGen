import netgen.geom2d as geom2d
geo = geom2d.SplineGeometry()
# узловые точки квадратной области
p1 = geo.AppendPoint (0,0)
p2 = geo.AppendPoint (1,0)
p3 = geo.AppendPoint (0,0.01)
p4 = geo.AppendPoint (1,0.01)
# граница области
geo.Append (["line", p1, p2])
geo.Append (["line", p2, p3])
geo.Append (["line", p3, p4])
geo.Append (["line", p4, p1])
# генерация сетки
mesh = geo.GenerateMesh(maxh=0.01)
mesh.Refine()
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