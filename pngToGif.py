# import glob
# import contextlib
# from PIL import Image
#
# # filepaths
# fp_in = "/home/ivan/MHDresults/diplomTests/task9_100/task9anim.0*.png"
# fp_out = "vortex.gif"
#
# # use exit stack to automatically close opened images
# with contextlib.ExitStack() as stack:
#
#     # lazily load images
#     imgs = (stack.enter_context(Image.open(f))
#             for f in sorted(glob.glob(fp_in)))
#
#     # extract  first image from iterator
#     img = next(imgs)
#
#     # https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif
#     img.save(fp=fp_out, format='GIF', append_images=imgs,
#              save_all=True, duration=200, loop=0)

# 2nd ver
# import glob
# from PIL import Image
#
# # Пути к файлам
# fp_in = "/home/ivan/MHDresults/diplomTests/task9_100/task9anim.0*.png"
# fp_out = "vortex.gif"
#
# # Получаем отсортированный список файлов
# filepaths = sorted(glob.glob(fp_in))
#
# if not filepaths:
#     raise ValueError("Не найдено изображений для обработки")
#
# # Обрабатываем первое изображение отдельно
# with Image.open(filepaths[0]) as first_img:
#     # Конвертируем в палитру для экономии памяти
#     first_img_p = first_img.convert('P')
#
#
#     # Генератор для последующих изображений
#     def generate_frames():
#         for fp in filepaths[1:]:
#             with Image.open(fp) as img:
#                 # Конвертируем и отдаем кадр
#                 yield img.convert('P')
#
#
#     # Сохраняем анимированный GIF
#     first_img_p.save(
#         fp=fp_out,
#         format='GIF',
#         save_all=True,
#         append_images=generate_frames(),
#         duration=200,
#         loop=0,
#         optimize=True
#     )

# 3rd ver
import glob
import sys
from PIL import Image

fp_in = "/home/ivan/CLionProjects/FLuidGPU/InputData/testFluidSphere.0*.png"
fp_out = "anim.gif"

filepaths = sorted(glob.glob(fp_in))
if not filepaths:
    raise ValueError("No images found!")

total_frames = len(filepaths)

# Обработка первого кадра
with Image.open(filepaths[0]) as first_img:
    first_img_p = first_img.convert('P')

    # Выводим прогресс первого кадра
    sys.stdout.write(f"\rProgress: {1 / total_frames * 100:.1f}%")
    sys.stdout.flush()


    # Генератор для последующих кадров
    def generate_frames():
        for i, fp in enumerate(filepaths[1:]):
            with Image.open(fp) as img:
                yield img.convert('P')

            # Обновляем прогресс
            progress = (i + 2) / total_frames * 100  # +2: 1-й кадл уже обработан + текущий
            sys.stdout.write(f"\rProgress: {progress:.1f}%")
            sys.stdout.flush()

        sys.stdout.write("\n")  # Переводим строку после завершения


    # Сохраняем анимацию
    first_img_p.save(
        fp=fp_out,
        format='GIF',
        save_all=True,
        append_images=generate_frames(),
        duration=200,
        loop=0,
        optimize=True
    )

print("GIF создан успешно!")