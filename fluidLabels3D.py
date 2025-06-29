import os
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LightSource

# Параметры корыта
L = 1.0
BEACH_X = 0.2
BEACH_Z = 0.1


def sqr(x):
    return x * x

# Функция высоты дна (батиметрия)
def bathymetry(x, z):
    """Возвращает высоту дна в точке (x, z)"""
    if x < 1.5 * BEACH_X:
        if z < 1.5 * BEACH_X:
            return (10.0/9.0) * (sqr(x - 1.5*BEACH_X) + sqr(z - 1.5*BEACH_X)) - BEACH_Z
        elif z < L - 1.5*BEACH_X:
            return (10.0/9.0) * sqr(x - 1.5*BEACH_X) - BEACH_Z
        else:  # z >= L - 1.5*BEACH_X
            return (10.0/9.0) * (sqr(x - 1.5*BEACH_X) + sqr(z - (L-1.5*BEACH_X))) - BEACH_Z
    elif x < L - 1.5*BEACH_X:
        if z < 1.5*BEACH_X:
            return (10.0/9.0) * sqr(z - 1.5*BEACH_X) - BEACH_Z
        elif z < L - 1.5*BEACH_X:
            return -BEACH_Z
        else:  # z >= L - 1.5*BEACH_X
            return (10.0/9.0) * sqr(z - (L-1.5*BEACH_X)) - BEACH_Z
    else:  # x >= L - 1.5*BEACH_X
        if z < 1.5*BEACH_X:
            return (10.0/9.0) * (sqr(x - (L-1.5*BEACH_X)) + sqr(z - 1.5*BEACH_X)) - BEACH_Z
        elif z < L - 1.5*BEACH_X:
            return (10.0/9.0) * sqr(x - (L-1.5*BEACH_X)) - BEACH_Z
        else:  # z >= L - 1.5*BEACH_X
            return (10.0/9.0) * (sqr(x - (L-1.5*BEACH_X)) + sqr(z - (L-1.5*BEACH_X))) - BEACH_Z


# Генерация твердого тела (корыто + стенки)
def generate_solid_bathymetry_3d(path,
                                 width=160,  # x (ширина)
                                 height=100,  # y (высота)
                                 depth=80,  # z (глубина)
                                 wall_thickness=4,
                                 floor_thickness=2):
    """
    Генерирует 3D твердое тело с корытообразным дном
    Оси: x (ширина), y (высота), z (глубина)
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    max_height = 0.5  # Максимальная высота области

    with open(path, 'w') as f:
        f.write(f"S {width} {height} {depth}\n")
        # Чтение в основном коде: k от depth-1 до 0, j от height-1 до 0, i от width-1 до 0
        # Поэтому записываем в обратном порядке
        for k in range(depth - 1, -1, -1):  # z (глубина)
            for j in range(height - 1, -1, -1):  # y (высота)
                for i in range(width - 1, -1, -1):  # x (ширина)
                    # Физические координаты
                    x_phys = L * i / (width - 1)
                    z_phys = L * k / (depth - 1)
                    y_phys = max_height * j / (height - 1)

                    # Высота дна в этой точке (смещаем так, чтобы min=0)
                    bottom_y = bathymetry(x_phys, z_phys) + BEACH_Z

                    # Проверка на стенки
                    in_wall = (i < wall_thickness or i >= width - wall_thickness or
                               k < wall_thickness or k >= depth - wall_thickness)

                    # Проверка на дно (все, что ниже или на уровне дна)
                    in_bottom = y_phys <= bottom_y

                    is_solid = in_wall or in_bottom
                    phi = -1.0 if is_solid else 1.0
                    f.write(f"{phi:.6f} ")
                f.write("\n")


# Генерация жидкости в корыте
# Генерация жидкости с гауссианом (нормальное распределение)
def generate_fluid_gaussian_3d(path,
                               width=160,
                               height=100,
                               depth=80,
                               wall_thickness=4,
                               base_level=0.2,  # Базовый уровень воды
                               amplitude=0.1,  # Амплитуда гауссиана
                               center_x=0.5,  # Центр гауссиана по X (0.0-1.0)
                               center_z=0.5,  # Центр гауссиана по Z (0.0-1.0)
                               sigma=0.1):  # Стандартное отклонение
    """
    Генерирует 3D жидкость с гауссианом (нормальным распределением)
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    max_height = 0.5

    with open(path, 'w') as f:
        f.write(f"F {width} {height} {depth}\n")
        # Запись в обратном порядке
        for k in range(depth - 1, -1, -1):  # z (глубина)
            for j in range(height - 1, -1, -1):  # y (высота)
                for i in range(width - 1, -1, -1):  # x (ширина)
                    # Физические координаты
                    x_phys = L * i / (width - 1)
                    z_phys = L * k / (depth - 1)
                    y_phys = max_height * j / (height - 1)

                    # Высота дна в этой точке (смещаем так, чтобы min=0)
                    bottom_y = bathymetry(x_phys, z_phys) + BEACH_Z

                    # Проверка на стенки
                    in_wall = (i < wall_thickness or i >= width - wall_thickness or
                               k < wall_thickness or k >= depth - wall_thickness)

                    # Вычисление гауссиана
                    dx = (x_phys - center_x * L)
                    dz = (z_phys - center_z * L)
                    gaussian = amplitude * math.exp(-(dx * dx + dz * dz) / (2 * sigma * sigma))

                    # Локальный уровень воды
                    water_level = base_level + gaussian

                    # Проверка на жидкость (над дном и под уровнем воды)
                    above_bottom = y_phys > bottom_y
                    below_water = y_phys <= water_level

                    is_fluid = not in_wall and above_bottom and below_water
                    phi = -1.0 if is_fluid else 1.0
                    f.write(f"{phi:.6f} ")
                f.write("\n")


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


# Генерация теста с корытом
# Генерация теста с гауссианом
def generate_gaussian_test(width=160, height=100, depth=80,
                           base_level=0.2, amplitude=0.1,
                           center_x=0.5, center_z=0.5, sigma=0.15):
    """
    Генерирует тест с гауссиановым распределением воды
    """
    # Создаем директории
    os.makedirs('res', exist_ok=True)

    # Генерация solid
    generate_solid_bathymetry_3d('res/solid_bathymetry.txt', width, height, depth)

    # Генерация fluid с гауссианом
    generate_fluid_gaussian_3d('res/fluid_gaussian.txt', width, height, depth,
                               base_level=base_level, amplitude=amplitude,
                               center_x=center_x, center_z=center_z, sigma=sigma)

    # Комбинированные метки
    generate_combined_labels_3d('res/solid_bathymetry.txt',
                                'res/fluid_gaussian.txt',
                                'res/labels_gaussian.txt')

# Пример генерации тестов
def generate_3d_tests():
    w, h, d = 35, 35, 35

    # Тест с гауссианом в центре
    generate_gaussian_test(
        width=75,
        height=75,
        depth=25,
        base_level=0.02,
        amplitude=0.19,
        center_x=0.5,
        center_z=0.5,
        sigma=0.15
    )
    # Визуализируем предварительную геометрию
    visualize_bathymetry(
        width=75,
        depth=25,
        base_level=0.04,
        amplitude=0.11,
        center_x=0.5,
        center_z=0.5,
        sigma=0.15,
        # save_path='res/bathymetry_visualization.png'
    )
    # # Тест с гауссианом смещенным к краю
    # generate_gaussian_test(
    #     width=160,
    #     height=100,
    #     depth=80,
    #     base_level=0.15,
    #     amplitude=0.2,
    #     center_x=0.3,
    #     center_z=0.7,
    #     sigma=0.12
    # )
    #
    # # Тест с широким гауссианом
    # generate_gaussian_test(
    #     width=160,
    #     height=100,
    #     depth=80,
    #     base_level=0.1,
    #     amplitude=0.25,
    #     center_x=0.5,
    #     center_z=0.5,
    #     sigma=0.25
    # )

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


# Визуализация батиметрии и поверхности воды

# Визуализация с осью Y, направленной вверх
def visualize_bathymetry(width=160, depth=80, base_level=0.2, amplitude=0.1,
                         center_x=0.5, center_z=0.5, sigma=0.15, save_path=None):
    """
    Визуализирует 3D-поверхности с осью Y, направленной вверх
    """
    # Создаем сетку координат
    x = np.linspace(0, L, width)
    z = np.linspace(0, L, depth)
    X, Z = np.meshgrid(x, z)

    # Рассчитываем высоту дна и уровень воды
    Bottom = np.zeros_like(X)
    for i in range(width):
        for j in range(depth):
            Bottom[j, i] = bathymetry(x[i], z[j]) + BEACH_Z

    dx = X - center_x * L
    dz = Z - center_z * L
    Gaussian = amplitude * np.exp(-(dx ** 2 + dz ** 2) / (2 * sigma ** 2))
    Water = base_level + Gaussian

    # Создаем 3D-график с правильной ориентацией осей
    fig = plt.figure(figsize=(14, 10))

    # 1. 3D-визуализация с осью Y вверх
    ax1 = fig.add_subplot(121, projection='3d')

    # Поверхность дна (переворачиваем Z для правильной ориентации)
    surf_bottom = ax1.plot_surface(X, Z, Bottom, cmap='terrain',
                                   alpha=0.8, antialiased=True)

    # Поверхность воды
    surf_water = ax1.plot_surface(X, Z, Water, color='blue',
                                  alpha=0.3, label='Water surface')

    # Настройки осей и вида
    ax1.set_xlabel('X')
    ax1.set_ylabel('Z')
    ax1.set_zlabel('Y (Height)', labelpad=15)
    ax1.set_title('3D Bathymetry and Water Surface\n(Y-axis points up)')
    ax1.view_init(elev=30, azim=-45)  # Угол обзора
    ax1.zaxis.set_rotate_label(False)  # Фиксируем метку оси Z
    # ax1.invert_zaxis()  # Инвертируем ось Z (Y), чтобы направление было вверх

    # 2. 2D-вид сверху с правильной ориентацией
    ax2 = fig.add_subplot(122)

    # Визуализация батиметрии с освещением
    ls = LightSource(azdeg=315, altdeg=45)
    rgb = ls.shade(Bottom, cmap=plt.cm.terrain, vert_exag=0.1, blend_mode='soft')

    # Отображаем батиметрию (инвертируем ось Y)
    extent = [0, L, 0, L]  # [xmin, xmax, ymin, ymax] - инвертируем Y
    im = ax2.imshow(Bottom, cmap='terrain', extent=extent,
                    origin='upper', alpha=0.8)  # origin='upper' для правильной ориентации

    # Контуры уровня воды (инвертируем ось Y)
    levels = np.linspace(Water.min(), Water.max(), 10)
    cs = ax2.contour(X, Z, Water, levels=levels, colors='blue', linewidths=1.5)

    # Настройки графика
    ax2.set_xlabel('X')
    ax2.set_ylabel('Z')
    ax2.set_title('2D Bathymetry Map with Water Contours\n(Y-axis points up)')
    plt.colorbar(im, ax=ax2, label='Bottom Height')
    plt.clabel(cs, inline=True, fontsize=9, fmt='%1.2f')

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300)
        print(f"Визуализация сохранена в {save_path}")
    else:
        plt.show()


generate_3d_tests()