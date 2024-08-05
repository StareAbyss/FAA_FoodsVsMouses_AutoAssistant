import time
import cv2

from function.globals.init_resources import RESOURCE_P
from function.scattered.match_ocr_text.match_text import match
from function.globals.thread_action_queue import T_ACTION_QUEUE_TIMER
from function.common.bg_img_screenshot import capture_image_png
from function.common.bg_img_match import match_p_in_w


def food_match_ocr_text(self):
    handle = self.handle

    quest_imgs = []

    my_dict = {0: 362, 1: 405, 2: 448, 3: 491, 4: 534, 5: 570}

    for i in range(6):

        # 先移动一次位置
        T_ACTION_QUEUE_TIMER.add_click_to_queue(handle=handle, x=536, y=my_dict[i])
        time.sleep(0.2)

        Y = 358

        # while True:
        # 使用掩模匹配图片
        for j in range(3):
            find = match_p_in_w(
                source_handle=self.handle,
                source_root_handle=self.handle_360,
                source_range=[82, Y + 55 * j, 533, 459 + 53 * j],
                template=RESOURCE_P["ocr"]["美食大赛任务.png"],
                mask=RESOURCE_P["ocr"]["美食大赛任务_掩模.png"],
                match_tolerance=0.999,
                # test_print=True,
                # test_show=True,
                return_center=False
            )

            if find:
                # 获取source_range的左上角坐标
                left_top_x, left_top_y = 82, Y + 55 * j

                quest_img = capture_image_png(
                    handle=self.handle,
                    root_handle=self.handle_360,
                    raw_range=[find[0] + left_top_x, find[1] + left_top_y,
                               find[0] + 445 + left_top_x, find[1] + 55 + left_top_y]
                )
                # 确保图像为BGR格式，OpenCV默认使用BGR

                if quest_img.shape[2] == 4:  # 检查是否有Alpha通道
                    # 将RGBA转换为BGR
                    quest_img_bgr = cv2.cvtColor(quest_img, cv2.COLOR_RGBA2BGR)
                else:
                    quest_img_bgr = quest_img[:, :, ::-1]  # RGB转BGR

                # 显示图像
                # 测试看截图是否正确
                # cv2.imshow('Quest Image', quest_img_bgr)
                # cv2.waitKey(0)  # 等待按键
                # cv2.destroyAllWindows()

                quest_imgs.append(quest_img_bgr)

            if i == 2:
                break

    return quest_imgs


def extract_text_from_images(images):
    """

    """
    seen = set()  # 用于记录已见过的元素
    unique_results = []  # 存储去重后的结果

    for source in images:
        text_result = match(source=source)
        # 只有当text_result不在seen集合中时才添加到unique_results和seen中
        if text_result not in seen:
            unique_results.append(text_result)
            seen.add(text_result)

    for result in unique_results:
        print(result)

    return unique_results
