import json
import os
import time

import cv2
import numpy as np

from function.globals.extra import EXTRA_GLOBALS
from function.globals.get_paths import PATHS


def im_read(img_path):
    return cv2.imdecode(buf=np.fromfile(file=img_path, dtype=np.uint8), flags=-1)


"""RESOURCE_P 常规图片资源 静态资源 可以直接调用"""

RESOURCE_P = {}


def add_to_resource_img(relative_path, img):
    global RESOURCE_P
    current_level = RESOURCE_P

    path_parts = relative_path.split(os.sep)

    for part in path_parts[:-1]:
        if part not in current_level:
            current_level[part] = {}
        current_level = current_level[part]
    current_level[path_parts[-1]] = img


def fresh_resource_img():
    # 清空
    global RESOURCE_P
    RESOURCE_P = {}

    # 遍历文件夹结构，读取所有名称后缀为.png的文件，加入到字典中
    root_dir = PATHS["root"] + "\\resource\\picture"

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".png"):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, root_dir)
                img = im_read(file_path)
                add_to_resource_img(relative_path, img)


"""RESOURCE_CP 用户自定义图片资源"""

RESOURCE_CP = {}


def add_to_resource_cus_img(relative_path, img):
    global RESOURCE_CP
    current_level = RESOURCE_CP

    path_parts = relative_path.split(os.sep)

    for part in path_parts[:-1]:
        if part not in current_level:
            current_level[part] = {}
        current_level = current_level[part]
    current_level[path_parts[-1]] = img


def fresh_resource_cus_img():
    # 清空
    global RESOURCE_CP
    RESOURCE_CP = {}

    # 遍历文件夹结构，读取所有名称后缀为.png的文件，加入到字典中
    root_dir = PATHS["config"] + "\\cus_images"

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".png"):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, root_dir)
                img = im_read(file_path)
                add_to_resource_cus_img(relative_path, img)


"""RESOURCE_LOG_IMG 日志图片资源 由于会出现变动, 请务import .py而非单独的全局变量"""

RESOURCE_LOG_IMG = {}


def add_to_resource_log_img(relative_path, img):
    global RESOURCE_LOG_IMG
    current_level = RESOURCE_LOG_IMG

    path_parts = relative_path.split(os.sep)

    for part in path_parts[:-1]:
        if part not in current_level:
            current_level[part] = {}
        current_level = current_level[part]
    current_level[path_parts[-1]] = img


def fresh_resource_log_img():
    # 清空
    global RESOURCE_LOG_IMG
    RESOURCE_LOG_IMG = {}

    # 遍历文件夹结构，读取所有名称后缀为.png的文件，加入到字典中
    root_dir = PATHS["logs"] + "\\match_failed"

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".png"):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, root_dir)
                img = im_read(file_path)
                add_to_resource_log_img(relative_path, img)


"""RESOURCE_B 战斗方案资源 由于会出现变动, 请务import .py而非单独的全局变量"""

RESOURCE_B = {}


def fresh_resource_b():
    # 清空
    global RESOURCE_B
    RESOURCE_B = {}

    for b_uuid, b_path in EXTRA_GLOBALS.battle_plan_uuid_to_path.items():

        # 自旋锁读写, 防止多线程读写问题
        while EXTRA_GLOBALS.file_is_reading_or_writing:
            time.sleep(0.1)
        EXTRA_GLOBALS.file_is_reading_or_writing = True  # 文件被访问

        with open(file=b_path, mode='r', encoding='utf-8') as file:
            json_data = json.load(file)

        EXTRA_GLOBALS.file_is_reading_or_writing = False  # 文件已解锁

        RESOURCE_B[b_uuid] = json_data


fresh_resource_img()
fresh_resource_cus_img()
fresh_resource_log_img()

if __name__ == '__main__':
    pass
