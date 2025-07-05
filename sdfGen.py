import numpy as np
from mesh_to_sdf import mesh_to_voxels
import trimesh


def save_sdf_to_file(mesh, filename, resolution=64, padding=True):
    # Генерация SDF вокселей
    voxels = mesh_to_voxels(mesh, resolution, pad=padding)

    # Вычисление параметров сетки
    bounds = mesh.bounds
    min_bounds, max_bounds = bounds[0], bounds[1]

    # Рассчет размера вокселя
    bbox_size = max_bounds - min_bounds
    max_bbox_size = np.max(bbox_size)
    voxel_size = max_bbox_size / (resolution - 2)  # Учет padding

    # Рассчет origin с учетом padding
    padding_size = voxel_size if padding else 0.0
    origin = min_bounds - padding_size

    # Сохранение в файл
    with open(filename, 'w') as f:
        # Запись размеров сетки
        f.write(f"{resolution} {resolution} {resolution}\n")

        # Запись origin
        f.write(f"{origin[0]} {origin[1]} {origin[2]}\n")

        # Запись размера ячейки
        f.write(f"{voxel_size}\n")

        # Запись значений в правильном порядке (x, y, z)
        for k in range(resolution):
            for j in range(resolution):
                for i in range(resolution):
                    f.write(f"{voxels[i, j, k]} ")
                f.write("\n")
            f.write("\n")



    # Загрузка меша
mesh = trimesh.load('ball.obj')

    # Сохранение SDF в файл
save_sdf_to_file(mesh, 'ball.sdf', resolution=64, padding=True)
print("SDF saved to ball.sdf")