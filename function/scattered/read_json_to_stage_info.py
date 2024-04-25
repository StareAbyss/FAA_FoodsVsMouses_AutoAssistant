import json

from function.globals.get_paths import PATHS
from function.globals.log import CUS_LOGGER


def read_json_to_stage_info(stage_id):
    """读取文件中是否存在预设"""
    with open(PATHS["config"] + "//stage_info.json", "r", encoding="UTF-8") as file:
        stages_info = json.load(file)
    with open(PATHS["config"] + "//stage_info_extra.json", "r", encoding="UTF-8") as file:
        stages_info_extra = json.load(file)

    # 初始化
    stage_info = stages_info["default"]
    stage_info["id"] = stage_id

    # 拆分关卡名称
    stage_0, stage_1, stage_2 = stage_id.split("-")  # type map stage

    # 如果找到预设
    for information in [stages_info, stages_info_extra]:
        try_stage_info = information.get(stage_0, {}).get(stage_1, {}).get(stage_2, None)
        print(try_stage_info)
        if try_stage_info:
            stage_info = {**stage_info, **try_stage_info}
            break

    CUS_LOGGER.info("读取关卡信息: {}".format(stage_info))
    return stage_info


if __name__ == '__main__':
    read_json_to_stage_info(stage_id="OR-0-2")
