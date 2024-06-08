import cProfile

from function.common.bg_img_match import match_ps_in_w
from function.globals.get_paths import PATHS
from function.scattered.gat_handle import faa_get_handle


def f_test():
    handle = faa_get_handle(channel="深渊之下 | 锑食", mode="flash")

    for i in range(100):
        match_ps_in_w(
            source_handle=handle,
            template_opts=[
                {
                    "source_range": [792, 200, 942, 534],
                    "template": PATHS["picture"]["common"] + "\\底部菜单\\跳转_竞技场.png",
                    "match_tolerance": 0.95,
                },
                {
                    "source_range": [792, 200, 942, 534],
                    "template": PATHS["picture"]["common"] + "\\底部菜单\\跳转_情侣任务.png",
                    "match_tolerance": 0.95,
                },
                {
                    "source_range": [792, 200, 942, 534],
                    "template": PATHS["picture"]["common"] + "\\底部菜单\\跳转_公会副本.png",
                    "match_tolerance": 0.95,
                }
            ],
            return_mode="or"
        )


cProfile.run("f_test()")

"""
从原始图像[950- x 600-] x 找目标图像[113 x 45] x 3图 x 1000次

一次裁剪X 二次裁剪X 103.2s
一次裁剪√ 二次裁剪X 103.2s
一次裁剪X 二次裁剪√ 11.4s
一次裁剪√ 二次裁剪√ 11.4s

结论1 速度只取决于最终需要比对的数量
结论2 范围过大超出截获区域的部分, 不会影响性能(切片操作可以超出索引)
"""
