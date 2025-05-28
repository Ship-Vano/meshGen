import os


# Генерация твёрдой ванны (3D)
def generate_solid_3d_init(path, w=50, h=50, d=50,
                           wall_thickness=4, floor_thickness=4):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(f"S {w} {h} {d}\n")
        for k in range(d):
            for j in range(h):
                for i in range(w):
                    # Проверяем все границы: боковые стенки, пол и потолок
                    if (i < wall_thickness or i >= w - wall_thickness or
                            k < wall_thickness or k >= d - wall_thickness or
                            j >= h - floor_thickness):
                        phi = -1.0
                    else:
                        phi = 1.0
                    f.write(f"{phi:.6f} ")
                f.write("\n")


# Генерация прямоугольного распределения жидкости (3D)
def generate_fluid_rectangle_3d_init(path, w=50, h=50, d=50,
                                     wall_thickness=4, floor_thickness=4,
                                     fill_width_frac=1.0,
                                     fill_depth_frac=1.0,
                                     fill_height_frac=0.4):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    interior_width = w - 2 * wall_thickness
    interior_depth = d - 2 * wall_thickness
    interior_height = h - floor_thickness

    x_end = wall_thickness + int(fill_width_frac * interior_width)
    z_end = wall_thickness + int(fill_depth_frac * interior_depth)
    y_start = int((1.0 - fill_height_frac) * interior_height)

    with open(path, 'w') as f:
        f.write(f"F {w} {h} {d}\n")
        for k in range(d):
            for j in range(h):
                for i in range(w):
                    in_x = (i >= wall_thickness and i < x_end)
                    in_z = (k >= wall_thickness and k < z_end)
                    in_y = (j >= y_start and j < interior_height)
                    phi = -1.0 if (in_x and in_z and in_y) else 1.0
                    f.write(f"{phi:.6f} ")
                f.write("\n")


# Генерация жидкости с шаром (3D)
def generate_fluid_with_sphere_3d_init(path, w=50, h=50, d=50,
                                       wall_thickness=4, floor_thickness=4,
                                       fill_width_frac=1.0,
                                       fill_depth_frac=1.0,
                                       fill_height_frac=0.4,
                                       sphere_center_frac=(0.5, 0.2, 0.5),
                                       sphere_radius_frac=0.1):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    interior_width = w - 2 * wall_thickness
    interior_depth = d - 2 * wall_thickness
    interior_height = h - floor_thickness

    # Прямоугольная часть
    x_end = wall_thickness + int(fill_width_frac * interior_width)
    z_end = wall_thickness + int(fill_depth_frac * interior_depth)
    y_start = int((1.0 - fill_height_frac) * interior_height)

    # Сфера
    cx = wall_thickness + sphere_center_frac[0] * interior_width
    cy = sphere_center_frac[1] * interior_height
    cz = wall_thickness + sphere_center_frac[2] * interior_depth
    r = sphere_radius_frac * min(interior_width, interior_height, interior_depth)

    with open(path, 'w') as f:
        f.write(f"F {w} {h} {d}\n")
        for k in range(d):
            for j in range(h):
                for i in range(w):
                    # Прямоугольник
                    in_rect = (
                            i >= wall_thickness and i < x_end and
                            k >= wall_thickness and k < z_end and
                            j >= y_start and j < interior_height
                    )
                    # Сфера
                    dx = i - cx
                    dy = j - cy
                    dz = k - cz
                    in_sphere = (dx * dx + dy * dy + dz * dz <= r * r)

                    phi = -1.0 if (in_rect or in_sphere) else 1.0
                    f.write(f"{phi:.6f} ")
                f.write("\n")


# Генерация комбинированных меток (3D)
def generate_combined_labels_3d(solid_path, fluid_path, output_path):
    # Чтение solid данных
    with open(solid_path, 'r') as f_solid:
        header_solid = f_solid.readline().split()
        w = int(header_solid[1])
        h = int(header_solid[2])
        d = int(header_solid[3])
        solid_data = []
        for _ in range(d * h):
            line = f_solid.readline()
            solid_data.extend(map(float, line.split()))

    # Чтение fluid данных
    with open(fluid_path, 'r') as f_fluid:
        header_fluid = f_fluid.readline().split()
        fluid_data = []
        for _ in range(d * h):
            line = f_fluid.readline()
            fluid_data.extend(map(float, line.split()))

    # Генерация меток
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f_out:
        f_out.write(f"{w} {h} {d}\n")
        total_cells = w * h * d
        for idx in range(total_cells):
            if solid_data[idx] < 0:
                f_out.write("S")
            elif fluid_data[idx] < 0:
                f_out.write("F")
            else:
                f_out.write("A")

            # Добавляем пробелы и переводы строк
            if (idx + 1) % w == 0:
                if (idx // w) % h == h - 1:
                    f_out.write("\n\n")  # Разделение слоев
                else:
                    f_out.write("\n")
            else:
                f_out.write(" ")


# Пример генерации тестов
def generate_3d_tests():
    w, h, d = 50, 50, 50

    # Солид-ванна
    generate_solid_3d_init('res/solid_3d_init.txt', w, h, d)

    # Прямоугольный слой
    generate_fluid_rectangle_3d_init('res/fluid_3d_rect.txt', w, h, d,
                                     fill_height_frac=0.3)

    # Узкий столб
    generate_fluid_rectangle_3d_init('res/fluid_3d_column.txt', w, h, d,
                                     fill_width_frac=0.3,
                                     fill_depth_frac=0.3,
                                     fill_height_frac=0.5)

    # Слой + сфера
    generate_fluid_with_sphere_3d_init('res/fluid_3d_sphere.txt', w, h, d,
                                       fill_height_frac=0.3,
                                       sphere_center_frac=(0.5, 0.5, 0.5),
                                       sphere_radius_frac=0.15)

    # Генерация меток
    generate_combined_labels_3d('res/solid_3d_init.txt',
                                'res/fluid_3d_rect.txt',
                                'res/labels_3d_rect.txt')

    generate_combined_labels_3d('res/solid_3d_init.txt',
                                'res/fluid_3d_column.txt',
                                'res/labels_3d_column.txt')

    generate_combined_labels_3d('res/solid_3d_init.txt',
                                'res/fluid_3d_sphere.txt',
                                'res/labels_3d_sphere.txt')


generate_3d_tests()