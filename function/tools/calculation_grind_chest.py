#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filename: calculation_grind_chest.py
Author: StareAbyss
Creation Date：2024-04-26
Last Date：2024-04-26

Description：
线性规划 以计算美食大战老鼠肝帝宝箱的最优方案 (暂不含掉落权重)
"""

import pulp

# 定义问题
problem = pulp.LpProblem("Material_Collection", pulp.LpMinimize)

# 定义决策变量，即每个关卡的次数，这些变量必须是整数
stage_A = pulp.LpVariable("NO-1-7", lowBound=0, cat='Integer')
stage_B = pulp.LpVariable("NO-1-14", lowBound=0, cat='Integer')
stage_C = pulp.LpVariable("NO-2-5", lowBound=0, cat='Integer')
stage_D = pulp.LpVariable("NO-2-10", lowBound=0, cat='Integer')
stage_E = pulp.LpVariable("NO-2-15", lowBound=0, cat='Integer')
stage_F = pulp.LpVariable("NO-4-5", lowBound=0, cat='Integer')
stage_G = pulp.LpVariable("NO-4-10", lowBound=0, cat='Integer')
stages_list = [stage_A, stage_B, stage_C, stage_D, stage_E, stage_F, stage_G]

# 目标函数：最小化总次数
problem += stage_A + stage_B + stage_C + stage_D + stage_E + stage_F + stage_G

# 约束条件：收集到足够的材料
problem += stage_A * 87 / 90 + stage_E * 85 / 90 >= 60  # 材料a
problem += stage_B + stage_D >= 35  # 材料b
problem += stage_B + stage_E + stage_G * 0.01 >= 123  # 材料c
problem += stage_C + stage_G * 0.01 >= 70  # 材料d
problem += stage_C + stage_F >= 70  # 材料e
problem += stage_A + stage_D + stage_F >= 123  # 材料f

# 解决问题
problem.solve()
# 输出结果
sum_count = 0
for stage in stages_list:
    print(f"关卡 {stage.name} 需要打:{stage.varValue}次")
    sum_count += stage.varValue
print(f"合计: {sum_count}次")
