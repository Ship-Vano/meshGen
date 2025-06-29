import glob
import sys
import re
import cv2
import numpy as np


def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]


def create_mp4_from_png(input_pattern, output_file, fps=30):
    # Получаем и сортируем файлы
    filepaths = sorted(glob.glob(input_pattern), key=natural_sort_key)
    if not filepaths:
        raise ValueError("No images found!")

    total_frames = len(filepaths)

    # Обрабатываем первый кадр для определения параметров видео
    first_frame = cv2.imread(filepaths[0])
    if first_frame is None:
        raise IOError(f"Failed to read first frame: {filepaths[0]}")

    height, width, _ = first_frame.shape
    size = (width, height)

    # Пытаемся использовать лучшие кодеки (H.264/AVC1 для совместимости с PowerPoint)
    for codec in ['avc1', 'h264', 'mp4v']:
        fourcc = cv2.VideoWriter_fourcc(*codec)
        video = cv2.VideoWriter(output_file, fourcc, fps, size)
        if video.isOpened():
            break
    else:
        raise RuntimeError("Failed to create video writer with supported codec")

    # Записываем первый кадр
    video.write(first_frame)
    sys.stdout.write(f"\rProgress: {1 / total_frames * 100:.1f}%")
    sys.stdout.flush()

    # Обрабатываем остальные кадры
    for i, fp in enumerate(filepaths[1:]):
        frame = cv2.imread(fp)
        if frame is not None:
            video.write(frame)

        # Обновляем прогресс
        progress = (i + 2) / total_frames * 100
        sys.stdout.write(f"\rProgress: {progress:.1f}%")
        sys.stdout.flush()

    video.release()
    sys.stdout.write("\n")
    print(f"MP4 video created successfully: {output_file}")



input_pattern = "/home/ivan/Pictures/New Folder/test1v2/test1v2.0*.png"
output_file = "test1v2_video.mp4"
fps = 30  # Частота кадров для плавной анимации
create_mp4_from_png(input_pattern, output_file, fps)