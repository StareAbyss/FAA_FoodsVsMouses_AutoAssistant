import time
from multiprocessing import Process, Queue

import cv2

from function.common.bg_img_screenshot import capture_image_png_all
from function.core_battle.coordinate_map import parse_positions
from function.globals.log import CUS_LOGGER
from function.yolo import onnxdetect


# 生产者函数
def producer(time_num, handle, read_queue, is_log, is_gpu):
    try:
        while True:
            # 获取图像并进行目标检测
            result = onnxdetect.get_mouse_position(
                capture_image_png_all(handle),
                is_log,
                is_gpu
            )

            # 检查结果是否有效
            if result is not None:
                information = parse_positions(*result)  # 加工信息
                # 将检测结果放入队列
                read_queue.put(information)
                wave, godwind, positions = information
                # 遍历所有检测到的目标
                CUS_LOGGER.debug(f"待加工信息为{result} ")
                CUS_LOGGER.debug(f"识图信息为是否检测到波次 {wave} 是否检测到波神风 {godwind},剩下待炸点位 {positions} ")

            # 暂停一段时间
            time.sleep(time_num)
    except cv2.error or AttributeError:
        CUS_LOGGER.critical("出现严重错误，请把当前FAA文件目录迁移至非中文路径下，否则程序不会正常运行！")


def read_and_get_return_information(faa, is_log, is_gpu, interval):
    # 创建并启动生产者进程
    read_queue = Queue()
    CUS_LOGGER.debug("开始多进程识别特殊老鼠及波次信息")

    p = Process(target=producer, args=(interval, faa.handle, read_queue, is_log, is_gpu))
    p.start()

    return p, read_queue


def kill_process(process):
    process.terminate()
    process.join()
